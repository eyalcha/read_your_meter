"""Read youe meter sensor."""

import logging

from datetime import datetime, timedelta

from homeassistant.helpers.entity import Entity

from .const import (
    DOMAIN_DATA, DATA, DATA_CLIENT
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=600)


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

    async def async_update(self) -> None:
        """Update"""
        client = self.hass.data[DOMAIN_DATA][DATA_CLIENT]
        daily_consumption = await client.async_get_daily_consumption()
        for row in daily_consumption:
            try: 
                if len(row):
                    date_time = datetime.strptime(row[0], '%d.%m.%Y')
                    if datetime.now().date() == date_time.date():
                        self._state = float(row[1])
                        _LOGGER.debug(f"Update state {self._state}")
                self._attributes = {
                  "meter_number": client.meter_number,
                  "last_read": client.last_read
                }
            except ValueError:
                continue