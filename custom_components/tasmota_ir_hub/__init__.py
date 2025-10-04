import asyncio
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST
from .const import DOMAIN, PLATFORMS, DATA_COORDINATOR, SERVICE_SEND_IR, SERVICE_LEARN_IR
from .coordinator import TasmotaIrCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    # Nothing to set up at platform load time
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    config = entry.data
    host = config.get(CONF_HOST)

    coordinator = TasmotaIrCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        DATA_COORDINATOR: coordinator,
    }

    # forward platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def async_handle_send_ir(service_call):
        raw = service_call.data.get("raw")
        await coordinator.client.send_ir(raw)

    async def async_handle_learn_ir(service_call):
        # trigger learn mode; implementation depends on device
        await coordinator.client.start_learn_mode()

    hass.services.async_register(DOMAIN, SERVICE_SEND_IR, async_handle_send_ir)
    hass.services.async_register(DOMAIN, SERVICE_LEARN_IR, async_handle_learn_ir)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
