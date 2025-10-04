import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_HOST, CONF_PORT, CONF_USE_MQTT, CONF_MQTT_TOPIC, CONF_HTTP_USER, CONF_HTTP_PASS, CONF_SCAN_INTERVAL, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): str,
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
    vol.Optional(CONF_USE_MQTT, default=False): bool,
    vol.Optional(CONF_MQTT_TOPIC, default="tele/tasmota_ir"): str,
    vol.Optional(CONF_HTTP_USER, default=""): str,
    vol.Optional(CONF_HTTP_PASS, default=""): str,
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
})

class TasmotaIrHubConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA)

        # Basic validation may be added here; keep it permissive for now
        return self.async_create_entry(title=f"Tasmota IR Hub ({user_input[CONF_HOST]})", data=user_input)
