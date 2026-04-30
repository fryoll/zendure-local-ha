# CLAUDE.md — Zendure Local HA Integration

This file gives Claude Code (and other AI agents) context about this project.

## Project overview

**zendure-local-ha** is a 100% local Home Assistant custom integration for the **Zendure SolarFlow 800 Pro2** (and compatible hub-based devices).  
No cloud dependency, no MQTT — pure REST HTTP polling every 30 seconds.

- Repository: https://github.com/fryoll/zendure-local-ha
- HA domain: `zendure_local`
- HACS compatible: yes (custom repository)
- Minimum HA version: 2026.4
- Python: 3.12+

## Repository structure

```
custom_components/zendure_local/   # Integration source
    __init__.py                    # Setup entry point
    config_flow.py                 # UI config flow (IP validation, device confirmation)
    coordinator.py                 # DataUpdateCoordinator — REST polling every 30 s
    entity.py                      # Base entity class
    sensor.py                      # Power (W), battery (%), energy (kWh) sensors
    number.py                      # Numeric controls (output power limit, min SOC…)
    select.py                      # Select controls (charge mode…)
    const.py                       # Constants (domain, endpoints, entity keys)
    manifest.json                  # HACS/HA manifest
    strings.json                   # English string keys
    translations/                  # en.json, fr.json
tests/                             # pytest test suite
```

## Development commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Install test dependencies
pip install -r requirements_test.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov

# Install commit hooks (commitizen / release-please)
pip install -r requirements_test.txt && pre-commit install --hook-type commit-msg
```

## Conventions

- **Commit style**: Conventional Commits enforced by commitizen (`feat:`, `fix:`, `chore:`, etc.)
- **Versioning**: release-please manages CHANGELOG and version bumps
- **No YAML config**: integration is configured entirely through the UI config flow
- **Polling only**: no push / webhook — coordinator polls REST API every 30 s
- **Energy entities**: use trapezoidal integration of power readings, persisted across restarts
- **Tests**: async (`asyncio_mode = "auto"`), mocked REST responses, no real device needed

## Key files to know

| File | Purpose |
|------|---------|
| `coordinator.py` | All REST calls live here; add new endpoints here |
| `const.py` | Entity keys, REST endpoint paths, domain constant |
| `sensor.py` | Sensor entity definitions mapped to coordinator data |
| `number.py` | Writable numeric entities (POST to REST API) |
| `select.py` | Writable select entities (POST to REST API) |
| `config_flow.py` | Two-step flow: IP input → device confirmation |
