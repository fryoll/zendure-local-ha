# Zendure Local — Home Assistant Integration

100 % local integration for the **Zendure SolarFlow 800 Pro2** (and compatible hub-based devices).  
No cloud, no MQTT — pure REST HTTP polling every 30 seconds.

---

## Requirements

| Item | Minimum version |
|------|----------------|
| Home Assistant | 2026.4 |
| Python | 3.12 |
| Device firmware | any with local REST API enabled |

---

## Installation

### Manual

1. Download or clone this repository.
2. Copy the `custom_components/zendure_local/` folder into your HA config directory:
   ```
   <config>/custom_components/zendure_local/
   ```
3. Restart Home Assistant.
4. Go to **Settings → Devices & Services → Add Integration** and search for **Zendure Local**.

### Via HACS (custom repository)

> Requires [HACS](https://hacs.xyz) to be installed in your Home Assistant instance.

1. In HA, open **HACS → Integrations**.
2. Click the three-dot menu (top-right) → **Custom repositories**.
3. Fill in:
   - **Repository**: `https://github.com/TON_USERNAME/zendure-local-ha`
   - **Category**: Integration
4. Click **Add**, then close the dialog.
5. Search for **Zendure Local** in the HACS Integrations list and click **Download**.
6. Restart Home Assistant.
7. Go to **Settings → Devices & Services → Add Integration** and search for **Zendure Local**.

---

## Configuration

The integration uses a UI config flow — no YAML required.

**Step 1 — IP address**  
Enter the local IPv4 address of your SolarFlow hub (e.g. `192.168.1.100`).  
The integration validates the format and opens a test connection.

**Step 2 — Confirmation**  
If the device responds, its serial number is displayed. Click **Submit** to create the entry.

**Reconfigure**  
To change the IP after installation: open the integration card → three-dot menu → **Reconfigure**.

---

## Entities

All entities are grouped under a single HA device named **SolarFlow 800 Pro2**, identified by the device serial number.

### Sensors — power (W)

| Entity ID | Description |
|-----------|-------------|
| `sensor.solarflow_800_pro2_solar_input_power` | Total solar input power |
| `sensor.solarflow_800_pro2_solar_power_mppt_1` | Solar power MPPT channel 1 |
| `sensor.solarflow_800_pro2_solar_power_mppt_2` | Solar power MPPT channel 2 |
| `sensor.solarflow_800_pro2_solar_power_mppt_3` | Solar power MPPT channel 3 |
| `sensor.solarflow_800_pro2_solar_power_mppt_4` | Solar power MPPT channel 4 |
| `sensor.solarflow_800_pro2_battery_charge_power` | Battery charge power |
| `sensor.solarflow_800_pro2_battery_discharge_power` | Battery discharge power |
| `sensor.solarflow_800_pro2_home_output_power` | Power injected to home |
| `sensor.solarflow_800_pro2_grid_input_power` | Power drawn from the grid |

### Sensors — battery (%)

| Entity ID | Description |
|-----------|-------------|
| `sensor.solarflow_800_pro2_battery_state_of_charge` | Main battery SOC |
| `sensor.solarflow_800_pro2_pack_1_state_of_charge` | Pack 1 SOC (if present) |
| `sensor.solarflow_800_pro2_pack_2_state_of_charge` | Pack 2 SOC (if present) |

### Sensors — energy (kWh) — Energy dashboard ready

These sensors use trapezoidal integration of the power readings and are persisted across HA restarts.

| Entity ID | Energy dashboard slot |
|-----------|-----------------------|
| `sensor.solarflow_800_pro2_solar_energy` | Solar production |
| `sensor.solarflow_800_pro2_battery_charge_energy` | Battery charge (from solar) |
| `sensor.solarflow_800_pro2_battery_discharge_energy` | Battery discharge (to home) |
| `sensor.solarflow_800_pro2_home_output_energy` | Home consumption (return) |
| `sensor.solarflow_800_pro2_grid_input_energy` | Grid consumption |

### Controls

| Entity ID | Type | Range / Options | Description |
|-----------|------|-----------------|-------------|
| `number.solarflow_800_pro2_output_limit` | Number | 0 – 800 W (step 10) | Injection power cap |
| `number.solarflow_800_pro2_minimum_state_of_charge` | Number | 0 – 100 % (step 5) | Deep-discharge protection |
| `number.solarflow_800_pro2_maximum_state_of_charge` | Number | 0 – 100 % (step 5) | Overcharge protection |
| `select.solarflow_800_pro2_ac_mode` | Select | Auto / Grid Charge / Injection | Operating mode |
| `switch.solarflow_800_pro2_injection_enabled` | Switch | ON / OFF | Enable/disable injection (remembers last limit) |

---

## Energy Dashboard

Go to **Settings → Energy** and add:

| Slot | Entity |
|------|--------|
| Solar panels | `sensor.solarflow_800_pro2_solar_energy` |
| Battery charge | `sensor.solarflow_800_pro2_battery_charge_energy` |
| Battery discharge | `sensor.solarflow_800_pro2_battery_discharge_energy` |
| Return to grid / Home | `sensor.solarflow_800_pro2_home_output_energy` |
| Grid consumption | `sensor.solarflow_800_pro2_grid_input_energy` |

---

## Automation examples

### 1 — Off-peak night charging (10 PM → 6 AM)

```yaml
alias: "Zendure — Night charge (off-peak)"
triggers:
  - trigger: time
    at: "22:00:00"
actions:
  - action: select.select_option
    target:
      entity_id: select.solarflow_800_pro2_ac_mode
    data:
      option: grid_charge
  - action: number.set_value
    target:
      entity_id: number.solarflow_800_pro2_output_limit
    data:
      value: 0
```

### 2 — Daytime injection (6 AM → 10 PM)

```yaml
alias: "Zendure — Day injection"
triggers:
  - trigger: time
    at: "06:00:00"
actions:
  - action: select.select_option
    target:
      entity_id: select.solarflow_800_pro2_ac_mode
    data:
      option: injection
  - action: number.set_value
    target:
      entity_id: number.solarflow_800_pro2_output_limit
    data:
      value: 800
```

### 3 — Winter battery protection (SOC-based)

```yaml
alias: "Zendure — Winter battery protection"
triggers:
  - trigger: numeric_state
    entity_id: sensor.solarflow_800_pro2_battery_state_of_charge
    below: 20
  - trigger: numeric_state
    entity_id: sensor.solarflow_800_pro2_battery_state_of_charge
    above: 80
conditions: []
actions:
  - choose:
      - conditions:
          - condition: numeric_state
            entity_id: sensor.solarflow_800_pro2_battery_state_of_charge
            below: 20
        sequence:
          - action: select.select_option
            target:
              entity_id: select.solarflow_800_pro2_ac_mode
            data:
              option: grid_charge
      - conditions:
          - condition: numeric_state
            entity_id: sensor.solarflow_800_pro2_battery_state_of_charge
            above: 80
        sequence:
          - action: select.select_option
            target:
              entity_id: select.solarflow_800_pro2_ac_mode
            data:
              option: injection
```

### 4 — Stop injection on grid outage

```yaml
alias: "Zendure — Stop injection on grid outage"
triggers:
  - trigger: numeric_state
    entity_id: sensor.solarflow_800_pro2_grid_input_power
    below: 1
    for:
      seconds: 30
actions:
  - action: number.set_value
    target:
      entity_id: number.solarflow_800_pro2_output_limit
    data:
      value: 0
```

---

## Development — Commit format (release-please)

This repository uses **Conventional Commits** so that release-please can generate versions and changelogs automatically.

Examples:

- `feat(sensor): add battery health sensor`
- `fix(coordinator): handle timeout on local API`
- `chore(ci): update pytest version`

To install local hooks:

1. `pip install -r requirements_test.txt`
2. `pre-commit install --hook-type commit-msg`

Once installed, each commit message is validated automatically.

---

## Troubleshooting

### Device not found during setup

- Confirm the device is powered on and connected to your LAN.
- Verify the IP with `ping <IP>` from the same network.
- Check that the local REST API is enabled in the Zendure app (some firmware versions require explicit activation).
- Ensure no firewall rule blocks port 80 between HA and the device.

### Entities show "Unavailable"

- HA polls the device every 30 seconds. If the device is unreachable, all entities (except energy sensors) become unavailable.
- Check **Settings → System → Logs** and filter for `zendure_local` to see the specific error.
- A coordinator error is logged as: `Cannot reach Zendure device at <IP>`.

### Energy sensors reset to 0 on HA restart

- Energy values are persisted via HA's `RestoreSensor` mechanism. If they reset, the HA recorder may not have had time to save the state before shutdown. This is rare and only affects the last polling interval.

### Pack 1 / Pack 2 SOC sensors unavailable

- These sensors are only available if the device reports `packData` in its API response. Devices without expansion packs will leave these entities unavailable, which is expected.

### Wrong entity IDs

- Entity IDs are generated by HA from the device name and entity name. If you have renamed the device or entities, IDs may differ. Use **Developer Tools → States** to find the exact IDs.

---

## License

MIT
