"""Helpers for deriving Libre sensor status."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

STATUS_ACTIVE = "Active"
STATUS_EXPIRING_SOON = "Expiring Soon"
STATUS_NO_DATA = "No Data"
STATUS_NO_RECENT_DATA = "No Recent Data"
STATUS_SENSOR_EXPIRED = "Sensor Expired"
STATUS_UNKNOWN = "Unknown"


@dataclass(frozen=True)
class SensorStatusConfig:
    """Thresholds used when deriving sensor status."""

    max_data_age: int
    expiry_warning_hours: int


def derive_sensor_status(
    *,
    now: datetime,
    expiry_dt: Optional[datetime],
    measurement_available: bool,
    measurement_dt: Optional[datetime],
    config: SensorStatusConfig,
) -> str:
    """Return a best-effort sensor status from the available Libre data."""
    status = STATUS_ACTIVE

    if expiry_dt is None:
        status = STATUS_UNKNOWN
    elif now >= expiry_dt:
        status = STATUS_SENSOR_EXPIRED
    elif not measurement_available:
        status = STATUS_NO_DATA
    elif measurement_dt is None:
        status = STATUS_UNKNOWN
    elif config.max_data_age > 0 and now - measurement_dt > timedelta(
        minutes=config.max_data_age
    ):
        status = STATUS_NO_RECENT_DATA
    elif config.expiry_warning_hours > 0 and expiry_dt - now <= timedelta(
        hours=config.expiry_warning_hours
    ):
        status = STATUS_EXPIRING_SOON

    return status
