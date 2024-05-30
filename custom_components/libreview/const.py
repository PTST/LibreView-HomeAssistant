"""Constants for the LibreView integration."""

import logging
from datetime import timedelta
from enum import Enum

DOMAIN = "libreview"

LOGGER = logging.getLogger(__package__)

DEFAULT_SCAN_INTERVAL = timedelta(minutes=1)

CONF_UOM = "uom"
CONF_SENSOR_DURATION = "sensor_duration"
CONF_SHOW_TREND_ARROW = "show_trend_arrow"
CONF_REGION = "region"


DEFAULT_ICON = "mdi:diabetes"
SENSOR_ICON = "mdi:circle-double"
TREND_ICONS = {
    1: "mdi:arrow-down-thick",
    2: "mdi:arrow-bottom-right-thick",
    3: "mdi:arrow-right-thick",
    4: "mdi:arrow-top-right-thick",
    5: "mdi:arrow-up-thick",
}


class GlucoseUnitOfMeasurement(Enum):
    MMOLL = "mmol/L"
    MGDL = "mg/dl"
