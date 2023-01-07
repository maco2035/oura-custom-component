"""Provides a sleep sensor."""

import logging
import voluptuous as vol

from dateutil import parser
from homeassistant import const
from homeassistant.helpers import config_validation as cv
from . import api
from . import sensor_base
from .helpers import date_helper

# Sensor configuration
_DEFAULT_NAME = 'oura_sleep'

_DEFAULT_MONITORED_VARIABLES = [
    'average_breath',
    'average_heart_rate',
    'awake_duration_in_hours',
    'bedtime_start_hour',
    'bedtime_end_hour',
    'day',
    'deep_sleep_duration_in_hours',
    'in_bed_duration_in_hours',
    'light_sleep_duration_in_hours',
    'lowest_heart_rate',
    'rem_sleep_duration_in_hours',
    'total_sleep_duration_in_hours',
]
_SUPPORTED_MONITORED_VARIABLES = [
    'average_breath',
    'average_heart_rate',
    'average_hrv',
    'day',
    'awake_time',
    'awake_duration_in_hours',
    'awake_duration',
    'bedtime_end',
    'bedtime_end_hour',
    'bedtime_start',
    'bedtime_start_hour',
    'deep_sleep_duration',
    'deep_sleep_duration_in_hours',
    'efficiency',
    'heart_rate',
    'hrv',
    'in_bed_duration_in_hours',
    'latency',
    'light_sleep_duration',
    'light_sleep_duration_in_hours',
    'low_battery_alert',
    'lowest_heart_rate',
    'movement_30_sec',
    'period',
    'readiness_score_delta',
    'rem_sleep_duration',
    'rem_sleep_duration_in_hours',
    'restless_periods',
    'sleep_phase_5_min',
    'sleep_score_delta',
    'time_in_bed',
    'total_sleep_duration',
    'total_sleep_duration_in_hours',
    'type',
]

CONF_KEY_NAME = 'sleep'
CONF_SCHEMA = {
    vol.Optional(const.CONF_NAME, default=_DEFAULT_NAME): cv.string,

    vol.Optional(
        sensor_base.CONF_MONITORED_DATES,
        default=sensor_base.DEFAULT_MONITORED_DATES
    ): cv.ensure_list,

    vol.Optional(
        const.CONF_MONITORED_VARIABLES,
        default=_DEFAULT_MONITORED_VARIABLES
    ): vol.All(cv.ensure_list, [vol.In(_SUPPORTED_MONITORED_VARIABLES)]),

    vol.Optional(
        sensor_base.CONF_BACKFILL,
        default=sensor_base.DEFAULT_BACKFILL
    ): cv.positive_int,
}

# There is no need to add any configuration as all fields are optional and
# with default values. However, this is done as it is used in the main sensor.
DEFAULT_CONFIG = {}

_EMPTY_SENSOR_ATTRIBUTE = {
    variable: None for variable in _SUPPORTED_MONITORED_VARIABLES
}


class OuraSleepSensor(sensor_base.OuraDatedSensor):
  """Representation of an Oura Ring Sleep sensor.

  Attributes:
    name: name of the sensor.
    state: state of the sensor.
    extra_state_attributes: attributes of the sensor.

  Methods:
    async_update: updates sensor data.
  """

  def __init__(self, config, hass):
    """Initializes the sensor."""
    sleep_config = config.get(const.CONF_SENSORS, {}).get(CONF_KEY_NAME, {})
    super(OuraSleepSensor, self).__init__(config, hass, sleep_config)

    self._api_endpoint = api.OuraEndpoints.SLEEP
    self._empty_sensor = _EMPTY_SENSOR_ATTRIBUTE
    self._main_state_attribute = 'efficiency'

  def parse_individual_data_point(self, data_point):
    """Parses the individual day or data point.

    Args:
      data_point: Object for an individual day or data point.

    Returns:
      Modified data_point with right parsed data.
    """
    data_point_copy = {}
    data_point_copy.update(data_point)

    bedtime_start = parser.parse(data_point_copy.get('bedtime_start'))
    bedtime_end = parser.parse(data_point_copy.get('bedtime_end'))

    # Derived metrics.
    data_point_copy.update({
        # HH:MM at which you went bed.
        'bedtime_start_hour': bedtime_start.strftime('%H:%M'),
        # HH:MM at which you woke up.
        'bedtime_end_hour': bedtime_end.strftime('%H:%M'),
        # Hours in deep sleep.
        'deep_sleep_duration_in_hours': date_helper.seconds_to_hours(
            data_point_copy.get('deep_sleep_duration')),
        # Hours in REM sleep.
        'rem_sleep_duration_in_hours': date_helper.seconds_to_hours(
            data_point_copy.get('rem_sleep_duration')),
        # Hours in light sleep.
        'light_sleep_duration_in_hours': date_helper.seconds_to_hours(
            data_point_copy.get('light_sleep_duration')),
        # Hours sleeping: deep + rem + light.
        'total_sleep_duration_in_hours': date_helper.seconds_to_hours(
            data_point_copy.get('total_sleep_duration')),
        # Hours awake.
        'awake_duration': date_helper.seconds_to_hours(
            data_point_copy.get('awake_time')),
        # Hours in bed: sleep + awake.
        'in_bed_duration_in_hours': date_helper.seconds_to_hours(
            data_point_copy.get('time_in_bed')),
    })

    return data_point_copy
