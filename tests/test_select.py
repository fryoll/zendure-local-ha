"""Tests for the AC mode select entity."""
import pytest

from custom_components.zendure_local.const import AC_MODE_FROM_VALUE, AC_MODE_TO_VALUE
from custom_components.zendure_local.select import ZendureAcModeSelect

from .conftest import MOCK_NORMALIZED, MOCK_SERIAL


def _select(mock_coordinator) -> ZendureAcModeSelect:
    return ZendureAcModeSelect(mock_coordinator)


# ---------------------------------------------------------------------------
# current_option — int → string key mapping
# ---------------------------------------------------------------------------


def test_current_option_injection(mock_coordinator):
    # MOCK_NORMALIZED has acMode=2 → "injection"
    assert _select(mock_coordinator).current_option == "injection"


def test_current_option_auto(mock_coordinator):
    mock_coordinator.data = {**MOCK_NORMALIZED, "acMode": 0}
    assert _select(mock_coordinator).current_option == "auto"


def test_current_option_grid_charge(mock_coordinator):
    mock_coordinator.data = {**MOCK_NORMALIZED, "acMode": 1}
    assert _select(mock_coordinator).current_option == "grid_charge"


def test_current_option_none_when_no_data(mock_coordinator):
    mock_coordinator.data = None
    assert _select(mock_coordinator).current_option is None


def test_current_option_none_when_key_missing(mock_coordinator):
    mock_coordinator.data = {}
    assert _select(mock_coordinator).current_option is None


# ---------------------------------------------------------------------------
# options list
# ---------------------------------------------------------------------------


def test_options_list_contains_all_modes(mock_coordinator):
    assert set(_select(mock_coordinator).options) == {"auto", "grid_charge", "injection"}


# ---------------------------------------------------------------------------
# unique_id
# ---------------------------------------------------------------------------


def test_unique_id(mock_coordinator):
    assert _select(mock_coordinator).unique_id == f"{MOCK_SERIAL}_ac_mode"


# ---------------------------------------------------------------------------
# async_select_option — string key → int write
# ---------------------------------------------------------------------------


async def test_select_injection(mock_coordinator):
    await _select(mock_coordinator).async_select_option("injection")
    mock_coordinator.async_write_property.assert_called_once_with("acMode", 2)
    mock_coordinator.async_request_refresh.assert_called_once()


async def test_select_auto(mock_coordinator):
    await _select(mock_coordinator).async_select_option("auto")
    mock_coordinator.async_write_property.assert_called_once_with("acMode", 0)
    mock_coordinator.async_request_refresh.assert_called_once()


async def test_select_grid_charge(mock_coordinator):
    await _select(mock_coordinator).async_select_option("grid_charge")
    mock_coordinator.async_write_property.assert_called_once_with("acMode", 1)
    mock_coordinator.async_request_refresh.assert_called_once()


async def test_unknown_option_does_not_write(mock_coordinator):
    await _select(mock_coordinator).async_select_option("unknown_mode")
    mock_coordinator.async_write_property.assert_not_called()
    mock_coordinator.async_request_refresh.assert_not_called()


# ---------------------------------------------------------------------------
# Const round-trip: AC_MODE_TO_VALUE ↔ AC_MODE_FROM_VALUE
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("key", "value"),
    [("auto", 0), ("grid_charge", 1), ("injection", 2)],
)
def test_ac_mode_mapping_roundtrip(key, value):
    assert AC_MODE_TO_VALUE[key] == value
    assert AC_MODE_FROM_VALUE[value] == key
