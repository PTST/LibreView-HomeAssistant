"""Constants for the LibreView integration."""

from datetime import timedelta
import logging

DOMAIN = "libreview"

LOGGER = logging.getLogger(__package__)

CONF_GIID = "giid"
DEFAULT_SCAN_INTERVAL = timedelta(minutes=1)
