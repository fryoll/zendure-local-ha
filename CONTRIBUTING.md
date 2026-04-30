# Contributing

## Prerequisites

- Python 3.12+

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements_test.txt
pre-commit install --hook-type commit-msg
```

## Running tests

```bash
# All tests
pytest

# Single file
pytest tests/test_coordinator.py

# Single test by name
pytest tests/test_coordinator.py::test_normalize_flattens_pack_data

# With coverage report (matches the CI threshold)
pytest --cov --cov-fail-under=95
```

## Commit format

This project uses [Conventional Commits](https://www.conventionalcommits.org/), enforced automatically by the pre-commit hook installed above.

| Prefix | When to use |
|--------|-------------|
| `feat:` | New sensor, control, or user-visible behaviour |
| `fix:` | Bug fix |
| `chore:` | CI, dependencies, tooling |
| `docs:` | README, CONTRIBUTING, docstrings |
| `refactor:` | Code restructuring with no behaviour change |

Examples:

```
feat(sensor): add battery temperature sensor
fix(coordinator): handle timeout on local API
chore(ci): bump pytest version
```

## Pull requests

1. Fork the repo and create a branch from `main`.
2. Add or update tests for any changed behaviour.
3. Run `pytest` — all tests must pass.
4. Open a PR. CI runs automatically and must pass before merge.
