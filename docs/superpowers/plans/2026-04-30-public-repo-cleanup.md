# Public Repo Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `zendure-local-ha` ready for public release by adding a licence, a CI pipeline that blocks releases, fixing one code duplication, a contributor guide, and README badges.

**Architecture:** Independent parallel tracks — code quality (utils extraction), legal (LICENSE), CI (two workflow files), docs (CONTRIBUTING.md + README badges). Tasks are ordered by dependency: utils first (other tests depend on it passing), then CI, then docs.

**Tech Stack:** Python 3.12, pytest, pytest-homeassistant-custom-component, GitHub Actions, shields.io badges.

---

## File Map

| Action | File |
|--------|------|
| Create | `custom_components/zendure_local/utils.py` |
| Create | `tests/test_utils.py` |
| Modify | `custom_components/zendure_local/sensor.py` |
| Modify | `custom_components/zendure_local/number.py` |
| Create | `LICENSE` |
| Create | `.github/workflows/ci.yml` |
| Modify | `.github/workflows/release.yml` |
| Create | `CONTRIBUTING.md` |
| Modify | `README.md` |

---

### Task 1: Extract `detect_percent_scale` into `utils.py`

**Files:**
- Create: `custom_components/zendure_local/utils.py`
- Create: `tests/test_utils.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_utils.py`:

```python
"""Unit tests for shared utilities."""
import pytest

from custom_components.zendure_local.utils import detect_percent_scale


def test_scale_1_when_all_values_under_100():
    assert detect_percent_scale({"minSoc": 50, "socSet": 80}, ("minSoc", "socSet")) == 1


def test_scale_10_when_values_between_100_and_1000():
    assert detect_percent_scale({"minSoc": 100, "socSet": 900}, ("minSoc", "socSet")) == 10


def test_scale_100_when_values_over_1000():
    assert detect_percent_scale({"minSoc": 1000, "socSet": 9000}, ("minSoc", "socSet")) == 100


def test_missing_key_is_ignored():
    # Only minSoc is present — should still work
    assert detect_percent_scale({"minSoc": 50}, ("minSoc", "socSet")) == 1


def test_all_keys_missing_returns_1():
    assert detect_percent_scale({}, ("minSoc", "socSet")) == 1


def test_boundary_value_101_returns_scale_10():
    assert detect_percent_scale({"minSoc": 101}, ("minSoc",)) == 10


def test_boundary_value_1001_returns_scale_100():
    assert detect_percent_scale({"minSoc": 1001}, ("minSoc",)) == 100
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_utils.py -v
```

Expected: `ModuleNotFoundError` or `ImportError` — `utils.py` does not exist yet.

- [ ] **Step 3: Create `utils.py`**

Create `custom_components/zendure_local/utils.py`:

```python
"""Shared utilities for the Zendure Local integration."""


def detect_percent_scale(data: dict, keys: tuple[str, ...]) -> int:
    """Infer whether percent-like values are reported as ×1, ×10, or ×100."""
    raw_values = [data.get(key) for key in keys if data.get(key) is not None]
    if any(float(v) > 1000 for v in raw_values):
        return 100
    if any(float(v) > 100 for v in raw_values):
        return 10
    return 1
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_utils.py -v
```

Expected: 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add custom_components/zendure_local/utils.py tests/test_utils.py
git commit -m "feat: extract detect_percent_scale into shared utils module"
```

---

### Task 2: Update `sensor.py` and `number.py` to use `utils.detect_percent_scale`

**Files:**
- Modify: `custom_components/zendure_local/sensor.py`
- Modify: `custom_components/zendure_local/number.py`

- [ ] **Step 1: Update `sensor.py`**

In `sensor.py`, replace the import block at the top (after the existing imports) by adding:

```python
from .utils import detect_percent_scale
```

Then delete the entire `_detect_percent_scale` function (lines 30–38):

```python
# DELETE this function:
def _detect_percent_scale(data: dict, keys: tuple[str, ...]) -> int:
    """Detect whether the selected percent-like values are reported as x1, x10, or x100."""
    raw_values = [data.get(key) for key in keys if data.get(key) is not None]

    if any(float(value) > 1000 for value in raw_values):
        return 100
    if any(float(value) > 100 for value in raw_values):
        return 10
    return 1
```

Update `_normalize_percent_value` to call the imported function instead:

```python
def _normalize_percent_value(
    data: dict, value: StateType, keys: tuple[str, ...]
) -> StateType:
    """Normalize a raw percent-like value to the 0-100 HA range."""
    if value is None:
        return None
    scale = detect_percent_scale(data, keys)
    if scale > 1:
        return float(value) / scale
    return value
```

- [ ] **Step 2: Update `number.py`**

In `number.py`, add after the existing imports:

```python
from .utils import detect_percent_scale
```

Delete the entire `_detect_percent_scale` function (lines 24–31):

```python
# DELETE this function:
def _detect_percent_scale(data: dict, keys: tuple[str, ...]) -> int:
    """Detect whether the selected percent-like values are reported as x1, x10, or x100."""
    raw_values = [data.get(key) for key in keys if data.get(key) is not None]

    if any(float(value) > 1000 for value in raw_values):
        return 100
    if any(float(value) > 100 for value in raw_values):
        return 10
    return 1
```

Update `_percent_scale` inside `ZendureNumber` to call the imported function:

```python
def _percent_scale(self) -> int:
    """Return the currently detected scale for percent-like values."""
    if self.entity_description.device_scale <= 1:
        return 1
    return detect_percent_scale(
        self.coordinator.data or {},
        ("minSoc", "socSet"),
    )
```

- [ ] **Step 3: Run all tests**

```bash
pytest -v
```

Expected: all 89 existing tests + 7 new utils tests = **96 tests PASS**, 0 failures.

- [ ] **Step 4: Commit**

```bash
git add custom_components/zendure_local/sensor.py custom_components/zendure_local/number.py
git commit -m "refactor: replace duplicated _detect_percent_scale with shared utils.detect_percent_scale"
```

---

### Task 3: Add `LICENSE` file

**Files:**
- Create: `LICENSE`

- [ ] **Step 1: Create the MIT licence file**

Create `LICENSE` at the repository root:

```
MIT License

Copyright (c) 2026 ylascaux

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 2: Commit**

```bash
git add LICENSE
git commit -m "chore: add MIT licence"
```

---

### Task 4: Create CI workflow

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Create `ci.yml`**

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -r requirements_test.txt

      - name: Run tests
        run: pytest --cov --cov-fail-under=95
```

- [ ] **Step 2: Verify syntax locally**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))" && echo "YAML valid"
```

Expected: `YAML valid`

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "chore(ci): add CI workflow to run tests on push and PR"
```

---

### Task 5: Gate release publish on tests

**Files:**
- Modify: `.github/workflows/release.yml`

- [ ] **Step 1: Replace `release.yml` with the gated version**

The full new content of `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    branches:
      - main

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -r requirements_test.txt

      - name: Run tests
        run: pytest --cov --cov-fail-under=95

  release-please:
    runs-on: ubuntu-latest
    outputs:
      release_created: ${{ steps.release.outputs.release_created }}
      tag_name: ${{ steps.release.outputs.tag_name }}
    steps:
      - uses: googleapis/release-please-action@v5
        id: release
        with:
          config-file: release-please-config.json
          manifest-file: .release-please-manifest.json

  publish:
    runs-on: ubuntu-latest
    needs: [release-please, test]
    if: needs.release-please.outputs.release_created == 'true'
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ needs.release-please.outputs.tag_name }}

      - name: Create HACS release zip
        run: |
          mkdir -p dist
          zip -r dist/zendure_local.zip custom_components/zendure_local/ -x '*/__pycache__/*' '*.pyc' '*.pyo'

      - name: Upload zip to GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          tag_name: ${{ needs.release-please.outputs.tag_name }}
          files: dist/zendure_local.zip
```

- [ ] **Step 2: Verify syntax locally**

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml'))" && echo "YAML valid"
```

Expected: `YAML valid`

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/release.yml
git commit -m "chore(ci): gate publish on tests passing"
```

---

### Task 6: Create `CONTRIBUTING.md`

**Files:**
- Create: `CONTRIBUTING.md`

- [ ] **Step 1: Create the file**

Create `CONTRIBUTING.md` at the repository root:

```markdown
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

# With coverage report
pytest --cov
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
```

- [ ] **Step 2: Commit**

```bash
git add CONTRIBUTING.md
git commit -m "docs: add CONTRIBUTING guide"
```

---

### Task 7: Add badges to `README.md`

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add badges below the H1 title**

Open `README.md`. After the first line (`# Zendure Local — Home Assistant Integration`), insert the following block (before the description paragraph):

```markdown
[![CI](https://github.com/fryoll/zendure-local-ha/actions/workflows/ci.yml/badge.svg)](https://github.com/fryoll/zendure-local-ha/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
```

The top of the file should look like:

```markdown
# Zendure Local — Home Assistant Integration

[![CI](https://github.com/fryoll/zendure-local-ha/actions/workflows/ci.yml/badge.svg)](https://github.com/fryoll/zendure-local-ha/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)

100 % local integration for the **Zendure SolarFlow 800 Pro2**...
```

- [ ] **Step 2: Run tests one final time to confirm nothing is broken**

```bash
pytest --cov --cov-fail-under=95
```

Expected: **96 tests PASS**, coverage ≥ 95%.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add CI, licence, and HACS badges to README"
```
