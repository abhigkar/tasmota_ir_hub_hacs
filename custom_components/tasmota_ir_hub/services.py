import voluptuous as vol
from homeassistant.helpers import config_validation as cv
from .const import SERVICE_SEND_IR

SEND_IR_SCHEMA = vol.Schema({vol.Required("raw"): cv.string})
