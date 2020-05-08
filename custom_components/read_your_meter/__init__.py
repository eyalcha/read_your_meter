"""Thermal integration"""

import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv

from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL
)

from .client import Client

from .const import (
    DOMAIN, DOMAIN_DATA,
    DEFAULT_HOST, DEFAULT_NAME,
    DATA, DATA_CLIENT
)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_HOST): cv.url,
        vol.Optional(CONF_NAME, DEFAULT_NAME): cv.string,
        vol.Optional(CONF_SCAN_INTERVAL): cv.time_period,
    })
}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass, config):

    # Check configuration exists
    conf = config.get(DOMAIN)
    if conf is None:
        return True

    host = conf.get(CONF_HOST, DEFAULT_HOST)
    username = conf.get(CONF_USERNAME)
    password = conf.get(CONF_PASSWORD)

    client = Client(host, 'https://cp.city-mind.com', username, password)
    if client is None:
        return True

    hass.data[DOMAIN_DATA] = {
        DATA_CLIENT: client
    }

    # Add sensors
    hass.async_create_task(
        hass.helpers.discovery.async_load_platform('sensor', DOMAIN, {}, config)
    )

    # Initialization was successful.
    return True