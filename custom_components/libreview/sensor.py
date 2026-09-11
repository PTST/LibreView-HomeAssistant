from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from uuid import UUID

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from LibreView.models import Connection, GlucoseMeasurement, Sensor

from .const import (
    CONF_EXPIRY_WARNING_HOURS,
    CONF_MAX_DATA_AGE,
    CONF_SENSOR_DURATION,
    CONF_SHOW_TREND_ARROW,
    CONF_UOM,
    DEFAULT_EXPIRY_WARNING_HOURS,
    DEFAULT_ICON,
    DEFAULT_MAX_DATA_AGE,
    DOMAIN,
    SENSOR_ICON,
    TREND_ICONS,
    TREND_MESSAGE,
    GlucoseUnitOfMeasurement,
)
from .coordinator import LibreViewCoordinator
from .status import SensorStatusConfig, derive_sensor_status


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: LibreViewCoordinator = hass.data[DOMAIN][entry.entry_id]
    uom = GlucoseUnitOfMeasurement.from_str(entry.data[CONF_UOM])
    sensor_duration = int(entry.data[CONF_SENSOR_DURATION])
    max_data_age = int(entry.data.get(CONF_MAX_DATA_AGE, DEFAULT_MAX_DATA_AGE))
    expiry_warning_hours = int(
        entry.data.get(CONF_EXPIRY_WARNING_HOURS, DEFAULT_EXPIRY_WARNING_HOURS)
    )
    show_trend_arrow = bool(entry.data[CONF_SHOW_TREND_ARROW])
    sensors: list[Entity] = (
        [
            GlucoseSensor(coordinator, connection_id, uom, show_trend_arrow)
            for connection_id, _ in coordinator.data["glucose_readings"].items()
        ]
        + [
            LibreSensor(coordinator, connection_id, sensor_duration)
            for connection_id, _ in coordinator.data["glucose_readings"].items()
        ]
        + [
            LibreSensorStatus(
                coordinator,
                connection_id,
                sensor_duration,
                max_data_age,
                expiry_warning_hours,
            )
            for connection_id, _ in coordinator.data["glucose_readings"].items()
        ]
    )
    async_add_entities(sensors)


class LibreSensor(CoordinatorEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(
        self,
        coordinator: LibreViewCoordinator,
        connection_id: UUID,
        sensor_duration: int,
    ):
        super().__init__(coordinator)
        self._attr_unique_id = f"{connection_id}_sensor_expiry"
        self.connection_id = connection_id
        self.sensor_duration = sensor_duration

    @property
    def application_dt(self):
        return datetime.fromtimestamp(self.sensor.a, timezone.utc)

    @property
    def icon(self):
        return SENSOR_ICON

    @property
    def connection(self) -> Connection:
        return self.coordinator.data["glucose_readings"][self.connection_id]

    @property
    def sensor(self) -> Sensor:
        return self.connection.sensor

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        name = f"{self.connection.first_name } {self.connection.last_name}"
        return f"{name} sensor expiry"

    @property
    def native_value(self) -> datetime | None:
        return self.application_dt + timedelta(days=self.sensor_duration)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "application_datetime": self.application_dt,
            "serial_no": f"{self.sensor.pt}{self.sensor.sn}",
        }


class LibreSensorStatus(CoordinatorEntity, SensorEntity):
    """Represent a derived Libre sensor status."""

    _attr_icon = "mdi:list-status"

    def __init__(
        self,
        coordinator: LibreViewCoordinator,
        connection_id: UUID,
        sensor_duration: int,
        max_data_age: int,
        expiry_warning_hours: int,
    ):
        super().__init__(coordinator)
        self._attr_unique_id = f"{connection_id}_sensor_status"
        self.connection_id = connection_id
        self.sensor_duration = sensor_duration
        self.max_data_age = max_data_age
        self.expiry_warning_hours = expiry_warning_hours

    @property
    def connection(self) -> Connection:
        return self.coordinator.data["glucose_readings"][self.connection_id]

    @property
    def sensor(self) -> Optional[Sensor]:
        return getattr(self.connection, "sensor", None)

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        name = f"{self.connection.first_name } {self.connection.last_name}"
        return f"{name} sensor status"

    @property
    def application_dt(self) -> Optional[datetime]:
        """Return the sensor application timestamp in UTC."""
        try:
            application_timestamp = int(self.sensor.a)
            if application_timestamp <= 0:
                return None
            return datetime.fromtimestamp(application_timestamp, timezone.utc)
        except (AttributeError, TypeError, ValueError, OSError, OverflowError):
            return None

    @property
    def expiry_dt(self) -> Optional[datetime]:
        """Return the configured sensor expiry timestamp."""
        if self.application_dt is None:
            return None
        return self.application_dt + timedelta(days=self.sensor_duration)

    @property
    def measurement_dt(self) -> Optional[datetime]:
        """Return the latest glucose measurement timestamp in UTC."""
        measurement = getattr(self.connection, "glucose_measurement", None)
        if measurement is None:
            return None

        try:
            return measurement.factory_timestamp.replace(tzinfo=timezone.utc)
        except (AttributeError, TypeError, ValueError, IndexError):
            return None

    @property
    def native_value(self) -> str:
        """Return the derived current sensor status."""
        measurement = getattr(self.connection, "glucose_measurement", None)
        return derive_sensor_status(
            now=datetime.now(timezone.utc),
            expiry_dt=self.expiry_dt,
            measurement_available=measurement is not None,
            measurement_dt=self.measurement_dt,
            config=SensorStatusConfig(
                max_data_age=self.max_data_age,
                expiry_warning_hours=self.expiry_warning_hours,
            ),
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return diagnostic details used to derive the status."""
        attributes: dict[str, Any] = {
            "connection_status": getattr(self.connection, "status", None),
            "stale_after_minutes": self.max_data_age,
            "stale_detection_enabled": self.max_data_age > 0,
            "expiry_warning_hours": self.expiry_warning_hours,
            "expiry_warning_enabled": self.expiry_warning_hours > 0,
        }

        if self.application_dt is not None:
            attributes["sensor_started"] = self.application_dt
        if self.expiry_dt is not None:
            now = datetime.now(timezone.utc)
            attributes["sensor_expires"] = self.expiry_dt
            expires_in_seconds = max(0.0, (self.expiry_dt - now).total_seconds())
            attributes["expires_in_hours"] = round(expires_in_seconds / 3600, 1)
        if self.measurement_dt is not None:
            now = datetime.now(timezone.utc)
            age_seconds = max(0.0, (now - self.measurement_dt).total_seconds())
            attributes["last_measurement"] = self.measurement_dt
            attributes["measurement_age_minutes"] = round(age_seconds / 60, 1)

        return attributes


class GlucoseSensor(CoordinatorEntity, SensorEntity):
    _attr_native_unit_of_measurement: str
    _attr_state_class = "measurement"
    uom: GlucoseUnitOfMeasurement

    def __init__(
        self,
        coordinator: LibreViewCoordinator,
        connection_id: UUID,
        uom: GlucoseUnitOfMeasurement,
        use_trend_icons: bool,
    ):
        super().__init__(coordinator)
        self._attr_unique_id = f"{connection_id}_glucose_reading"
        self.connection_id = connection_id
        self.uom = uom
        self._attr_native_unit_of_measurement = self.uom.value
        self.use_trend_icons = use_trend_icons

    @property
    def icon(self):
        if self.use_trend_icons:
            return TREND_ICONS.get(self.trend_arrow, DEFAULT_ICON)
        return DEFAULT_ICON

    @property
    def connection(self) -> Connection:
        return self.coordinator.data["glucose_readings"][self.connection_id]

    @property
    def gcm(self) -> GlucoseMeasurement:
        return self.connection.glucose_measurement

    @property
    def trend_arrow(self) -> Optional[int]:
        return self.gcm.trend_arrow

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        name = f"{self.connection.first_name } {self.connection.last_name}"
        return f"{name} glucose level"

    @property
    def native_value(self) -> int | float | None:
        """Return the state of the entity."""
        if self.uom == GlucoseUnitOfMeasurement.MMOLL:
            return self.get_mmol_l_value
        if self.uom == GlucoseUnitOfMeasurement.MGDL:
            return self.gcm.value_in_mg_per_dl
        return None

    @property
    def get_mmol_l_value(self) -> float:
        if self.app_uom == 1:
            return self.gcm.value_in_mg_per_dl / 18.0
        return self.gcm.value

    @property
    def app_uom(self) -> int:
        return self.connection.uom

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return {
            "value_mmol_l": self.get_mmol_l_value,
            "value_mg_dl": self.gcm.value_in_mg_per_dl,
            "target_high_mmol_l": round(self.connection.target_high / 18, 1),
            "target_low_mmol_l": round(self.connection.target_low / 18, 1),
            "target_high_mg_dl": self.connection.target_high,
            "target_low_mg_dl": self.connection.target_low,
            "trend": TREND_MESSAGE.get(self.trend_arrow, "unknown"),
            "app_unit_of_measurement": "mmol/L" if self.app_uom == 0 else "mg/dL",
            "measurement_timestamp": self.gcm.factory_timestamp.replace(
                tzinfo=timezone.utc
            ),
        }
