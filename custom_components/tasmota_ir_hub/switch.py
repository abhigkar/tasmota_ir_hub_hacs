from homeassistant.helpers.entity import ToggleEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([TasmotaSendIrSwitch(coordinator, entry, identifier="send_ir")])

class TasmotaSendIrSwitch(ToggleEntity):
    def __init__(self, coordinator, entry, identifier="send_ir"):
        self.coordinator = coordinator
        self._entry = entry
        self._attr_name = f"Tasmota IR Send ({entry.data.get('host')})"
        self._unique_id = f"{entry.entry_id}_{identifier}"
        self._is_on = False

    @property
    def name(self):
        return self._attr_name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def is_on(self):
        return self._is_on

    async def async_turn_on(self, **kwargs):
        # This switch doesn't maintain on/off; use it as a momentary trigger
        raw = kwargs.get("raw")
        if not raw:
            return
        await self.coordinator.client.send_ir(raw)
        # flip state briefly to indicate trigger
        self._is_on = True
        self.async_write_ha_state()
        await self.coordinator.hass.async_add_executor_job(lambda: None)
        # reset state
        self._is_on = False
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        # no-op
        self._is_on = False
        self.async_write_ha_state()
