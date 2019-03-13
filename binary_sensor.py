"""
    Support for the SmartWeather Weatherstation from WeatherFlow
    This component will read the local or public weatherstation data
    and create a few binary sensors.

    For a full description, go here: https://github.com/briis/hass-SmartWeather

    Author: Bjarne Riis
"""
import logging
from datetime import timedelta

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from . import DATA_SMARTWEATHER, CONF_NAME, ATTRIBUTION

from homeassistant.const import (
    ATTR_ATTRIBUTION, CONF_ENTITY_NAMESPACE, CONF_MONITORED_CONDITIONS)

from homeassistant.components.binary_sensor import (
    BinarySensorDevice, PLATFORM_SCHEMA, ENTITY_ID_FORMAT)
from homeassistant.helpers.entity import Entity, generate_entity_id

DEPENDENCIES = ['smartweather']

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    'raining': ['Raining', 'moisture', 'mdi:water', 'mdi:water-off'],
    'freezing': ['Freezing', 'cold', 'mdi:fridge', 'mdi:fridge-outline']
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_MONITORED_CONDITIONS, default=list(SENSOR_TYPES)):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the SmartWeather binary sensor platform."""

    data = hass.data[DATA_SMARTWEATHER]
    name = hass.data[CONF_NAME]

    if data.data.timestamp is None:
        return

    sensors = []
    for variable in config[CONF_MONITORED_CONDITIONS]:
        sensors.append(SmartWeatherBinarySensor(hass, data, variable, name))
        _LOGGER.debug("Binary ensor added: " + variable)

    add_entities(sensors, True)

class SmartWeatherBinarySensor(BinarySensorDevice):
    """ Implementation of a SmartWeather Weatherflow Current Sensor """

    def __init__(self, hass, data, condition, name):
        """Initialize the sensor."""
        self._condition = condition
        self.data = data
        self._device_class = SENSOR_TYPES[self._condition][1]
        self._name = SENSOR_TYPES[self._condition][0]
        self.entity_id = generate_entity_id(ENTITY_ID_FORMAT, '{} {}'.format(name, SENSOR_TYPES[self._condition][0]), hass=hass)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def is_on(self):
        """Return the state of the sensor."""
        if hasattr(self.data.data, self._condition):
            variable = getattr(self.data.data, self._condition)
            if not (variable is None):
                return variable
        return None

    @property
    def icon(self):
        """Icon to use in the frontend."""
        if getattr(self.data.data, self._condition):
            return SENSOR_TYPES[self._condition][2]
        else:
            return SENSOR_TYPES[self._condition][3]

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return SENSOR_TYPES[self._condition][1]

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        attr = {}
        attr[ATTR_ATTRIBUTION] = ATTRIBUTION
        return attr

    def update(self):
        """Update current conditions."""
        self.data.update()
