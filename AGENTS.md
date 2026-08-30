# AGENT.md

This file is the global entrypoint for AI coding agents working in this repository.

## Goal

Provide comprehensive guidance for AI agents working on the `zendure-local-ha` integration.
Use this file for shared rules and cross-cutting concerns. Use `.github/agents/*.agent.md` for domain-specific guidance.

## Project Snapshot

- **Project**: `zendure-local-ha`
- **Type**: Home Assistant custom integration (HACS-compatible)
- **Domain**: `zendure_local`
- **Device family**: Zendure SolarFlow hub-based devices (e.g., SolarFlow 800 Pro2)
- **Runtime model**: 100% local REST polling every 30 seconds
- **Constraints**: No cloud dependency, no MQTT, no webhooks
- **Minimum HA version**: 2026.4
- **Python**: 3.12+
- **Repository**: https://github.com/fryoll/zendure-local-ha

## Architecture Overview

```mermaid
graph TD
    A[__init__.py] --> B[ZendureCoordinator]
    B --> C[sensor.py]
    B --> D[number.py]
    B --> E[select.py]
    B --> F[config_flow.py]
    B -.->|REST API| G[/properties/report & /properties/write]
```

### Data Flow

1. **Entry setup**: `__init__.py` creates `ZendureCoordinator`, stores in `entry.runtime_data`, forwards platform setup
2. **Polling**: Coordinator polls `/properties/report` every 30s, normalizes via `_normalize_data()`, stores flat dict in `coordinator.data`
3. **Read entities**: Platforms read from coordinator data using `value_key` or `value_fn` strategies
4. **Write operations**: Writable entities call `coordinator.async_write_property(key, value)` → POST to `/properties/write`

### Normalization Layer (`_normalize_data()`)

Transforms raw device payloads into flat dicts:
- Strips `properties` wrapper if present (some firmwares return flat root)
- Flattens `packData` array → `pack0_soc`, `pack1_soc` keys (max 2 packs)
- Aliases `socLevel` → `electricLevel` when only `socLevel` present

### Energy Integration (`ZendureEnergySensor`)

- Extends `RestoreSensor` (not `SensorEntity`) for state persistence across restarts
- Accumulates kWh via trapezoidal rule in `_handle_coordinator_update()`
- Requires power readings from device payload

### Percent Scale Detection (`_detect_percent_scale()`)

Handles firmware variations reporting percent-like values as ×1, ×10, or ×100:
- Used by `ZendureSensor` and `ZendureNumberDescription`
- Infers multiplier from raw values, divides accordingly

## Project Snapshot

- **Project**: `zendure-local-ha`
- **Type**: Home Assistant custom integration
- **Domain**: `zendure_local`
- **Device family**: Zendure SolarFlow hub-based devices (e.g., SolarFlow 800 Pro2)
- **Runtime model**: local REST polling every 30 seconds
- **Constraints**: no cloud dependency, no MQTT, no webhooks, HACS-compatible
- **Stack**: Python 3.12+, Home Assistant 2026.4+, pytest, GitHub Actions
- **Repository**: https://github.com/fryoll/zendure-local-ha

## Global Rules

### Core Principles

1. **Local-first architecture**: Zero cloud dependency, no webhooks, no MQTT — pure REST polling
2. **Coordinator as single source of truth**: All device I/O routes through `ZendureCoordinator`
3. **Async-first**: All operations must be async-compatible with Home Assistant event loop
4. **Test coverage**: Add/update tests for all behavior changes (target: 95%+ coverage)
5. **String synchronization**: User-facing strings in `strings.json`, `translations/en.json`, `translations/fr.json`
6. **Conventional Commits**: Enforced by pre-commit hooks (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`)
7. **HACS compatibility**: Follow HACS repository structure and packaging guidelines

### Code Quality Standards

8. **Type hints**: Use type annotations for all functions and methods
9. **Error handling**: Proper exception handling with informative messages
10. **Documentation**: Docstrings for all public APIs, inline comments for complex logic
11. **Logging**: Use `logging` module instead of `print()` statements
12. **Async/await**: Avoid blocking operations in async code

## Agent Routing

### Primary Agents (in `.github/agents/`)

| Agent | Use For |
|-------|---------|
| `integration-dev.agent.md` | Entities, coordinator, config flow, translations, integration behavior |
| `tests-review.agent.md` | Test additions, regression analysis, code review |
| `ci-release.agent.md` | GitHub Actions, release automation, packaging, repo hygiene |
| `docs-maintainer.agent.md` | README, CONTRIBUTING, badges, release notes, public-repo polish |

### Fallback Agent

| Agent | Use For |
|-------|---------|
| `zendure-local.agent.md` | General-purpose tasks spanning multiple areas |

**Routing Priority**: 
1. Try to match task to specific agent first
2. If no clear match, use `zendure-local.agent.md` as fallback
3. Document routing decisions in commit messages for transparency

## Shared Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements_test.txt

# Run all tests
pytest

# Run tests with coverage
pytest --cov

# Run a specific test file
pytest tests/test_coordinator.py

# Run a specific test by name
pytest tests/test_coordinator.py::test_normalize_flattens_pack_data
```

## Key Architecture Notes

- **Data flow**: `__init__.py` → `ZendureCoordinator` → platforms (`sensor`, `number`, `select`)
- **Normalization**: `_normalize_data()` in `coordinator.py` transforms raw device payloads into flat dicts
- **Writable entities**: Use `coordinator.async_write_property(key, value)` for POST operations
- **Energy sensors**: `ZendureEnergySensor` extends `RestoreSensor` for state persistence across restarts
- **Percent scaling**: `_detect_percent_scale()` handles firmware variations (×1, ×10, ×100)

## Key Architecture Notes

- **Data flow**: `__init__.py` → `ZendureCoordinator` → platforms (`sensor`, `number`, `select`)
- **Normalization**: `_normalize_data()` in `coordinator.py` transforms raw device payloads into flat dicts
- **Writable entities**: Use `coordinator.async_write_property(key, value)` for POST operations
- **Energy sensors**: `ZendureEnergySensor` extends `RestoreSensor` for state persistence across restarts
- **Percent scaling**: `_detect_percent_scale()` handles firmware variations (×1, ×10, ×100)

## File Structure

```
custom_components/zendure_local/
├── __init__.py          # Entry setup and platform forwarding
├── coordinator.py       # REST polling, normalization, writes
├── sensor.py            # Read-only entities and energy integration
├── number.py            # Writable numeric controls
├── select.py            # Writable select controls
├── config_flow.py       # IP-based discovery and confirmation
├── const.py             # Domain constants, endpoints, entity keys
├── entity.py            # Base entity classes
├── utils.py             # Shared utilities
├── manifest.json        # Integration metadata
├── strings.json         # Default UI strings
└── translations/        # Localized strings (en.json, fr.json)
```

## Testing Strategy

- **Framework**: pytest with `pytest-homeassistant-custom-component`
- **Fixtures**: `mock_coordinator` (unit tests), `real_coordinator` (integration tests with `aioclient_mock`)
- **Coverage target**: 95%+ (enforced in CI)
- **Test organization**: One test file per module (`test_coordinator.py`, `test_sensor.py`, etc.)

## Commit Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/), enforced by pre-commit hooks:

| Prefix | When to use |
|--------|-------------|
| `feat:` | New sensor, control, or user-visible behavior |
| `fix:` | Bug fix |
| `chore:` | CI, dependencies, tooling |
| `docs:` | README, CONTRIBUTING, docstrings |
| `refactor:` | Code restructuring with no behavior change |

Examples:
```
feat(sensor): add battery temperature sensor
fix(coordinator): handle timeout on local API
chore(ci): bump pytest version
```

## Versioning

- **Release automation**: release-please manages CHANGELOG and version bumps
- **Version location**: `custom_components/zendure_local/manifest.json`
- **Changelog**: `CHANGELOG.md` (auto-generated)
