from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant
from typing import Any
from datetime import timedelta
import async_timeout
import logging

from .api import TasmotaIrHubClient
from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

class TasmotaIrCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry):
        self.hass = hass
        self.entry = entry
        self.client = TasmotaIrHubClient(
            hass,
            host=entry.data.get("host"),
            port=entry.data.get("port", 80),
            http_user=entry.data.get("http_user"),
            http_pass=entry.data.get("http_pass"),
            use_mqtt=entry.data.get("use_mqtt", False),
            mqtt_topic=entry.data.get("mqtt_topic"),
        )
        scan = entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            name="Tasmota IR Hub",
            update_interval = timedelta(seconds=scan)
        )
        # internal state
        self.last_ir: dict[str, Any] = {}

    async def _async_update_data(self):
        # Polling path for HTTP mode: attempt to query a status endpoint
        if not self.client.use_mqtt:
            try:
                async with async_timeout.timeout(10):
                    # Tasmota does not provide a standard IR receive GET endpoint; many users instead
                    # configure the device to publish received codes to an MQTT topic. We attempt
                    # to query /cm?cmnd=IRRead or /cm?cmnd=Status 8 if available. This is best-effort.
                    # If nothing is available, return previous cached value.
                    return self.last_ir
            except Exception as err:
                raise UpdateFailed(err)

        # MQTT mode: data is pushed; nothing to poll, return cached
        return self.last_ir

    async def async_handle_mqtt_message(self, topic: str, payload: str):
        """Called by mqtt subscription to update the coordinator state when an IR event arrives."""
        # Basic parsing: payload is expected to be a JSON string containing a `IR` or `IRRecv` field
        try:
            # best-effort parsing
            import json
            parsed = None
            try:
                parsed = json.loads(payload)
            except Exception:
                parsed = {"raw": payload}

            # Normalize into a small dict with raw and device-type guess
            raw = parsed.get("IR") or parsed.get("IRrecv") or parsed.get("raw")
            device_type = parsed.get("DeviceType") or parsed.get("Type") or "unknown"
            self.last_ir = {"raw": raw, "device_type": device_type, "raw_payload": parsed}
            self.async_set_updated_data(self.last_ir)
        except Exception as e:
            _LOGGER.exception("Failed to handle MQTT IR message: %s", e)
