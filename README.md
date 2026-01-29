# MHO-H411 CO2 Monitor (Home Assistant + HACS)

Vibe coded Home Assistant integration for the **MHO-H411** Bluetooth temperature/humidity/CO₂ sensor.

- UI setup (no `configuration.yaml`)  
- Automatic discovery
- Works with ESPHome Bluetooth Proxies

## Entities
- Temperature (°C)
- Humidity (%)
- CO₂ (ppm) *(may be `unknown` when sensor disables CO₂ reporting)*
- Battery (%)
- Voltage (V)

## Requirements
- Home Assistant with Bluetooth enabled (local adapter or ESPHome Bluetooth proxy)

### ESPHome Bluetooth proxy example
```yaml
esp32_ble_tracker:

bluetooth_proxy:
  active: true
```

## Installation (HACS)
1. In HACS, add this repository as a **Custom repository** (category: *Integration*).
2. Install it.
3. Restart Home Assistant.
4. Go to **Settings → Devices & services**, **Add integration** and look for "MHO-H411 CO2 Monitor"

## Options
After adding the device, open the integration entry → **Options** to set the polling interval.

## Notes / troubleshooting
- The sensor can only handle one active BLE connection at a time. If your phone/app is connected, Home Assistant may not be able to read it.

## Credits
The payload format and UUIDs were derived from `elsemieni/elsemieni-mho-h411`
