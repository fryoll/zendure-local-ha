"""Tests for the Zendure Local config flow."""
import aiohttp
import pytest
from unittest.mock import AsyncMock, patch
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.data_entry_flow import FlowResultType

from custom_components.zendure_local.const import CONF_SERIAL_NUMBER, DOMAIN

from .conftest import MOCK_HOST, MOCK_REPORT_URL, MOCK_RESPONSE, MOCK_SERIAL

# enable_custom_integrations pops DATA_CUSTOM_COMPONENTS from hass.data so
# HA re-scans hass_config_dir/custom_components/ (pointed at project root in conftest).
pytestmark = pytest.mark.usefixtures("enable_custom_integrations")


# ---------------------------------------------------------------------------
# Happy path: user → confirm → entry created
# ---------------------------------------------------------------------------


@pytest.mark.skip(reason="Temporarily disabled in CI: lingering aiohttp shutdown thread")
async def test_full_flow_creates_entry(hass, aioclient_mock):
    aioclient_mock.get(MOCK_REPORT_URL, json=MOCK_RESPONSE)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_HOST: MOCK_HOST}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "confirm"

    with patch(
        "custom_components.zendure_local.coordinator.ZendureCoordinator.async_config_entry_first_refresh",
        new=AsyncMock(),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input={}
        )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_HOST] == MOCK_HOST
    assert result["data"][CONF_SERIAL_NUMBER] == MOCK_SERIAL


# ---------------------------------------------------------------------------
# IP validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bad_ip",
    [
        "not-an-ip",
        "999.999.999.999",
        "192.168.1",
        "192.168.1.1.1",
        "",
        "192.168.1.256",
    ],
)
async def test_invalid_ip_shows_error(hass, bad_ip):
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_HOST: bad_ip}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"][CONF_HOST] == "invalid_host"


# ---------------------------------------------------------------------------
# Connection failure
# ---------------------------------------------------------------------------


@pytest.mark.skip(reason="Temporarily disabled in CI: lingering aiohttp shutdown thread")
async def test_cannot_connect_shows_error(hass, aioclient_mock):
    aioclient_mock.get(MOCK_REPORT_URL, exc=aiohttp.ClientConnectionError())

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_HOST: MOCK_HOST}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "cannot_connect"


# ---------------------------------------------------------------------------
# Duplicate device detection
# ---------------------------------------------------------------------------


async def test_already_configured_aborts(hass, aioclient_mock, mock_config_entry):
    mock_config_entry.add_to_hass(hass)
    aioclient_mock.get(MOCK_REPORT_URL, json=MOCK_RESPONSE)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_HOST: MOCK_HOST}
    )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"


# ---------------------------------------------------------------------------
# Reconfigure
# ---------------------------------------------------------------------------


@pytest.mark.skip(reason="Temporarily disabled in CI: lingering coordinator refresh timer")
async def test_reconfigure_updates_host(hass, aioclient_mock, mock_config_entry):
    new_host = "192.168.1.200"
    mock_config_entry.add_to_hass(hass)
    aioclient_mock.get(f"http://{new_host}/properties/report", json=MOCK_RESPONSE)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": mock_config_entry.entry_id,
        },
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    with patch(
        "custom_components.zendure_local.coordinator.ZendureCoordinator.async_config_entry_first_refresh",
        new=AsyncMock(),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input={CONF_HOST: new_host}
        )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert mock_config_entry.data[CONF_HOST] == new_host


async def test_reconfigure_invalid_ip_shows_error(hass, mock_config_entry):
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": mock_config_entry.entry_id,
        },
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_HOST: "bad-ip"}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"][CONF_HOST] == "invalid_host"


async def test_reconfigure_cannot_connect_shows_error(hass, aioclient_mock, mock_config_entry):
    mock_config_entry.add_to_hass(hass)
    new_host = "192.168.1.200"
    aioclient_mock.get(f"http://{new_host}/properties/report", exc=aiohttp.ClientConnectionError())

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": mock_config_entry.entry_id,
        },
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_HOST: new_host}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "cannot_connect"
