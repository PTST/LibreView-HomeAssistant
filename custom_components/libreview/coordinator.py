from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from LibreView import LibreView

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, LOGGER


class LibreViewCoordinator(DataUpdateCoordinator):
    entry: ConfigEntry
    libre: LibreView

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.entry = entry
        self.libre = LibreView(
            username=entry.data[CONF_EMAIL], password=entry.data[CONF_PASSWORD]
        )
        super().__init__(
            hass, LOGGER, name=DOMAIN, update_interval=DEFAULT_SCAN_INTERVAL
        )

    async def _async_update_data(self) -> dict:
        try:
            await self.hass.async_add_executor_job(self.libre.get_connections)
        except Exception as ex:
            LOGGER.error("Could not update status, %s", ex)
            raise

        # Store data in a way Home Assistant can easily consume it
        data = {
            "glucose_readings": self.libre.connections_dict,
        }
        return data
