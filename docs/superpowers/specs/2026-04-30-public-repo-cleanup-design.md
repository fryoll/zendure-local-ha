# Design — Public repo cleanup (full polish)

**Date:** 2026-04-30  
**Status:** Approved

## Goal

Prepare `zendure-local-ha` for publication as a public GitHub repository. The repo is already
functionally solid (97% test coverage, no secrets, complete translations). This spec covers the
remaining gaps: a missing licence file, no CI pipeline, one code duplication, no contributor
guide, and no README badges.

---

## 1. Code quality — deduplicate `_detect_percent_scale()`

**Problem:** `_detect_percent_scale()` is copy-pasted identically in `sensor.py` and `number.py`.

**Change:**

- Create `custom_components/zendure_local/utils.py` containing the single shared function.
- Update `sensor.py` and `number.py` to import it from `utils`.
- No logic change — move only.

```python
# utils.py
def detect_percent_scale(data: dict, keys: tuple[str, ...]) -> int:
    """Infer whether percent-like values are reported as ×1, ×10, or ×100."""
    raw_values = [data.get(key) for key in keys if data.get(key) is not None]
    if any(float(v) > 1000 for v in raw_values):
        return 100
    if any(float(v) > 100 for v in raw_values):
        return 10
    return 1
```

The function is pure and stateless, so no fixture or mock change is needed in tests.

---

## 2. Licence

- Add `LICENSE` at the repository root — MIT licence, copyright `ylascaux`, year 2026.
- No other file changes needed (README already states "MIT").

---

## 3. CI pipeline

### 3a. New workflow — `ci.yml`

File: `.github/workflows/ci.yml`

Triggers:
- `push` to `main`
- `pull_request` targeting `main`

Steps:
1. `actions/checkout@v4`
2. `actions/setup-python@v5` with `python-version: "3.12"`
3. `pip install -r requirements_test.txt`
4. `pytest --cov --cov-fail-under=95`

Purpose: fast feedback on every push and PR. Fails if tests break or coverage drops below 95%
(current coverage is 97%, giving a 2-point buffer).

### 3b. Update `release.yml` — tests block publish

Add a `test` job (same steps as `ci.yml`) at the top of `release.yml`.

Update the `publish` job's `needs` from `[release-please]` to `[release-please, test]`.

The `release-please` job runs in parallel with `test` (it does not depend on tests — it only
manages the release PR). `publish` is gated on both: it only runs if a release was created AND
tests passed.

Flow:
```
push to main
  ├── test ──────────────────────────┐
  └── release-please (PR/tag only) ──┤
                                     └── publish (only if release_created AND test passed)
```

---

## 4. CONTRIBUTING.md

File: `CONTRIBUTING.md` at repository root.

Content (short and practical):

- **Prerequisites:** Python 3.12+, a virtual environment
- **Setup:** `pip install -r requirements_test.txt` + `pre-commit install --hook-type commit-msg`
- **Running tests:** `pytest`, single file, single test by name, coverage
- **Commit format:** Conventional Commits (`feat:`, `fix:`, `chore:`, etc.) — enforced by
  commitizen pre-commit hook; examples included
- **Pull requests:** all tests must pass; CI runs automatically on PR open/push

No code-of-conduct or issue templates for now.

---

## 5. README badges

Add three badges immediately below the H1 title in `README.md`:

| Badge | Source |
|-------|--------|
| CI | GitHub Actions status for `ci.yml` on `main` |
| License | Static MIT shield |
| HACS | `hacs.xyz` custom-repository badge |

---

## Out of scope

- Type hint audit (code is already well-typed)
- Issue / PR templates
- Code of conduct
- Changelog edits (managed by release-please)
