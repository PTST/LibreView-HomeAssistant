"""Constants for the LibreView integration."""

from datetime import timedelta
import logging
from enum import Enum

DOMAIN = "libreview"

LOGGER = logging.getLogger(__package__)

CONF_GIID = "giid"
DEFAULT_SCAN_INTERVAL = timedelta(minutes=1)

CONF_UOM = "uom"

class GlucoseUnitOfMeasurement(Enum):
    MMOLL = "mmol/L"
    MGDL = "mg/dl"
