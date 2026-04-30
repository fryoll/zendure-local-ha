"""Sensor platform for Zendure Local."""
from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .coordinator import ZendureCoordinator
from .entity import ZendureBaseEntity

_LOGGER = logging.getLogger(__name__)

type StateType = float | int | str | None


def _detect_percent_scale(data: dict, keys: tuple[str, ...]) -> int:
    """Detect whether the selected percent-like values are reported as x1, x10, or x100."""
    raw_values = [data.get(key) for key in keys if data.get(key) is not None]

    if any(float(value) > 1000 for value in raw_values):
        return 100
    if any(float(value) > 100 for value in raw_values):
        return 10
    return 1


def _normalize_percent_value(
    data: dict, value: StateType, keys: tuple[str, ...]
) -> StateType:
    """Normalize a raw percent-like value to the 0-100 HA range."""
    if value is None:
        return None
    scale = _detect_percent_scale(data, keys)
    if scale > 1:
        return float(value) / scale
    return value


# ---------------------------------------------------------------------------
# Sensor descriptions
# ---------------------------------------------------------------------------


@dataclass(frozen=True, kw_only=True)
class ZendureSensorDescription(SensorEntityDescription):
    """Extends SensorEntityDescription with flexible value extraction."""

    value_key: str | None = None
    value_fn: Callable[[dict], StateType] | None = None


POWER_SENSORS: tuple[ZendureSensorDescription, ...] = (
    ZendureSensorDescription(
        key="solar_input_power",
        translation_key="solar_input_power",
        value_key="solarInputPower",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
    ),
    ZendureSensorDescription(
        key="solar_power1",
        translation_key="solar_power1",
        value_key="solarPower1",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
    ),
    ZendureSensorDescription(
        key="solar_power2",
        translation_key="solar_power2",
        value_key="solarPower2",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
    ),
    ZendureSensorDescription(
        key="solar_power3",
        translation_key="solar_power3",
        value_key="solarPower3",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
    ),
    ZendureSensorDescription(
        key="solar_power4",
        translation_key="solar_power4",
        value_key="solarPower4",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
    ),
    ZendureSensorDescription(
        key="pack_input_power",
        translation_key="pack_input_power",
        value_key="packInputPower",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
    ),
    ZendureSensorDescription(
        key="output_pack_power",
        translation_key="output_pack_power",
        value_key="outputPackPower",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
    ),
    ZendureSensorDescription(
        key="output_home_power",
        translation_key="output_home_power",
        value_key="outputHomePower",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
    ),
    ZendureSensorDescription(
        key="grid_input_power",
        translation_key="grid_input_power",
        value_key="gridInputPower",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0,
    ),
)

BATTERY_SENSORS: tuple[ZendureSensorDescription, ...] = (
    ZendureSensorDescription(
        key="electric_level",
        translation_key="electric_level",
        # Device may use electricLevel or socLevel; prefer electricLevel
        value_fn=lambda d: (
            _normalize_percent_value(d, d.get("electricLevel"), ("electricLevel", "socLevel"))
            if d.get("electricLevel") is not None
            else _normalize_percent_value(d, d.get("socLevel"), ("electricLevel", "socLevel"))
        ),
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
    ),
    ZendureSensorDescription(
        key="pack0_soc",
        translation_key="pack0_soc",
        value_fn=lambda d: _normalize_percent_value(d, d.get("pack0_soc"), ("pack0_soc",)),
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
    ),
    ZendureSensorDescription(
        key="pack1_soc",
        translation_key="pack1_soc",
        value_fn=lambda d: _normalize_percent_value(d, d.get("pack1_soc"), ("pack1_soc",)),
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
    ),
)


@dataclass(frozen=True)
class EnergySensorConfig:
    """Maps an energy accumulation sensor to its source power key."""

    key: str
    translation_key: str
    power_key: str


ENERGY_SENSORS: tuple[EnergySensorConfig, ...] = (
    EnergySensorConfig(
        key="solar_energy",
        translation_key="solar_energy",
        power_key="solarInputPower",
    ),
    EnergySensorConfig(
        key="pack_charge_energy",
        translation_key="pack_charge_energy",
        power_key="packInputPower",
    ),
    EnergySensorConfig(
        key="pack_discharge_energy",
        translation_key="pack_discharge_energy",
        power_key="outputPackPower",
    ),
    EnergySensorConfig(
        key="output_home_energy",
        translation_key="output_home_energy",
        power_key="outputHomePower",
    ),
    EnergySensorConfig(
        key="grid_input_energy",
        translation_key="grid_input_energy",
        power_key="gridInputPower",
    ),
)


# ---------------------------------------------------------------------------
# Platform setup
# ---------------------------------------------------------------------------


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Register all sensor entities for this config entry."""
    coordinator: ZendureCoordinator = entry.runtime_data

    entities: list[SensorEntity] = [
        ZendureSensor(coordinator, desc)
        for desc in (*POWER_SENSORS, *BATTERY_SENSORS)
    ]
    entities.extend(
        ZendureEnergySensor(coordinator, cfg) for cfg in ENERGY_SENSORS
    )
    async_add_entities(entities)


# ---------------------------------------------------------------------------
# Entity classes
# ---------------------------------------------------------------------------


class ZendureSensor(ZendureBaseEntity, SensorEntity):
    """Read-only sensor for a single device property."""

    entity_description: ZendureSensorDescription

    def __init__(
        self,
        coordinator: ZendureCoordinator,
        description: ZendureSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.serial_number}_{description.key}"

    @property
    def native_value(self) -> StateType:
        data = self.coordinator.data
        if not data:
            return None
        desc = self.entity_description
        if desc.value_fn is not None:
            return desc.value_fn(data)
        return data.get(desc.value_key)

    @property
    def available(self) -> bool:
        if not self.coordinator.last_update_success or not self.coordinator.data:
            return False
        desc = self.entity_description
        if desc.value_fn is not None:
            return desc.value_fn(self.coordinator.data) is not None
        return desc.value_key in self.coordinator.data


class ZendureEnergySensor(ZendureBaseEntity, RestoreSensor):
    """Energy sensor that integrates power (W) into energy (kWh) via the trapezoidal rule.

    State is persisted across HA restarts via RestoreSensor.
    """

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_suggested_display_precision = 3

    def __init__(
        self,
        coordinator: ZendureCoordinator,
        config: EnergySensorConfig,
    ) -> None:
        super().__init__(coordinator)
        self._config = config
        self._attr_translation_key = config.translation_key
        self._attr_unique_id = f"{coordinator.serial_number}_{config.key}"
        self._total_kwh: float = 0.0
        self._last_time: datetime | None = None
        self._last_power_w: float = 0.0

    async def async_added_to_hass(self) -> None:
        """Restore last persisted energy total and seed the integrator."""
        await super().async_added_to_hass()
        last = await self.async_get_last_sensor_data()
        if last is not None and last.native_value is not None:
            try:
                self._total_kwh = float(last.native_value)
            except (ValueError, TypeError):
                self._total_kwh = 0.0
        self._last_time = dt_util.utcnow()
        self._last_power_w = self._current_power_w()

    def _current_power_w(self) -> float:
        data = self.coordinator.data
        if not data:
            return 0.0
        return float(data.get(self._config.power_key) or 0)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Accumulate energy using the trapezoidal rule, then push state."""
        now = dt_util.utcnow()
        power_w = self._current_power_w()

        if self._last_time is not None and self.coordinator.last_update_success:
            delta_h = (now - self._last_time).total_seconds() / 3600.0
            avg_w = (self._last_power_w + power_w) / 2.0
            delta_kwh = avg_w * delta_h / 1000.0
            if delta_kwh > 0:
                self._total_kwh += delta_kwh

        self._last_time = now
        self._last_power_w = power_w
        self.async_write_ha_state()

    @property
    def native_value(self) -> float:
        return round(self._total_kwh, 3)

    @property
    def available(self) -> bool:
        # Energy counters stay available even during temporary device outages
        return True
