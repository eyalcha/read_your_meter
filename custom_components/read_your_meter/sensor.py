"""Read youe meter sensor."""

import logging

from datetime import datetime, timedelta

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed


from .const import (
    DOMAIN_DATA, DATA, DATA_CLIENT,
    DEFAULT_SCAN_INTERVAL, DEFAULT_NAME, DEFAULT_ICON,
    DEFAULT_UNIT_OF_MEASUREMENTS
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

    async_add_entities([
        ReadYourMeterSensor(hass, coordinator, None, config),
        ReadYourMeterSensor(hass, coordinator, 'daily', config),
        ReadYourMeterSensor(hass, coordinator, 'monthly', config),
        ])


class ReadYourMeterSensor(Entity):
    """Read your meter sensor"""

    def __init__(self, hass, coordinator, period, config) -> None:
        """Init sensor"""
        self._hass = hass
        self._coordinator = coordinator
        self._period = period
        self._name = DEFAULT_NAME if not period else '{} {}'.format(DEFAULT_NAME, period)
        self._icon = DEFAULT_ICON
        self._client = hass.data[DOMAIN_DATA][DATA_CLIENT]

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._period is 'daily':
            return self._client.daily
        elif self._period is 'monthly':
            return self._client.monthly
        else:
            return self._client.last_read

    @property
    def device_state_attributes(self):
        """Return the attributes of the sensor."""
        if self._period is 'daily':
            attributes = {
                "reading_state": self._client.daily_state
            }
        elif self._period is 'monthly':
            attributes = {
                "reading_state": self._client.monthly_state
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
        return DEFAULT_UNIT_OF_MEASUREMENTS

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