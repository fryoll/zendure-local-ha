"""Number platform for Zendure Local."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import ZendureCoordinator
from .entity import ZendureBaseEntity
from .utils import detect_percent_scale

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class ZendureNumberDescription(NumberEntityDescription):
    """Extends NumberEntityDescription with device property keys."""

    value_key: str = ""
    write_key: str = ""
    device_scale: int = 1


NUMBER_DESCRIPTIONS: tuple[ZendureNumberDescription, ...] = (
    ZendureNumberDescription(
        key="output_limit",
        translation_key="output_limit",
        value_key="outputLimit",
        write_key="outputLimit",
        native_min_value=0,
        native_max_value=800,
        native_step=10,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=NumberDeviceClass.POWER,
        mode=NumberMode.SLIDER,
    ),
    ZendureNumberDescription(
        key="input_limit",
        translation_key="input_limit",
        value_key="inputLimit",
        write_key="inputLimit",
        native_min_value=0,
        native_max_value=800,
        native_step=10,
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=NumberDeviceClass.POWER,
        mode=NumberMode.SLIDER,
    ),
    ZendureNumberDescription(
        key="min_soc",
        translation_key="min_soc",
        value_key="minSoc",
        write_key="minSoc",
        native_min_value=0,
        native_max_value=100,
        native_step=5,
        native_unit_of_measurement=PERCENTAGE,
        device_class=NumberDeviceClass.BATTERY,
        mode=NumberMode.BOX,
        device_scale=10,
    ),
    ZendureNumberDescription(
        key="soc_set",
        translation_key="soc_set",
        value_key="socSet",
        write_key="socSet",
        native_min_value=0,
        native_max_value=100,
        native_step=5,
        native_unit_of_measurement=PERCENTAGE,
        device_class=NumberDeviceClass.BATTERY,
        mode=NumberMode.BOX,
        device_scale=10,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Register number entities for this config entry."""
    coordinator: ZendureCoordinator = entry.runtime_data
    async_add_entities(ZendureNumber(coordinator, desc) for desc in NUMBER_DESCRIPTIONS)


class ZendureNumber(ZendureBaseEntity, NumberEntity):
    """Read/write number control for a Zendure device property."""

    entity_description: ZendureNumberDescription

    def __init__(
        self,
        coordinator: ZendureCoordinator,
        description: ZendureNumberDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.serial_number}_{description.key}"

    def _uses_scaled_percent_values(self) -> bool:
        """Return True when the device reports percent values multiplied by 10."""
        return self._percent_scale() > 1

    def _percent_scale(self) -> int:
        """Return the currently detected scale for percent-like values."""
        if self.entity_description.device_scale <= 1:
            return 1
        return detect_percent_scale(
            self.coordinator.data or {},
            ("minSoc", "socSet"),
        )

    def _device_value_to_native(self, value: int | float) -> float:
        """Convert a raw device value into the HA-facing value."""
        scale = self._percent_scale()
        if scale > 1:
            return float(value) / scale
        return float(value)

    def _native_value_to_device(self, value: float) -> int:
        """Convert the HA-facing value into the raw device value."""
        scale = self._percent_scale()
        if scale > 1:
            return int(value * scale)
        return int(value)

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data
        if not data:
            return None
        val = data.get(self.entity_description.value_key)
        return self._device_value_to_native(val) if val is not None else None

    async def async_set_native_value(self, value: float) -> None:
        """Write the new value to the device, then refresh coordinator data."""
        await self.coordinator.async_write_property(
            self.entity_description.write_key,
            self._native_value_to_device(value),
        )
        await self.coordinator.async_request_refresh()
