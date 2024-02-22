"""Constants for the LibreView integration."""

import logging
from datetime import timedelta
from enum import Enum

DOMAIN = "libreview"

LOGGER = logging.getLogger(__package__)

DEFAULT_SCAN_INTERVAL = timedelta(minutes=1)

CONF_UOM = "uom"


class GlucoseUnitOfMeasurement(Enum):
    MMOLL = "mmol/L"
    MGDL = "mg/dl"
