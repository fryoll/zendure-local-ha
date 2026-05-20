# Battery Temperature Sensors — Design Spec

**Date:** 2026-05-20
**Status:** Approved

## Goal

Add two read-only temperature sensors to the integration — one per battery pack — surfacing the `maxTemp` field already present in the device's `packData` array.

## Scope

- Add `pack0_temp` and `pack1_temp` to `coordinator.data`
- Add two `ZendureSensorDescription` entries to `BATTERY_SENSORS`
- Add translations (en + fr)
- Update test fixtures and add new tests

Out of scope: voltage sensors, generic packData refactor.

## Data Source

The device exposes `maxTemp` inside each `packData` entry in `GET /properties/report`. The value is in tenths of degrees Celsius (e.g. `250` = 25.0 °C). The field may be absent if the pack is not present.

## Coordinator (`coordinator.py`)

In `_normalize_data()`, extend the existing `packData` loop:

```python
for i, pack in enumerate(properties.get("packData", [])[:2]):
    if (soc := pack.get("socLevel")) is not None:
        data[f"pack{i}_soc"] = soc
    if (temp := pack.get("maxTemp")) is not None:
        data[f"pack{i}_temp"] = temp / 10.0
```

Result: `pack0_temp` and `pack1_temp` are floats in °C, present only when the device reports them.

## Sensor (`sensor.py`)

Add `UnitOfTemperature` to the import from `homeassistant.const`.

Append to `BATTERY_SENSORS`:

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

No `value_fn` needed — the division by 10 is done at normalization time.

## Translations

**`translations/en.json`** — add under `entity.sensor`:
```json
"pack0_temp": { "name": "Pack 1 Temperature" },
"pack1_temp": { "name": "Pack 2 Temperature" }
```

**`translations/fr.json`** — add under `entity.sensor`:
```json
"pack0_temp": { "name": "Température pack 1" },
"pack1_temp": { "name": "Température pack 2" }
```

## Tests

### `conftest.py`

Update `MOCK_PROPERTIES.packData` to include `maxTemp`:
```python
"packData": [
    {"socLevel": 74, "maxTemp": 250},
    {"socLevel": 76, "maxTemp": 260},
],
```

Add to `MOCK_NORMALIZED`:
```python
"pack0_temp": 25.0,
"pack1_temp": 26.0,
```

### `test_coordinator.py`

```python
def test_normalize_flattens_pack_temp():
    raw = {"properties": {"packData": [{"maxTemp": 250}, {"maxTemp": 260}]}}
    result = _normalize_data(raw)
    assert result["pack0_temp"] == 25.0
    assert result["pack1_temp"] == 26.0

def test_normalize_pack_missing_maxtemp_skipped():
    raw = {"properties": {"packData": [{"socLevel": 74}]}}
    result = _normalize_data(raw)
    assert "pack0_temp" not in result
```

### `test_sensor.py`

```python
def test_pack0_temp_value(mock_coordinator):
    desc = next(d for d in BATTERY_SENSORS if d.key == "pack0_temp")
    sensor = ZendureSensor(mock_coordinator, desc)
    assert sensor.native_value == 25.0

def test_pack1_temp_value(mock_coordinator):
    desc = next(d for d in BATTERY_SENSORS if d.key == "pack1_temp")
    sensor = ZendureSensor(mock_coordinator, desc)
    assert sensor.native_value == 26.0

def test_pack0_temp_unavailable_when_missing(mock_coordinator):
    mock_coordinator.data = {}
    desc = next(d for d in BATTERY_SENSORS if d.key == "pack0_temp")
    sensor = ZendureSensor(mock_coordinator, desc)
    assert not sensor.available
```

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
