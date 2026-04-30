"""Base entity shared by all Zendure Local platforms."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEVICE_NAME, DOMAIN, MANUFACTURER, MODEL
from .coordinator import ZendureCoordinator


class ZendureBaseEntity(CoordinatorEntity[ZendureCoordinator]):
    """Provides device info and availability for every Zendure entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ZendureCoordinator) -> None:
        super().__init__(coordinator)

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.serial_number)},
            name=DEVICE_NAME,
            manufacturer=MANUFACTURER,
            model=MODEL,
            serial_number=self.coordinator.serial_number,
        )

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success
