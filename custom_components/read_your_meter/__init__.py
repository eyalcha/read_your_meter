"""Thermal integration"""

import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv

from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_UNIT_OF_MEASUREMENT
)

from .client import Client

from .const import (
    DOMAIN,
    DOMAIN_DATA,
    CONF_DAILY,
    CONF_MONTHLY,
    DEFAULT_HOST,
    DEFAULT_NAME,
    DEFAULT_DAILY,
    DEFAULT_MONTHLY,
    DEFAULT_UNIT_OF_MEASUREMENT,
    DATA, DATA_CLIENT
)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.url,
        vol.Optional(CONF_NAME, DEFAULT_NAME): cv.string,
        vol.Optional(CONF_SCAN_INTERVAL): cv.time_period,
        vol.Optional(CONF_UNIT_OF_MEASUREMENT, default=DEFAULT_UNIT_OF_MEASUREMENT): cv.string,
        vol.Optional(CONF_DAILY, default=DEFAULT_DAILY): vol.All(
            cv.ensure_list, [vol.Range(min=0, max=3)]
        ),
        vol.Optional(CONF_MONTHLY, default=DEFAULT_MONTHLY): vol.All(
            cv.ensure_list, [vol.Range(min=0, max=3)]
        ),
    })
}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass, config):

    # Check configuration exists
    conf = config.get(DOMAIN)
    if conf is None:
        return True

    host = conf.get(CONF_HOST)
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
        hass.helpers.discovery.async_load_platform('sensor', DOMAIN, conf, config)
    )

    # Initialization was successful.
    return True