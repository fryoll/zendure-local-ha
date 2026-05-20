# Battery Temperature Sensors Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add two read-only temperature sensors (`pack0_temp`, `pack1_temp`) that surface the `maxTemp` field from the device's `packData` array, divided by 10 to convert from tenths of °C to °C.

**Architecture:** Normalization happens in `_normalize_data()` (coordinator.py) so sensor entities stay simple `value_key` lookups with no custom `value_fn`. Tests follow TDD: write failing test → implement → verify passing → commit.

**Tech Stack:** Python 3.12, pytest, pytest-homeassistant-custom-component, Home Assistant sensor platform.

---

## File Map

| Action | File |
|--------|------|
| Modify | `custom_components/zendure_local/coordinator.py` |
| Modify | `custom_components/zendure_local/sensor.py` |
| Modify | `custom_components/zendure_local/translations/en.json` |
| Modify | `custom_components/zendure_local/translations/fr.json` |
| Modify | `tests/conftest.py` |
| Modify | `tests/test_coordinator.py` |
| Modify | `tests/test_sensor.py` |

---

### Task 1: Normalize `maxTemp` in the coordinator

**Files:**
- Modify: `custom_components/zendure_local/coordinator.py:98-113`
- Modify: `tests/conftest.py`
- Modify: `tests/test_coordinator.py`

- [ ] **Step 1: Write the failing tests**

Open `tests/test_coordinator.py` and add these two tests at the end of the `_normalize_data` section (after `test_normalize_pack_missing_soclevel_skipped`):

```python
def test_normalize_flattens_pack_temp():
    raw = {
        "properties": {
            "packData": [{"maxTemp": 250}, {"maxTemp": 260}],
        }
    }
    result = _normalize_data(raw)
    assert result["pack0_temp"] == 25.0
    assert result["pack1_temp"] == 26.0


def test_normalize_pack_missing_maxtemp_skipped():
    raw = {"properties": {"packData": [{"socLevel": 74}]}}
    result = _normalize_data(raw)
    assert "pack0_temp" not in result
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_coordinator.py::test_normalize_flattens_pack_temp tests/test_coordinator.py::test_normalize_pack_missing_maxtemp_skipped -v
```

Expected: 2 FAILED — `AssertionError: assert 'pack0_temp' not in result` (key doesn't exist yet).

- [ ] **Step 3: Implement the normalization**

In `coordinator.py`, find the `_normalize_data` function. The `packData` loop currently reads:

```python
for i, pack in enumerate(properties.get("packData", [])[:2]):
    soc = pack.get("socLevel")
    if soc is not None:
        data[f"pack{i}_soc"] = soc
```

Replace it with:

```python
for i, pack in enumerate(properties.get("packData", [])[:2]):
    if (soc := pack.get("socLevel")) is not None:
        data[f"pack{i}_soc"] = soc
    if (temp := pack.get("maxTemp")) is not None:
        data[f"pack{i}_temp"] = temp / 10.0
```

- [ ] **Step 4: Run the new tests to verify they pass**

```bash
pytest tests/test_coordinator.py::test_normalize_flattens_pack_temp tests/test_coordinator.py::test_normalize_pack_missing_maxtemp_skipped -v
```

Expected: 2 PASSED.

- [ ] **Step 5: Update the shared mock data in `conftest.py`**

In `tests/conftest.py`, update `MOCK_PROPERTIES` — the `packData` entries need `maxTemp`:

```python
"packData": [
    {"socLevel": 74, "maxTemp": 250},
    {"socLevel": 76, "maxTemp": 260},
],
```

Add two entries to `MOCK_NORMALIZED` (keep the existing keys, add at the end):

```python
"pack0_temp": 25.0,
"pack1_temp": 26.0,
```

- [ ] **Step 6: Run all coordinator tests to verify nothing is broken**

```bash
pytest tests/test_coordinator.py -v
```

Expected: all tests PASS (the `test_normalize_full_response` test validates `MOCK_NORMALIZED` against `MOCK_RESPONSE`, so it will catch any mismatch).

- [ ] **Step 7: Commit**

```bash
git add custom_components/zendure_local/coordinator.py tests/conftest.py tests/test_coordinator.py
git commit -m "feat(coordinator): extract pack maxTemp into pack0_temp / pack1_temp"
```

---

### Task 2: Add temperature sensor entities

**Files:**
- Modify: `custom_components/zendure_local/sensor.py`
- Modify: `tests/test_sensor.py`

- [ ] **Step 1: Write the failing tests**

Open `tests/test_sensor.py`. Add these imports at the top if not already present:

```python
from custom_components.zendure_local.sensor import BATTERY_SENSORS, ZendureSensor
```

Then add the three new tests at the end of the file:

```python
def test_pack0_temp_value(mock_coordinator):
    desc = next(d for d in BATTERY_SENSORS if d.key == "pack0_temp")
    sensor = ZendureSensor(mock_coordinator, desc)
    assert sensor.native_value == 25.0


def test_pack1_temp_value(mock_coordinator):
    desc = next(d for d in BATTERY_SENSORS if d.key == "pack1_temp")
    sensor = ZendureSensor(mock_coordinator, desc)
    assert sensor.native_value == 26.0


def test_pack_temp_unavailable_when_key_missing(mock_coordinator):
    mock_coordinator.data = {}
    desc = next(d for d in BATTERY_SENSORS if d.key == "pack0_temp")
    sensor = ZendureSensor(mock_coordinator, desc)
    assert not sensor.available
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_sensor.py::test_pack0_temp_value tests/test_sensor.py::test_pack1_temp_value tests/test_sensor.py::test_pack_temp_unavailable_when_key_missing -v
```

Expected: 3 FAILED — `StopIteration` because `pack0_temp` doesn't exist in `BATTERY_SENSORS` yet.

- [ ] **Step 3: Add the import for `UnitOfTemperature`**

In `sensor.py`, find this line:

```python
from homeassistant.const import PERCENTAGE, UnitOfEnergy, UnitOfPower
```

Replace it with:

```python
from homeassistant.const import PERCENTAGE, UnitOfEnergy, UnitOfPower, UnitOfTemperature
```

- [ ] **Step 4: Add the two sensor descriptions**

In `sensor.py`, find `BATTERY_SENSORS` and append the two new descriptions inside the tuple (before the closing parenthesis):

```python
    ZendureSensorDescription(
        key="pack0_temp",
        translation_key="pack0_temp",
        value_key="pack0_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
    ),
    ZendureSensorDescription(
        key="pack1_temp",
        translation_key="pack1_temp",
        value_key="pack1_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
    ),
```

- [ ] **Step 5: Run the new tests to verify they pass**

```bash
pytest tests/test_sensor.py::test_pack0_temp_value tests/test_sensor.py::test_pack1_temp_value tests/test_sensor.py::test_pack_temp_unavailable_when_key_missing -v
```

Expected: 3 PASSED.

- [ ] **Step 6: Run all sensor tests**

```bash
pytest tests/test_sensor.py -v
```

Expected: all tests PASS.

- [ ] **Step 7: Commit**

```bash
git add custom_components/zendure_local/sensor.py tests/test_sensor.py
git commit -m "feat(sensor): add pack0_temp and pack1_temp temperature sensors"
```

---

### Task 3: Add translations

**Files:**
- Modify: `custom_components/zendure_local/translations/en.json`
- Modify: `custom_components/zendure_local/translations/fr.json`

- [ ] **Step 1: Update `en.json`**

In `translations/en.json`, find the `entity.sensor` object. Add after `"pack1_soc"`:

```json
"pack0_temp": { "name": "Pack 1 Temperature" },
"pack1_temp": { "name": "Pack 2 Temperature" },
```

The sensor block should look like:

```json
"electric_level": { "name": "Battery State of Charge" },
"pack0_soc": { "name": "Pack 1 State of Charge" },
"pack1_soc": { "name": "Pack 2 State of Charge" },
"pack0_temp": { "name": "Pack 1 Temperature" },
"pack1_temp": { "name": "Pack 2 Temperature" },
```

- [ ] **Step 2: Update `fr.json`**

In `translations/fr.json`, find the `entity.sensor` object. Add after `"pack1_soc"`:

```json
"pack0_temp": { "name": "Température pack 1" },
"pack1_temp": { "name": "Température pack 2" },
```

- [ ] **Step 3: Validate JSON syntax**

```bash
python3 -c "import json; json.load(open('custom_components/zendure_local/translations/en.json')); json.load(open('custom_components/zendure_local/translations/fr.json')); print('JSON valid')"
```

Expected: `JSON valid`

- [ ] **Step 4: Run full test suite**

```bash
pytest -v
```

Expected: all tests PASS, 0 failures.

- [ ] **Step 5: Commit**

```bash
git add custom_components/zendure_local/translations/en.json custom_components/zendure_local/translations/fr.json
git commit -m "feat(translations): add pack temperature sensor names (en + fr)"
```
