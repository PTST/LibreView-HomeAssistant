from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import CONF_GIID, DEVICE_TYPE_NAME, DOMAIN, LOGGER, GlucoseUnitOfMeasurement
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
)
from uuid import UUID
from .coordinator import LibreViewCoordinator
from LibreView.models import Connection, GlucoseMeasurement
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    LOGGER.error(entry)
    coordinator: LibreViewCoordinator = hass.data[DOMAIN][entry.entry_id]
    sensors: list[Entity] = [
        GlucoseSensor(coordinator, connection_id, GlucoseMeasurement.MMOLL)
        for connection_id, values in coordinator.data["glucose_readings"].items()
    ]

class GlucoseSensor(CoordinatorEntity, SensorEntity):
    _attr_native_unit_of_measurement : str
    gcm: GlucoseMeasurement
    con: Connection
    uom: GlucoseUnitOfMeasurement

    def __init__(self, coordinator: LibreViewCoordinator, connection_id: UUID, uom: GlucoseUnitOfMeasurement):
        super().__init__(coordinator)
        self._attr_unique_id = f"{connection_id}_glucose_reading"
        self.connection_id = connection_id
        self.con = self.coordinator.data["glucose_readings"][self.connection_id]
        self.gcm = con.glucose_measurement
        self.uom = uom
        self._attr_native_unit_of_measurement = self.uom.value

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        name = f"{self.con.first_name } {self.con.last_name}"
        return f"{name} Glucose Measurement"

    @property
    def native_value(self) -> str | None:
        """Return the state of the entity."""
        if self.uom == GlucoseUnitOfMeasurement.MMOLL:
            return self.gcm.value
        if self.uom == GlucoseMeasurement.MGDL:
            return self.value_in_mg_per_dl
        return None