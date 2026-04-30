"""Data update coordinator for the Zendure Local integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_REPORT_PATH,
    API_WRITE_PATH,
    CONF_SERIAL_NUMBER,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    HTTP_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


class ZendureCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator that polls the Zendure device every 30 seconds."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
            config_entry=entry,
        )
        self.host: str = entry.data[CONF_HOST]
        self.serial_number: str = entry.data[CONF_SERIAL_NUMBER]

    async def _async_update_data(self) -> dict:
        """Fetch and normalize device properties."""
        session = async_get_clientsession(self.hass)
        url = f"http://{self.host}{API_REPORT_PATH}"
        try:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=HTTP_TIMEOUT),
            ) as response:
                response.raise_for_status()
                raw = await response.json(content_type=None)
        except aiohttp.ClientError as err:
            raise UpdateFailed(
                f"Cannot reach Zendure device at {self.host}: {err}"
            ) from err
        except Exception as err:
            raise UpdateFailed(
                f"Unexpected error reading Zendure device at {self.host}: {err}"
            ) from err

        return _normalize_data(raw)

    async def async_write_property(self, key: str, value: int | float) -> None:
        """POST a single property update to the device.

        The device may acknowledge a write before the new value is visible on
        /properties/report, so we wait briefly to avoid an immediate stale refresh.
        """
        session = async_get_clientsession(self.hass)
        url = f"http://{self.host}{API_WRITE_PATH}"
        payload = {
            "sn": self.serial_number,
            "properties": {key: value},
        }
        try:
            async with session.post(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=HTTP_TIMEOUT),
            ) as response:
                response.raise_for_status()
            await asyncio.sleep(1)
        except aiohttp.ClientError as err:
            _LOGGER.error(
                "Failed to write %s=%s to Zendure device at %s (sn=%s): %s",
                key,
                value,
                self.host,
                self.serial_number,
                err,
            )
            raise


def _normalize_data(raw: dict) -> dict:
    """Flatten the raw API payload into a simple key/value dict."""
    properties: dict = raw.get("properties", raw)
    data: dict = {k: v for k, v in properties.items() if k != "packData"}

    # Flatten per-pack battery data (Pro2 supports up to 2 packs)
    for i, pack in enumerate(properties.get("packData", [])[:2]):
        soc = pack.get("socLevel")
        if soc is not None:
            data[f"pack{i}_soc"] = soc

    # Normalise main SOC key — device may report electricLevel or socLevel
    if "electricLevel" not in data and "socLevel" in data:
        data["electricLevel"] = data["socLevel"]

    return data
