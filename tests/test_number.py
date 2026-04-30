"""Tests for number entities: outputLimit, minSoc, socSet."""
import pytest

from custom_components.zendure_local.number import NUMBER_DESCRIPTIONS, ZendureNumber

from .conftest import MOCK_NORMALIZED, MOCK_SERIAL


def _number(mock_coordinator, index: int) -> ZendureNumber:
    return ZendureNumber(mock_coordinator, NUMBER_DESCRIPTIONS[index])


# ---------------------------------------------------------------------------
# native_value
# ---------------------------------------------------------------------------


def test_output_limit_value(mock_coordinator):
    assert _number(mock_coordinator, 0).native_value == 600.0


def test_min_soc_value(mock_coordinator):
    assert _number(mock_coordinator, 1).native_value == 10.0


def test_soc_set_value(mock_coordinator):
    assert _number(mock_coordinator, 2).native_value == 90.0


def test_returns_none_when_coordinator_has_no_data(mock_coordinator):
    mock_coordinator.data = None
    assert _number(mock_coordinator, 0).native_value is None


def test_returns_none_when_key_missing(mock_coordinator):
    mock_coordinator.data = {}
    assert _number(mock_coordinator, 0).native_value is None


# ---------------------------------------------------------------------------
# availability (inherited from ZendureBaseEntity)
# ---------------------------------------------------------------------------


def test_available_when_coordinator_succeeds(mock_coordinator):
    assert _number(mock_coordinator, 0).available is True


def test_unavailable_when_coordinator_fails(mock_coordinator):
    mock_coordinator.last_update_success = False
    assert _number(mock_coordinator, 0).available is False


# ---------------------------------------------------------------------------
# unique_id
# ---------------------------------------------------------------------------


def test_unique_ids(mock_coordinator):
    assert _number(mock_coordinator, 0).unique_id == f"{MOCK_SERIAL}_output_limit"
    assert _number(mock_coordinator, 1).unique_id == f"{MOCK_SERIAL}_min_soc"
    assert _number(mock_coordinator, 2).unique_id == f"{MOCK_SERIAL}_soc_set"


# ---------------------------------------------------------------------------
# entity description ranges
# ---------------------------------------------------------------------------


def test_output_limit_range(mock_coordinator):
    n = _number(mock_coordinator, 0)
    assert n.native_min_value == 0
    assert n.native_max_value == 800
    assert n.native_step == 10


def test_min_soc_range(mock_coordinator):
    n = _number(mock_coordinator, 1)
    assert n.native_min_value == 0
    assert n.native_max_value == 100
    assert n.native_step == 5


def test_soc_set_range(mock_coordinator):
    n = _number(mock_coordinator, 2)
    assert n.native_min_value == 0
    assert n.native_max_value == 100
    assert n.native_step == 5


# ---------------------------------------------------------------------------
# async_set_native_value — writes to device, then refreshes
# ---------------------------------------------------------------------------


async def test_set_output_limit(mock_coordinator):
    await _number(mock_coordinator, 0).async_set_native_value(400.0)
    mock_coordinator.async_write_property.assert_called_once_with("outputLimit", 400)
    mock_coordinator.async_request_refresh.assert_called_once()


async def test_set_min_soc(mock_coordinator):
    await _number(mock_coordinator, 1).async_set_native_value(20.0)
    mock_coordinator.async_write_property.assert_called_once_with("minSoc", 20)
    mock_coordinator.async_request_refresh.assert_called_once()


async def test_set_soc_set(mock_coordinator):
    await _number(mock_coordinator, 2).async_set_native_value(85.0)
    mock_coordinator.async_write_property.assert_called_once_with("socSet", 85)
    mock_coordinator.async_request_refresh.assert_called_once()


async def test_set_value_casts_to_int(mock_coordinator):
    """Float input must be cast to int before being sent to the device."""
    await _number(mock_coordinator, 0).async_set_native_value(750.9)
    mock_coordinator.async_write_property.assert_called_once_with("outputLimit", 750)
