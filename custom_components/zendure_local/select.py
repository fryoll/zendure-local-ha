"""Select platform for Zendure Local (AC mode control)."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import AC_MODE_FROM_VALUE, AC_MODE_TO_VALUE
from .coordinator import ZendureCoordinator
from .entity import ZendureBaseEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Register the AC mode select entity for this config entry."""
    coordinator: ZendureCoordinator = entry.runtime_data
    async_add_entities([ZendureAcModeSelect(coordinator)])


class ZendureAcModeSelect(ZendureBaseEntity, SelectEntity):
    """Selects the AC operating mode of the device.

    Options use internal English keys (auto / grid_charge / injection);
    display names are resolved from translations/XX.json.
    """

    _attr_translation_key = "ac_mode"
    _attr_options = list(AC_MODE_TO_VALUE)

    def __init__(self, coordinator: ZendureCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.serial_number}_ac_mode"

    @property
    def current_option(self) -> str | None:
        data = self.coordinator.data
        if not data:
            return None
        raw = data.get("acMode")
        if raw is None:
            return None
        return AC_MODE_FROM_VALUE.get(int(raw))

    async def async_select_option(self, option: str) -> None:
        """Write the chosen mode to the device and refresh."""
        value = AC_MODE_TO_VALUE.get(option)
        if value is None:
            _LOGGER.error("Unknown AC mode option: %s", option)
            return
        await self.coordinator.async_write_property("acMode", value)
        await self.coordinator.async_request_refresh()
