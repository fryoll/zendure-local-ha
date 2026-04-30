"""Tests for sensor entities: power, battery, and energy accumulation."""
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest

from custom_components.zendure_local.sensor import (
    BATTERY_SENSORS,
    ENERGY_SENSORS,
    POWER_SENSORS,
    ZendureEnergySensor,
    ZendureSensor,
)

from .conftest import MOCK_NORMALIZED, MOCK_SERIAL


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sensor(mock_coordinator, description):
    return ZendureSensor(mock_coordinator, description)


def _energy(mock_coordinator, index=0):
    return ZendureEnergySensor(mock_coordinator, ENERGY_SENSORS[index])


# ---------------------------------------------------------------------------
# Power sensors — native_value
# ---------------------------------------------------------------------------


def test_solar_input_power_value(mock_coordinator):
    s = _sensor(mock_coordinator, POWER_SENSORS[0])  # solar_input_power
    assert s.native_value == 450


def test_solar_mppt_values(mock_coordinator):
    for i, expected in enumerate([120, 130, 100, 100], start=1):
        s = _sensor(mock_coordinator, POWER_SENSORS[i])
        assert s.native_value == expected, f"MPPT {i} mismatch"


def test_pack_input_power(mock_coordinator):
    s = _sensor(mock_coordinator, POWER_SENSORS[5])  # pack_input_power
    assert s.native_value == 200


def test_output_home_power(mock_coordinator):
    s = _sensor(mock_coordinator, POWER_SENSORS[7])  # output_home_power
    assert s.native_value == 250


def test_returns_none_when_coordinator_has_no_data(mock_coordinator):
    mock_coordinator.data = None
    s = _sensor(mock_coordinator, POWER_SENSORS[0])
    assert s.native_value is None


def test_returns_none_when_key_missing(mock_coordinator):
    mock_coordinator.data = {}
    s = _sensor(mock_coordinator, POWER_SENSORS[0])
    assert s.native_value is None


# ---------------------------------------------------------------------------
# Power sensors — availability
# ---------------------------------------------------------------------------


def test_power_sensor_available_when_key_present(mock_coordinator):
    s = _sensor(mock_coordinator, POWER_SENSORS[0])
    assert s.available is True


def test_power_sensor_unavailable_when_coordinator_fails(mock_coordinator):
    mock_coordinator.last_update_success = False
    s = _sensor(mock_coordinator, POWER_SENSORS[0])
    assert s.available is False


def test_power_sensor_unavailable_when_key_missing(mock_coordinator):
    mock_coordinator.data = {}
    s = _sensor(mock_coordinator, POWER_SENSORS[0])
    assert s.available is False


def test_power_sensor_unavailable_when_data_is_none(mock_coordinator):
    mock_coordinator.data = None
    s = _sensor(mock_coordinator, POWER_SENSORS[0])
    assert s.available is False


# ---------------------------------------------------------------------------
# Battery sensors
# ---------------------------------------------------------------------------


def test_battery_soc_from_electriclevel(mock_coordinator):
    s = _sensor(mock_coordinator, BATTERY_SENSORS[0])  # electric_level
    assert s.native_value == 75


def test_battery_soc_falls_back_to_soclevel(mock_coordinator):
    mock_coordinator.data = {"socLevel": 68}
    s = _sensor(mock_coordinator, BATTERY_SENSORS[0])
    assert s.native_value == 68


def test_battery_soc_scaled_by_10_is_normalized(mock_coordinator):
    mock_coordinator.data = {"electricLevel": 750, "minSoc": 100, "socSet": 900}
    s = _sensor(mock_coordinator, BATTERY_SENSORS[0])
    assert s.native_value == 75.0


def test_battery_soc_scaled_by_100_is_normalized(mock_coordinator):
    mock_coordinator.data = {"electricLevel": 7500, "minSoc": 1000, "socSet": 9000}
    s = _sensor(mock_coordinator, BATTERY_SENSORS[0])
    assert s.native_value == 75.0


def test_battery_soc_returns_none_when_both_missing(mock_coordinator):
    mock_coordinator.data = {}
    s = _sensor(mock_coordinator, BATTERY_SENSORS[0])
    assert s.native_value is None


def test_pack0_soc_value(mock_coordinator):
    s = _sensor(mock_coordinator, BATTERY_SENSORS[1])  # pack0_soc
    assert s.native_value == 74


def test_pack_soc_scaled_by_100_is_normalized(mock_coordinator):
    mock_coordinator.data = {"pack0_soc": 7400, "minSoc": 1000, "socSet": 9000}
    s = _sensor(mock_coordinator, BATTERY_SENSORS[1])
    assert s.native_value == 74.0


def test_pack1_soc_value(mock_coordinator):
    s = _sensor(mock_coordinator, BATTERY_SENSORS[2])  # pack1_soc
    assert s.native_value == 76


def test_pack_soc_unavailable_when_no_pack_data(mock_coordinator):
    mock_coordinator.data = {"electricLevel": 75}
    s = _sensor(mock_coordinator, BATTERY_SENSORS[1])
    assert s.available is False


def test_battery_soc_unavailable_when_both_keys_absent(mock_coordinator):
    mock_coordinator.data = {}
    s = _sensor(mock_coordinator, BATTERY_SENSORS[0])
    assert s.available is False


# ---------------------------------------------------------------------------
# Unique IDs and device class
# ---------------------------------------------------------------------------


def test_unique_id_format(mock_coordinator):
    s = _sensor(mock_coordinator, POWER_SENSORS[0])
    assert s.unique_id == f"{MOCK_SERIAL}_solar_input_power"


def test_energy_sensor_unique_id(mock_coordinator):
    e = _energy(mock_coordinator)
    assert e.unique_id == f"{MOCK_SERIAL}_solar_energy"


# ---------------------------------------------------------------------------
# Energy sensor — trapezoidal accumulation
# ---------------------------------------------------------------------------


def test_energy_sensor_initial_value_is_zero(mock_coordinator):
    e = _energy(mock_coordinator)
    assert e.native_value == 0.0


def test_energy_accumulates_constant_power(mock_coordinator):
    """400 W constant for 1 hour should yield 0.4 kWh."""
    e = _energy(mock_coordinator)
    e.async_write_ha_state = Mock()

    t0 = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    t1 = datetime(2026, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
    mock_coordinator.data = {"solarInputPower": 400}

    e._last_time = t0
    e._last_power_w = 400.0

    with patch(
        "custom_components.zendure_local.sensor.dt_util.utcnow", return_value=t1
    ):
        e._handle_coordinator_update()

    assert e.native_value == pytest.approx(0.4, rel=1e-3)


def test_energy_trapezoidal_rule_rising_power(mock_coordinator):
    """Power rises 0 → 1000 W over 1 hour → (0+1000)/2 * 1h / 1000 = 0.5 kWh."""
    e = _energy(mock_coordinator)
    e.async_write_ha_state = Mock()

    t0 = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    t1 = datetime(2026, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
    mock_coordinator.data = {"solarInputPower": 1000}

    e._last_time = t0
    e._last_power_w = 0.0

    with patch(
        "custom_components.zendure_local.sensor.dt_util.utcnow", return_value=t1
    ):
        e._handle_coordinator_update()

    assert e.native_value == pytest.approx(0.5, rel=1e-3)


def test_energy_not_incremented_on_coordinator_failure(mock_coordinator):
    """When last_update_success is False the counter must not change."""
    e = _energy(mock_coordinator)
    e.async_write_ha_state = Mock()

    t0 = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    t1 = datetime(2026, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
    mock_coordinator.data = {"solarInputPower": 400}
    mock_coordinator.last_update_success = False

    e._last_time = t0
    e._last_power_w = 400.0
    e._total_kwh = 1.0

    with patch(
        "custom_components.zendure_local.sensor.dt_util.utcnow", return_value=t1
    ):
        e._handle_coordinator_update()

    assert e.native_value == pytest.approx(1.0)


def test_energy_does_not_go_negative(mock_coordinator):
    """Power = 0 means no energy increment, total stays the same."""
    e = _energy(mock_coordinator)
    e.async_write_ha_state = Mock()

    t0 = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    t1 = datetime(2026, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
    mock_coordinator.data = {"solarInputPower": 0}

    e._last_time = t0
    e._last_power_w = 0.0
    e._total_kwh = 5.0

    with patch(
        "custom_components.zendure_local.sensor.dt_util.utcnow", return_value=t1
    ):
        e._handle_coordinator_update()

    assert e.native_value == pytest.approx(5.0)


def test_energy_sensor_always_available(mock_coordinator):
    """Energy sensors stay available even when the coordinator fails."""
    mock_coordinator.last_update_success = False
    e = _energy(mock_coordinator)
    assert e.available is True


def test_energy_sensor_accumulates_multiple_intervals(mock_coordinator):
    """Three consecutive 30-second intervals at 600 W → 3 * (600 * 30/3600/1000)."""
    e = _energy(mock_coordinator)
    e.async_write_ha_state = Mock()
    mock_coordinator.data = {"solarInputPower": 600}

    base = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    e._last_power_w = 600.0

    for i in range(1, 4):
        t = base + timedelta(seconds=i * 30)
        e._last_time = base + timedelta(seconds=(i - 1) * 30)
        with patch(
            "custom_components.zendure_local.sensor.dt_util.utcnow", return_value=t
        ):
            e._handle_coordinator_update()

    expected = 3 * (600 * 30 / 3600 / 1000)
    assert e.native_value == pytest.approx(expected, rel=1e-3)
