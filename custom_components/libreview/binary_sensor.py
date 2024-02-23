from datetime import datetime, timedelta, timezone
from typing import Dict
from uuid import UUID

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from LibreView.models import Connection, GlucoseMeasurement, Sensor
from .coordinator import LibreViewCoordinator

from .const import (
    CONF_SENSOR_DURATION,
    CONF_SHOW_TREND_ARROW,
    CONF_UOM,
    DEFAULT_ICON,
    DOMAIN,
    SENSOR_ICON,
    TREND_ICONS,
    GlucoseUnitOfMeasurement,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up G4S binary sensors based on a config entry."""
    coordinator: LibreViewCoordinator = hass.data[DOMAIN][entry.entry_id]
    uom = GlucoseUnitOfMeasurement(entry.data[CONF_UOM])

    sensors = [
        GlucoseHighSensor(coordinator, connection_id, uom)
        for connection_id, _ in coordinator.data["glucose_readings"].items()
    ] + [
        GlucoseLowSensor(coordinator, connection_id, uom)
        for connection_id, _ in coordinator.data["glucose_readings"].items()
    ]

    async_add_entities(sensors)


class GlucoseHighSensor(CoordinatorEntity, BinarySensorEntity):
    coordinator: LibreViewCoordinator
    uom: GlucoseUnitOfMeasurement

    def __init__(
        self,
        coordinator: LibreViewCoordinator,
        connection_id: UUID,
        uom: GlucoseUnitOfMeasurement,
    ):
        super().__init__(coordinator)
        self._attr_unique_id = f"{connection_id}_glucose_reading"
        self.connection_id = connection_id
        self.uom = uom


class GlucoseLowSensor(CoordinatorEntity, BinarySensorEntity):
    coordinator: LibreViewCoordinator
    uom: GlucoseUnitOfMeasurement

    def __init__(
        self,
        coordinator: LibreViewCoordinator,
        connection_id: UUID,
        uom: GlucoseUnitOfMeasurement,
    ):
        super().__init__(coordinator)
        self._attr_unique_id = f"{connection_id}_glucose_reading"
        self.connection_id = connection_id
        self.uom = uom
