# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

**zendure-local-ha** is a 100% local Home Assistant custom integration for the **Zendure SolarFlow 800 Pro2** (and compatible hub-based devices).
No cloud dependency, no MQTT — pure REST HTTP polling every 30 seconds.

- Repository: https://github.com/fryoll/zendure-local-ha
- HA domain: `zendure_local`
- HACS compatible: yes (custom repository)
- Minimum HA version: 2026.4
- Python: 3.12+

## Development commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Install test dependencies
pip install -r requirements_test.txt

# Run all tests
pytest

# Run a single test file
pytest tests/test_coordinator.py

# Run a single test by name
pytest tests/test_coordinator.py::test_normalize_flattens_pack_data

# Run tests with coverage
pytest --cov

# Install commit hooks (commitizen / release-please)
pip install -r requirements_test.txt && pre-commit install --hook-type commit-msg
```

## Architecture

### Data flow

1. `__init__.py` creates a `ZendureCoordinator` on entry setup, stores it in `entry.runtime_data`, then forwards setup to each platform (`sensor`, `number`, `select`).
2. All platforms retrieve the coordinator via `entry.runtime_data`.
3. `coordinator.py` polls `GET /properties/report` every 30 s, normalizes the payload via `_normalize_data()`, and stores it in `coordinator.data` (a flat `dict`).
4. Writable entities (`number`, `select`) call `coordinator.async_write_property(key, value)` which POSTs to `/properties/write`, then call `coordinator.async_request_refresh()`.

### `_normalize_data()` (coordinator.py)

Transforms the raw device payload into a flat dict:
- Strips the `properties` wrapper if present (some firmwares return a flat root object).
- Flattens `packData` array into `pack0_soc` / `pack1_soc` keys (max 2 packs).
- Aliases `socLevel` → `electricLevel` when only `socLevel` is present.

### Sensor entity patterns (sensor.py)

`ZendureSensorDescription` has two mutually exclusive value strategies:
- `value_key`: simple `data[key]` lookup — use for raw device fields.
- `value_fn`: callable receiving the full `data` dict — use when normalization is needed (e.g. percent scale detection).

`ZendureEnergySensor` extends `RestoreSensor` (not `SensorEntity`) to persist the accumulated kWh total across HA restarts. It integrates power readings via the trapezoidal rule in `_handle_coordinator_update`.

### Percent scale detection

The device may report percent-like values (`electricLevel`, `minSoc`, `socSet`) as ×1, ×10, or ×100 depending on firmware.
`_detect_percent_scale()` infers the multiplier from raw values and divides accordingly. This helper is duplicated in `sensor.py` and `number.py`.
For `ZendureNumberDescription`, setting `device_scale > 1` opts the entity into this scaling on both read and write.

### Config flow (config_flow.py)

Two-step setup + a reconfigure step:
1. **user** — validates IPv4 address, then calls `_probe_device()` to fetch `/properties/report` and extract the serial number (tries keys `sn`, `deviceSn`, `snNumber` in order).
2. **confirm** — displays discovered serial number; user confirms to create the entry.
3. **reconfigure** — allows updating the device IP without losing entity history.

## Test fixtures

Tests use `pytest-homeassistant-custom-component` which provides the `hass` and `aioclient_mock` fixtures.

`conftest.py` defines two coordinator fixtures:
- `mock_coordinator` — a `MagicMock` with pre-populated data; use this for entity unit tests (no `hass` required).
- `real_coordinator` — a real `ZendureCoordinator` wired to `hass`; use this with `aioclient_mock` for HTTP-level integration tests.

## Conventions

- **Commit style**: Conventional Commits enforced by commitizen (`feat:`, `fix:`, `chore:`, etc.)
- **Versioning**: release-please manages CHANGELOG and version bumps
- **No YAML config**: integration is configured entirely through the UI config flow
- **Polling only**: no push / webhook — coordinator polls REST API every 30 s
- **Entity strings**: display names are in `translations/en.json` and `translations/fr.json`; add both when adding a new entity key
