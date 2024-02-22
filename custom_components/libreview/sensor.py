from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN, LOGGER, GlucoseUnitOfMeasurement, CONF_UOM
from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity

from uuid import UUID
from .coordinator import LibreViewCoordinator
from LibreView.models import Connection, GlucoseMeasurement
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from typing import Dict

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: LibreViewCoordinator = hass.data[DOMAIN][entry.entry_id]
    sensors: list[Entity] = [
        GlucoseSensor(coordinator, connection_id, GlucoseUnitOfMeasurement(entry.data[CONF_UOM]))
        for connection_id, _ in coordinator.data["glucose_readings"].items()
    ]

    async_add_entities(sensors)


class GlucoseSensor(CoordinatorEntity, SensorEntity):
    _attr_native_unit_of_measurement: str
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
        self._attr_native_unit_of_measurement = self.uom.value

    @property
    def connection(self) -> Connection:
        return self.coordinator.data["glucose_readings"][self.connection_id]

    @property
    def gcm(self) -> GlucoseMeasurement:
        return self.connection.glucose_measurement

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        name = f"{self.connection.first_name } {self.connection.last_name}"
        return f"{name} Glucose Measurement"

    @property
    def native_value(self) -> str | None:
        """Return the state of the entity."""
        if self.uom == GlucoseUnitOfMeasurement.MMOLL:
            return self.gcm.value
        if self.uom == GlucoseUnitOfMeasurement.MGDL:
            return self.gcm.value_in_mg_per_dl
        return None

    @property
    def extra_state_attributes(self) -> Dict[str, int | float]:
        return {GlucoseUnitOfMeasurement.MMOLL.value: self.gcm.value, GlucoseUnitOfMeasurement.MGDL.value: self.gcm.value_in_mg_per_dl}
