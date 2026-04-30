"""Config flow for Zendure Local."""
from __future__ import annotations

import logging
import re
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import API_REPORT_PATH, CONF_SERIAL_NUMBER, DOMAIN, HTTP_TIMEOUT

_LOGGER = logging.getLogger(__name__)

_IPv4_RE = re.compile(
    r"^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$"
)


def _valid_ip(host: str) -> bool:
    return bool(_IPv4_RE.match(host.strip()))


async def _probe_device(hass, host: str) -> str:
    """Return the device serial number, or raise on failure."""
    session = async_get_clientsession(hass)
    url = f"http://{host.strip()}{API_REPORT_PATH}"
    async with session.get(
        url, timeout=aiohttp.ClientTimeout(total=HTTP_TIMEOUT)
    ) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    props = data.get("properties", data)
    sn = (
        props.get("sn")
        or props.get("deviceSn")
        or props.get("snNumber")
        or data.get("sn")
        or "unknown"
    )
    return str(sn)


class ZendureConfigFlow(ConfigFlow, domain=DOMAIN):
    """Two-step config flow: IP input → confirmation with serial number."""

    VERSION = 1

    def __init__(self) -> None:
        self._host: str = ""
        self._serial_number: str = ""

    # ------------------------------------------------------------------
    # Step 1 — user enters IP address
    # ------------------------------------------------------------------

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            if not _valid_ip(host):
                errors[CONF_HOST] = "invalid_host"
            else:
                try:
                    sn = await _probe_device(self.hass, host)
                    self._host = host
                    self._serial_number = sn
                    await self.async_set_unique_id(sn)
                    self._abort_if_unique_id_configured()
                    return await self.async_step_confirm()
                except aiohttp.ClientError:
                    errors["base"] = "cannot_connect"
                except Exception:
                    _LOGGER.exception("Unexpected error during Zendure connection test")
                    errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_HOST): str}),
            errors=errors,
        )

    # ------------------------------------------------------------------
    # Step 2 — display discovered serial number, user confirms
    # ------------------------------------------------------------------

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(
                title=f"SolarFlow 800 Pro2 ({self._serial_number})",
                data={
                    CONF_HOST: self._host,
                    CONF_SERIAL_NUMBER: self._serial_number,
                },
            )

        return self.async_show_form(
            step_id="confirm",
            description_placeholders={"serial_number": self._serial_number},
        )

    # ------------------------------------------------------------------
    # Reconfigure — let the user change the IP after initial setup
    # ------------------------------------------------------------------

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        entry: ConfigEntry = self._get_reconfigure_entry()

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            if not _valid_ip(host):
                errors[CONF_HOST] = "invalid_host"
            else:
                try:
                    await _probe_device(self.hass, host)
                    return self.async_update_reload_and_abort(
                        entry,
                        data_updates={CONF_HOST: host},
                    )
                except aiohttp.ClientError:
                    errors["base"] = "cannot_connect"
                except Exception:
                    _LOGGER.exception("Unexpected error during Zendure reconfigure")
                    errors["base"] = "unknown"

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {vol.Required(CONF_HOST, default=entry.data[CONF_HOST]): str}
            ),
            errors=errors,
        )
