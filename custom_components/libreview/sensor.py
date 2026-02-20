from datetime import datetime, timedelta, timezone
from typing import Dict
from uuid import UUID

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from LibreView.models import Connection, GlucoseMeasurement, Sensor

from .const import (
    CONF_SENSOR_DURATION,
    CONF_SHOW_TREND_ARROW,
    CONF_UOM,
    DEFAULT_ICON,
    DOMAIN,
    SENSOR_ICON,
    TREND_ICONS,
    TREND_MESSAGE,
    GlucoseUnitOfMeasurement,
)
from .coordinator import LibreViewCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: LibreViewCoordinator = hass.data[DOMAIN][entry.entry_id]
    uom = GlucoseUnitOfMeasurement(entry.data[CONF_UOM])
    sensor_duration = int(entry.data[CONF_SENSOR_DURATION])
    show_trend_arrow = bool(entry.data[CONF_SHOW_TREND_ARROW])
    sensors: list[Entity] = [
        GlucoseSensor(coordinator, connection_id, uom, show_trend_arrow)
        for connection_id, _ in coordinator.data["glucose_readings"].items()
    ] + [
        LibreSensor(coordinator, connection_id, sensor_duration)
        for connection_id, _ in coordinator.data["glucose_readings"].items()
    ]
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
    def extra_state_attributes(self) -> Dict[str, str]:
        return {
            "application_datetime": self.application_dt,
            "serial_no": self.sensor.sn,
        }


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
    def trend_arrow(self) -> int:
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

    def get_mmol_l_value(self) -> float:
        return self.gcm_value_in_mg_per_dl / 18.0

    @property
    def extra_state_attributes(self) -> Dict[str, int | float]:
        return {
            "value_mmol_l": self.get_mmol_l_value,
            "value_mg_dl": self.gcm.value_in_mg_per_dl,
            "target_high_mmol_l": round(self.connection.target_high / 18, 1),
            "target_low_mmol_l": round(self.connection.target_low / 18, 1),
            "target_high_mg_dl": self.connection.target_high,
            "target_low_mg_dl": self.connection.target_low,
            "trend": TREND_MESSAGE.get(self.trend_arrow, "unknown"),
            "measurement_timestamp": self.gcm.factory_timestamp.replace(
                tzinfo=timezone.utc
            ),
        }
