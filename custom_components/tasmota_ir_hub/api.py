import asyncio
import logging
from typing import Optional
import aiohttp

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

class TasmotaIrHubClient:
    """Async client for a Tasmota-based IR hub.

    Supports two modes:
      - MQTT: rely on Home Assistant's MQTT integration to receive `tele/...` messages.
      - HTTP: send commands to Tasmota's web API (`/cm?cmnd=...`).

    The client implements sending IR (send_ir) and starting learn mode (start_learn_mode).
    """

    def __init__(self, hass: HomeAssistant, host: Optional[str] = None, port: int = 80, http_user: Optional[str] = None, http_pass: Optional[str] = None, use_mqtt: bool = False, mqtt_topic: Optional[str] = None):
        self.hass = hass
        self.host = host
        self.port = port
        self.http_user = http_user
        self.http_pass = http_pass
        self.use_mqtt = use_mqtt
        self.mqtt_topic = mqtt_topic
        self._session: Optional[aiohttp.ClientSession] = None

    async def async_get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def send_ir(self, raw_code: str) -> None:
        """Send an IR raw code string to the hub.

        If `use_mqtt` is True, we publish via HASS MQTT component (user must configure MQTT in HA).
        Otherwise we call Tasmota HTTP API.
        """
        if self.use_mqtt:
            # Use Home Assistant MQTT publish
            try:
                await self.hass.components.mqtt.async_publish(self.mqtt_topic + "/command", raw_code)
                _LOGGER.debug("Published IR via MQTT to %s", self.mqtt_topic + "/command")
            except Exception as err:
                _LOGGER.error("Failed to publish IR via MQTT: %s", err)
                raise
            return

        # HTTP mode: call Tasmota cm?cmnd=IRSend <raw> (URL-encoded)
        session = await self.async_get_session()
        url = f"http://{self.host}:{self.port}/cm?cmnd=IRSend%20{raw_code}"
        auth = None
        if self.http_user and self.http_pass:
            auth = aiohttp.BasicAuth(self.http_user, self.http_pass)
        _LOGGER.debug("Sending IR HTTP request to %s", url)
        try:
            async with session.get(url, auth=auth, timeout=10) as resp:
                text = await resp.text()
                _LOGGER.debug("Tasmota IR send response: %s", text)
        except Exception as e:
            _LOGGER.error("Error sending IR via HTTP: %s", e)
            raise

    async def start_learn_mode(self) -> None:
        """Trigger Tasmota to start IR learning if supported.

        Note: Command names vary by firmware; we attempt `IRLearn` then `IRLearning` as common patterns.
        """
        if self.use_mqtt:
            await self.hass.components.mqtt.async_publish(self.mqtt_topic + "/command", "IRLearn")
            return

        session = await self.async_get_session()
        # Try common Tasmota commands; allow failures
        for cmd in ("IRLearn 1", "IRLearning 1"):
            url = f"http://{self.host}:{self.port}/cm?cmnd={cmd.replace(' ', '%20')}"
            try:
                async with session.get(url, timeout=10) as resp:
                    _LOGGER.debug("Called %s -> %s", cmd, await resp.text())
                    return
            except Exception:
                _LOGGER.debug("Learn mode command %s failed, trying next", cmd)
        _LOGGER.error("Failed to start IR learn mode via HTTP")

    async def async_close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
