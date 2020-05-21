"""Read youe meter sensor."""

import logging

from datetime import datetime, timedelta

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from homeassistant.const import (
    CONF_UNIT_OF_MEASUREMENT
)

from .const import (
    DOMAIN_DATA, DATA, DATA_CLIENT,
    CONF_DAILY, CONF_MONTHLY,
    DEFAULT_SCAN_INTERVAL, DEFAULT_NAME, DEFAULT_ICON
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup sensor platform"""

    async def async_update_data():
        try:
            client = hass.data[DOMAIN_DATA][DATA_CLIENT]
            await hass.async_add_executor_job(client.update_data)
        except Exception as e:
            raise UpdateFailed(f"Error communicating with server: {e}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="sensor",
        update_method=async_update_data,
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
    )

    # Immediate refresh
    await coordinator.async_request_refresh()
    
    entities = [ReadYourMeterSensor(hass, discovery_info, coordinator)]
    for d in discovery_info.get(CONF_DAILY):
        entities.append(ReadYourMeterSensor(hass, discovery_info, coordinator, 'daily', d))
    for m in discovery_info.get(CONF_MONTHLY):
        entities.append(ReadYourMeterSensor(hass, discovery_info, coordinator, 'monthly', m))
    async_add_entities(entities)


class ReadYourMeterSensor(Entity):
    """Read your meter sensor"""

    def __init__(self, hass, config, coordinator, period=None, index=None) -> None:
        """Init sensor"""
        self._hass = hass
        self._coordinator = coordinator
        self._period = period
        self._index = index
        self._icon = DEFAULT_ICON
        self._client = hass.data[DOMAIN_DATA][DATA_CLIENT]
        self._unit_of_measurement = config.get(CONF_UNIT_OF_MEASUREMENT)
        _LOGGER.debug(f"Add sensor period:{self._period} index:{self._index} icon:{ self._icon}")

    @property
    def name(self):
        """Return the name of the sensor."""
        if not self._period:
            return DEFAULT_NAME
        elif self._index == 0:
            return '{} {}'.format(DEFAULT_NAME, self._period)
        return '{} {} {}'.format(DEFAULT_NAME, self._period, self._index)

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._period:
            return self._client.consumption(self._period, self._index)
        else:
            return self._client.last_read

    @property
    def device_state_attributes(self):
        """Return the attributes of the sensor."""
        if self._period:
            statistics = self._client.statistics(self._period)
            if self._index == 0:
                attributes = {
                    "date": self._client.date(self._period, self._index),
                    "avg": statistics['avg'] if 'avg' in statistics else 0,
                    "min": statistics['min'] if 'min' in statistics else 0,
                    "max": statistics['max'] if 'max' in statistics else 0,
                    "reading_state": self._client.state(self._period, self._index)
                }
            else:
                attributes = {
                    "date": self._client.date(self._period, self._index),
                    "reading_state": self._client.state(self._period, self._index)
                }
        else:
            attributes = {
                "meter_number": self._client.meter_number
            }
        return attributes

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

    @property
    def should_poll(self):
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    @property
    def available(self):
        """Return if entity is available."""
        return self._coordinator.last_update_success

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    async def async_update(self):
        """Update the entity. Only used by the generic entity update service."""
        await self._coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self._coordinator.async_add_listener(
                self.async_write_ha_state
            )
        )