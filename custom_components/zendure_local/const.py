"""Constants for the Zendure Local integration."""
from homeassistant.const import Platform

DOMAIN = "zendure_local"
CONF_SERIAL_NUMBER = "serial_number"

DEFAULT_SCAN_INTERVAL = 30
HTTP_TIMEOUT = 10

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SWITCH,
]

API_REPORT_PATH = "/properties/report"
API_WRITE_PATH = "/properties/write"

# Internal option keys → device integer values
AC_MODE_TO_VALUE: dict[str, int] = {
    "auto": 0,
    "grid_charge": 1,
    "injection": 2,
}
AC_MODE_FROM_VALUE: dict[int, str] = {v: k for k, v in AC_MODE_TO_VALUE.items()}

DEVICE_NAME = "SolarFlow 800 Pro2"
MANUFACTURER = "Zendure"
MODEL = "SolarFlow 800 Pro2"

DEFAULT_OUTPUT_LIMIT = 800
