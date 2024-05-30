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
        region = entry.data.get("region", None)
        region = region if region and len(region) == 2 else None
        self.libre = LibreView(
            username=entry.data[CONF_EMAIL],
            password=entry.data[CONF_PASSWORD],
            region=region,
        )
        super().__init__(
            hass, LOGGER, name=DOMAIN, update_interval=DEFAULT_SCAN_INTERVAL
        )

    async def _async_update_data(self) -> dict:
        try:
            LOGGER.debug("Updating data")
            await self.hass.async_add_executor_job(self.libre.get_connections)
        except Exception as ex:
            LOGGER.error(ex)
            raise

        # Store data in a way Home Assistant can easily consume it
        LOGGER.debug(self.libre.connections_dict)
        data = {
            "glucose_readings": self.libre.connections_dict,
        }
        return data
