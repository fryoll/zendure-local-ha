"""Switch platform for Zendure Local (injection enable/disable)."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEFAULT_OUTPUT_LIMIT
from .coordinator import ZendureCoordinator
from .entity import ZendureBaseEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Register the injection switch for this config entry."""
    coordinator: ZendureCoordinator = entry.runtime_data
    async_add_entities([ZendureInjectionSwitch(coordinator)])


class ZendureInjectionSwitch(ZendureBaseEntity, SwitchEntity):
    """Toggle power injection by setting outputLimit to 0 (OFF) or its last value (ON).

    The remembered limit defaults to DEFAULT_OUTPUT_LIMIT (800 W) if the device
    has never reported a non-zero value in the current HA session.
    """

    _attr_translation_key = "injection_enabled"

    def __init__(self, coordinator: ZendureCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.serial_number}_injection_enabled"
        self._last_nonzero_limit: int = DEFAULT_OUTPUT_LIMIT

    async def async_added_to_hass(self) -> None:
        """Seed the remembered limit from the first coordinator payload."""
        await super().async_added_to_hass()
        if self.coordinator.data:
            limit = self.coordinator.data.get("outputLimit", 0)
            if limit and int(limit) > 0:
                self._last_nonzero_limit = int(limit)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Track the last non-zero outputLimit so we can restore it on turn-on."""
        if self.coordinator.data:
            limit = self.coordinator.data.get("outputLimit", 0)
            if limit and int(limit) > 0:
                self._last_nonzero_limit = int(limit)
        self.async_write_ha_state()

    @property
    def is_on(self) -> bool | None:
        data = self.coordinator.data
        if not data:
            return None
        limit = data.get("outputLimit")
        return int(limit) > 0 if limit is not None else None

    async def async_turn_on(self, **kwargs) -> None:
        """Restore the last known non-zero outputLimit."""
        await self.coordinator.async_write_property(
            "outputLimit", self._last_nonzero_limit
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Set outputLimit to 0 to stop injection."""
        await self.coordinator.async_write_property("outputLimit", 0)
        await self.coordinator.async_request_refresh()
