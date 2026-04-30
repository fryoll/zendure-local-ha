"""Tests for ZendureCoordinator: data fetching, normalization, write."""
import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.zendure_local.coordinator import _normalize_data

from .conftest import MOCK_HOST, MOCK_NORMALIZED, MOCK_REPORT_URL, MOCK_RESPONSE, MOCK_SERIAL, MOCK_WRITE_URL


# ---------------------------------------------------------------------------
# _normalize_data — pure unit tests, no hass
# ---------------------------------------------------------------------------


def test_normalize_flattens_pack_data():
    raw = {
        "properties": {
            "electricLevel": 80,
            "packData": [{"socLevel": 79}, {"socLevel": 81}],
        }
    }
    result = _normalize_data(raw)
    assert result["pack0_soc"] == 79
    assert result["pack1_soc"] == 81
    assert "packData" not in result


def test_normalize_only_two_packs_max():
    raw = {
        "properties": {
            "packData": [{"socLevel": 10}, {"socLevel": 20}, {"socLevel": 30}],
        }
    }
    result = _normalize_data(raw)
    assert "pack0_soc" in result
    assert "pack1_soc" in result
    assert "pack2_soc" not in result


def test_normalize_missing_pack_data():
    raw = {"properties": {"electricLevel": 50}}
    result = _normalize_data(raw)
    assert "pack0_soc" not in result
    assert result["electricLevel"] == 50


def test_normalize_soclevel_aliased_to_electriclevel():
    """Device reports socLevel but not electricLevel — aliased to electricLevel."""
    raw = {"properties": {"socLevel": 65}}
    result = _normalize_data(raw)
    assert result["electricLevel"] == 65
    assert result["socLevel"] == 65


def test_normalize_electriclevel_takes_priority():
    """When both keys are present, electricLevel is kept as-is."""
    raw = {"properties": {"electricLevel": 70, "socLevel": 68}}
    result = _normalize_data(raw)
    assert result["electricLevel"] == 70


def test_normalize_flat_response_without_properties_wrapper():
    """Some firmwares return properties at the root level."""
    raw = {"electricLevel": 55, "solarInputPower": 300}
    result = _normalize_data(raw)
    assert result["electricLevel"] == 55
    assert result["solarInputPower"] == 300


def test_normalize_full_response():
    result = _normalize_data(MOCK_RESPONSE)
    for key, value in MOCK_NORMALIZED.items():
        assert result[key] == value, f"Mismatch for key {key!r}"


def test_normalize_pack_missing_soclevel_skipped():
    """Pack entries without socLevel should not produce a key."""
    raw = {"properties": {"packData": [{"voltage": 48}]}}
    result = _normalize_data(raw)
    assert "pack0_soc" not in result


# ---------------------------------------------------------------------------
# _async_update_data — integration tests using hass + aioclient_mock
# ---------------------------------------------------------------------------


async def test_fetch_success(real_coordinator, aioclient_mock):
    aioclient_mock.get(MOCK_REPORT_URL, json=MOCK_RESPONSE)
    data = await real_coordinator._async_update_data()

    assert data["solarInputPower"] == 450
    assert data["pack0_soc"] == 74
    assert data["electricLevel"] == 75


async def test_fetch_raises_update_failed_on_connection_error(real_coordinator, aioclient_mock):
    aioclient_mock.get(MOCK_REPORT_URL, exc=Exception("timeout"))
    with pytest.raises(UpdateFailed):
        await real_coordinator._async_update_data()


async def test_fetch_raises_update_failed_on_http_error(real_coordinator, aioclient_mock):
    aioclient_mock.get(MOCK_REPORT_URL, status=500)
    with pytest.raises(UpdateFailed):
        await real_coordinator._async_update_data()


# ---------------------------------------------------------------------------
# async_write_property
# ---------------------------------------------------------------------------


async def test_write_property_posts_correct_payload(real_coordinator, aioclient_mock):
    aioclient_mock.post(MOCK_WRITE_URL, json={"success": True})
    await real_coordinator.async_write_property("outputLimit", 400)

    assert aioclient_mock.call_count == 1
    # mock_calls entries are (method, url, data, headers) tuples
    _method, _url, data, _headers = aioclient_mock.mock_calls[0]
    assert data == {"properties": {"outputLimit": 400}}


async def test_write_property_raises_on_http_error(real_coordinator, aioclient_mock):
    aioclient_mock.post(MOCK_WRITE_URL, status=503)
    with pytest.raises(Exception):
        await real_coordinator.async_write_property("outputLimit", 0)


async def test_coordinator_stores_serial_and_host(real_coordinator):
    assert real_coordinator.serial_number == MOCK_SERIAL
    assert real_coordinator.host == MOCK_HOST
