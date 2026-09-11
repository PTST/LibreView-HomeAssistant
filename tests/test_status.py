"""Tests for Libre sensor status derivation."""

import importlib.util
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

STATUS_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "libreview"
    / "status.py"
)
SPEC = importlib.util.spec_from_file_location("libreview_status", STATUS_PATH)
STATUS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(STATUS)


class TestDeriveSensorStatus(unittest.TestCase):
    """Validate the derived status decision order."""

    def setUp(self) -> None:
        self.now = datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc)
        self.expiry = self.now + timedelta(days=5)

    def derive(
        self,
        *,
        expiry_dt=None,
        measurement_available=True,
        measurement_dt=None,
        max_data_age=5,
        expiry_warning_hours=24,
    ):
        """Call derive_sensor_status with sensible test defaults."""
        return STATUS.derive_sensor_status(
            now=self.now,
            expiry_dt=self.expiry if expiry_dt is None else expiry_dt,
            measurement_available=measurement_available,
            measurement_dt=(
                self.now - timedelta(minutes=1)
                if measurement_dt is None and measurement_available
                else measurement_dt
            ),
            config=STATUS.SensorStatusConfig(
                max_data_age=max_data_age,
                expiry_warning_hours=expiry_warning_hours,
            ),
        )

    def test_active(self) -> None:
        self.assertEqual(self.derive(), STATUS.STATUS_ACTIVE)

    def test_no_recent_data(self) -> None:
        result = self.derive(measurement_dt=self.now - timedelta(minutes=10))
        self.assertEqual(result, STATUS.STATUS_NO_RECENT_DATA)

    def test_no_data(self) -> None:
        result = self.derive(measurement_available=False, measurement_dt=None)
        self.assertEqual(result, STATUS.STATUS_NO_DATA)

    def test_sensor_expired_takes_precedence(self) -> None:
        result = self.derive(expiry_dt=self.now - timedelta(seconds=1))
        self.assertEqual(result, STATUS.STATUS_SENSOR_EXPIRED)

    def test_unknown_when_expiry_missing(self) -> None:
        result = STATUS.derive_sensor_status(
            now=self.now,
            expiry_dt=None,
            measurement_available=True,
            measurement_dt=self.now,
            config=STATUS.SensorStatusConfig(
                max_data_age=5,
                expiry_warning_hours=24,
            ),
        )
        self.assertEqual(result, STATUS.STATUS_UNKNOWN)

    def test_unknown_when_measurement_timestamp_missing(self) -> None:
        result = STATUS.derive_sensor_status(
            now=self.now,
            expiry_dt=self.expiry,
            measurement_available=True,
            measurement_dt=None,
            config=STATUS.SensorStatusConfig(
                max_data_age=5,
                expiry_warning_hours=24,
            ),
        )
        self.assertEqual(result, STATUS.STATUS_UNKNOWN)

    def test_zero_disables_stale_detection(self) -> None:
        result = self.derive(
            measurement_dt=self.now - timedelta(hours=2), max_data_age=0
        )
        self.assertEqual(result, STATUS.STATUS_ACTIVE)

    def test_exact_stale_threshold_is_active(self) -> None:
        result = self.derive(measurement_dt=self.now - timedelta(minutes=5))
        self.assertEqual(result, STATUS.STATUS_ACTIVE)

    def test_expiring_soon(self) -> None:
        result = self.derive(expiry_dt=self.now + timedelta(hours=12))
        self.assertEqual(result, STATUS.STATUS_EXPIRING_SOON)

    def test_exact_expiry_warning_threshold_is_expiring_soon(self) -> None:
        result = self.derive(expiry_dt=self.now + timedelta(hours=24))
        self.assertEqual(result, STATUS.STATUS_EXPIRING_SOON)

    def test_zero_disables_expiry_warning(self) -> None:
        result = self.derive(
            expiry_dt=self.now + timedelta(hours=12), expiry_warning_hours=0
        )
        self.assertEqual(result, STATUS.STATUS_ACTIVE)

    def test_no_recent_data_takes_precedence_over_expiring_soon(self) -> None:
        result = self.derive(
            expiry_dt=self.now + timedelta(hours=12),
            measurement_dt=self.now - timedelta(minutes=10),
        )
        self.assertEqual(result, STATUS.STATUS_NO_RECENT_DATA)

    def test_no_data_takes_precedence_over_expiring_soon(self) -> None:
        result = self.derive(
            expiry_dt=self.now + timedelta(hours=12),
            measurement_available=False,
            measurement_dt=None,
        )
        self.assertEqual(result, STATUS.STATUS_NO_DATA)


if __name__ == "__main__":
    unittest.main()
