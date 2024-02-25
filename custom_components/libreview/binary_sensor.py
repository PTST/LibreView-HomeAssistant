from typing import Dict
from uuid import UUID

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from LibreView.models import Connection, GlucoseMeasurement

from .const import CONF_UOM, DEFAULT_ICON, DOMAIN, GlucoseUnitOfMeasurement
from .coordinator import LibreViewCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
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
        self._attr_unique_id = f"{connection_id}_glucose_reading_is_high"
        self.connection_id = connection_id
        self.uom = uom

    @property
    def icon(self):
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
        return f"{name} glucose level is high"

    @property
    def is_on(self) -> bool:
        """Return the state of the entity."""
        return self.gcm.value_in_mg_per_dl > self.connection.target_high

    @property
    def extra_state_attributes(self) -> Dict[str, int | float]:
        return {
            "target_high_mmol_l": round(self.connection.target_high / 18, 1),
            "target_high_mg_dl": self.connection.target_high,
        }


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
        self._attr_unique_id = f"{connection_id}_glucose_reading_is_low"
        self.connection_id = connection_id
        self.uom = uom

    @property
    def icon(self):
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
        return f"{name} glucose level is low"

    @property
    def is_on(self) -> bool:
        """Return the state of the entity."""
        return self.gcm.value_in_mg_per_dl > self.connection.target_low

    @property
    def extra_state_attributes(self) -> Dict[str, int | float]:
        return {
            "target_low_mmol_l": round(self.connection.target_low / 18, 1),
            "target_low_mg_dl": self.connection.target_low,
        }
