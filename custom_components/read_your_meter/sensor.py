"""Read youe meter sensor."""

import logging

from datetime import datetime, timedelta

from homeassistant.helpers.entity import Entity

from .const import (
    DOMAIN_DATA, DATA, DATA_CLIENT
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=1800)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
  """Setup sensor platform"""
  async_add_entities([ReadYourMeterSensor(hass, config)], True)


class ReadYourMeterSensor(Entity):
    """Read your meter sensor"""

    def __init__(self, hass, config) -> None:
        """Init sensor"""
        self._hass = hass
        self._name = 'Read your meter'
        self._state = 0
        self._attributes = {}
        self._icon = 'mdi:gauge'
        self._client = hass.data[DOMAIN_DATA][DATA_CLIENT]

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the attributes of the sensor."""
        return self._attributes

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

    @property
    def should_poll(self):
        return True

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return 'm3'

    async def async_update(self) -> None:
        """Update"""
        await self._hass.async_add_executor_job(self._client.update_consumption)
        self._state = self._client.daily
        self._attributes = {
            "meter_number": self._client.meter_number,
            "monthly": self._client.monthly,
            "last_read": self._client.last_read,
            "daily_state": self._client.daily_state,
            "monthly_state": self._client.monthly_state,
        }
        _LOGGER.debug(f"Update state {self._state}")
