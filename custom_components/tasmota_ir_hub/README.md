# Tasmota IR Hub (HACS)

This is a Home Assistant custom integration to work with Tasmota-based IR hub devices.

## Features

- Configure via UI (Config Flow)
- Support for MQTT and HTTP-based command delivery
- Sensor that shows the last received IR code
- Momentary switch to send raw IR codes (or use the `tasmota_ir_hub.send_ir` service)

## Notes

- For receiving IR codes reliably, configure your Tasmota device to publish `tele` messages via MQTT to Home Assistant. Then configure this integration in MQTT mode and set the `mqtt_topic` accordingly (e.g., `tele/tasmota_ir`).
- HTTP-based receiving is best-effort — Tasmota does not expose a standardized `IRRead` endpoint; MQTT is recommended for event delivery.

## Installation

1. Use the provided zip or add this repository to HACS as a custom repository (Integration type).
2. After install, restart Home Assistant.
3. Add the integration through Settings → Devices & Services → Add Integration → Tasmota IR Hub.
