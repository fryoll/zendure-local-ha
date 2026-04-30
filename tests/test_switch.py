"""Tests for the injection switch entity."""
from unittest.mock import Mock

from custom_components.zendure_local.const import DEFAULT_OUTPUT_LIMIT
from custom_components.zendure_local.switch import ZendureInjectionSwitch

from .conftest import MOCK_NORMALIZED, MOCK_SERIAL


def _switch(mock_coordinator) -> ZendureInjectionSwitch:
    return ZendureInjectionSwitch(mock_coordinator)


# ---------------------------------------------------------------------------
# is_on — reflects outputLimit > 0
# ---------------------------------------------------------------------------


def test_is_on_when_limit_nonzero(mock_coordinator):
    # MOCK_NORMALIZED has outputLimit=600
    assert _switch(mock_coordinator).is_on is True


def test_is_off_when_limit_zero(mock_coordinator):
    mock_coordinator.data = {**MOCK_NORMALIZED, "outputLimit": 0}
    assert _switch(mock_coordinator).is_on is False


def test_is_none_when_no_data(mock_coordinator):
    mock_coordinator.data = None
    assert _switch(mock_coordinator).is_on is None


def test_is_none_when_key_missing(mock_coordinator):
    mock_coordinator.data = {}
    assert _switch(mock_coordinator).is_on is None


# ---------------------------------------------------------------------------
# unique_id
# ---------------------------------------------------------------------------


def test_unique_id(mock_coordinator):
    assert _switch(mock_coordinator).unique_id == f"{MOCK_SERIAL}_injection_enabled"


# ---------------------------------------------------------------------------
# async_turn_off — posts 0
# ---------------------------------------------------------------------------


async def test_turn_off_posts_zero(mock_coordinator):
    await _switch(mock_coordinator).async_turn_off()
    mock_coordinator.async_write_property.assert_called_once_with("outputLimit", 0)
    mock_coordinator.async_request_refresh.assert_called_once()


# ---------------------------------------------------------------------------
# async_turn_on — restores last known non-zero limit
# ---------------------------------------------------------------------------


async def test_turn_on_uses_default_when_no_prior_limit(mock_coordinator):
    """Before any coordinator update, ON must fall back to DEFAULT_OUTPUT_LIMIT."""
    mock_coordinator.data = {**MOCK_NORMALIZED, "outputLimit": 0}
    sw = _switch(mock_coordinator)
    # _last_nonzero_limit is DEFAULT_OUTPUT_LIMIT at construction time
    await sw.async_turn_on()
    mock_coordinator.async_write_property.assert_called_once_with(
        "outputLimit", DEFAULT_OUTPUT_LIMIT
    )


async def test_turn_on_restores_remembered_limit(mock_coordinator):
    """After _last_nonzero_limit is set to 600, ON must restore 600."""
    sw = _switch(mock_coordinator)
    sw._last_nonzero_limit = 600
    mock_coordinator.data = {**MOCK_NORMALIZED, "outputLimit": 0}
    await sw.async_turn_on()
    mock_coordinator.async_write_property.assert_called_once_with("outputLimit", 600)


# ---------------------------------------------------------------------------
# _handle_coordinator_update — tracks _last_nonzero_limit
# ---------------------------------------------------------------------------


def test_update_tracks_nonzero_limit(mock_coordinator):
    sw = _switch(mock_coordinator)
    sw.async_write_ha_state = Mock()
    mock_coordinator.data = {**MOCK_NORMALIZED, "outputLimit": 750}
    sw._handle_coordinator_update()
    assert sw._last_nonzero_limit == 750


def test_update_does_not_track_zero(mock_coordinator):
    """When outputLimit is 0, the remembered limit must not be overwritten."""
    sw = _switch(mock_coordinator)
    sw.async_write_ha_state = Mock()
    sw._last_nonzero_limit = 500
    mock_coordinator.data = {**MOCK_NORMALIZED, "outputLimit": 0}
    sw._handle_coordinator_update()
    assert sw._last_nonzero_limit == 500  # unchanged


def test_update_calls_write_ha_state(mock_coordinator):
    sw = _switch(mock_coordinator)
    sw.async_write_ha_state = Mock()
    sw._handle_coordinator_update()
    sw.async_write_ha_state.assert_called_once()


# ---------------------------------------------------------------------------
# Availability (inherited from ZendureBaseEntity)
# ---------------------------------------------------------------------------


def test_available_when_coordinator_succeeds(mock_coordinator):
    assert _switch(mock_coordinator).available is True


def test_unavailable_when_coordinator_fails(mock_coordinator):
    mock_coordinator.last_update_success = False
    assert _switch(mock_coordinator).available is False
