"""Unit tests for shared utilities."""

from custom_components.zendure_local.utils import detect_percent_scale


def test_scale_1_when_all_values_under_100():
    assert detect_percent_scale({"minSoc": 50, "socSet": 80}, ("minSoc", "socSet")) == 1


def test_scale_10_when_values_between_100_and_1000():
    assert detect_percent_scale({"minSoc": 150, "socSet": 900}, ("minSoc", "socSet")) == 10


def test_scale_100_when_values_over_1000():
    assert detect_percent_scale({"minSoc": 1500, "socSet": 9000}, ("minSoc", "socSet")) == 100


def test_missing_key_is_ignored():
    assert detect_percent_scale({"minSoc": 50}, ("minSoc", "socSet")) == 1


def test_all_keys_missing_returns_1():
    assert detect_percent_scale({}, ("minSoc", "socSet")) == 1


def test_boundary_value_101_returns_scale_10():
    assert detect_percent_scale({"minSoc": 101}, ("minSoc",)) == 10


def test_boundary_value_1001_returns_scale_100():
    assert detect_percent_scale({"minSoc": 1001}, ("minSoc",)) == 100


def test_boundary_exact_100_returns_scale_1():
    # exactly 100 does NOT satisfy > 100
    assert detect_percent_scale({"minSoc": 100}, ("minSoc",)) == 1


def test_boundary_exact_1000_returns_scale_10():
    # exactly 1000 does NOT satisfy > 1000
    assert detect_percent_scale({"minSoc": 1000}, ("minSoc",)) == 10
