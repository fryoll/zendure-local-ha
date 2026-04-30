"""Shared fixtures and mock data for Zendure Local tests."""
from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.const import CONF_HOST

from custom_components.zendure_local.const import CONF_SERIAL_NUMBER, DEFAULT_OUTPUT_LIMIT, DOMAIN
from custom_components.zendure_local.coordinator import ZendureCoordinator

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

MOCK_HOST = "192.168.1.100"
MOCK_SERIAL = "ZD123456"
MOCK_REPORT_URL = f"http://{MOCK_HOST}/properties/report"
MOCK_WRITE_URL = f"http://{MOCK_HOST}/properties/write"

MOCK_PROPERTIES: dict = {
    "sn": MOCK_SERIAL,
    "solarInputPower": 450,
    "solarPower1": 120,
    "solarPower2": 130,
    "solarPower3": 100,
    "solarPower4": 100,
    "packInputPower": 200,
    "outputPackPower": 0,
    "outputHomePower": 250,
    "gridInputPower": 0,
    "electricLevel": 75,
    "socSet": 90,
    "minSoc": 10,
    "outputLimit": 600,
    "acMode": 2,
    "packData": [
        {"socLevel": 74},
        {"socLevel": 76},
    ],
}

MOCK_RESPONSE: dict = {"success": True, "properties": MOCK_PROPERTIES}

# Expected result of _normalize_data(MOCK_RESPONSE)
MOCK_NORMALIZED: dict = {
    "sn": MOCK_SERIAL,
    "solarInputPower": 450,
    "solarPower1": 120,
    "solarPower2": 130,
    "solarPower3": 100,
    "solarPower4": 100,
    "packInputPower": 200,
    "outputPackPower": 0,
    "outputHomePower": 250,
    "gridInputPower": 0,
    "electricLevel": 75,
    "socSet": 90,
    "minSoc": 10,
    "outputLimit": 600,
    "acMode": 2,
    "pack0_soc": 74,
    "pack1_soc": 76,
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Config entry pre-populated with test host and serial."""
    return MockConfigEntry(
        domain=DOMAIN,
        title=f"SolarFlow 800 Pro2 ({MOCK_SERIAL})",
        data={CONF_HOST: MOCK_HOST, CONF_SERIAL_NUMBER: MOCK_SERIAL},
        unique_id=MOCK_SERIAL,
    )


@pytest.fixture
def mock_coordinator(mock_config_entry) -> MagicMock:
    """Lightweight mock coordinator for entity unit tests (no hass needed)."""
    coord = MagicMock(spec=ZendureCoordinator)
    coord.data = MOCK_NORMALIZED.copy()
    coord.last_update_success = True
    coord.serial_number = MOCK_SERIAL
    coord.async_write_property = AsyncMock()
    coord.async_request_refresh = AsyncMock()
    coord.config_entry = mock_config_entry
    return coord


@pytest.fixture
def real_coordinator(hass, mock_config_entry) -> ZendureCoordinator:
    """Real coordinator wired to the hass instance (for HTTP-level tests)."""
    mock_config_entry.add_to_hass(hass)
    return ZendureCoordinator(hass, mock_config_entry)
