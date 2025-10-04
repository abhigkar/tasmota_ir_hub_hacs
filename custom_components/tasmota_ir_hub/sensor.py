from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN, ATTR_RAW

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([TasmotaLastIrSensor(coordinator, entry)])

class TasmotaLastIrSensor(Entity):
    def __init__(self, coordinator, entry):
        self.coordinator = coordinator
        self._entry = entry
        self._attr_name = f"Tasmota IR Last ({entry.data.get('host')})"
        self._unique_id = f"{entry.entry_id}_last_ir"

    @property
    def name(self):
        return self._attr_name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def state(self):
        data = self.coordinator.data or {}
        return (data.get("device_type") or "unknown") if data else None

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        return {ATTR_RAW: data.get("raw"), "payload": data.get("raw_payload")}

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
