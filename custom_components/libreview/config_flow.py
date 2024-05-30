"""Config flow for LibreView integration."""

from typing import Any, Dict

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from LibreView import LibreView

from .const import (
    CONF_REGION,
    CONF_SENSOR_DURATION,
    CONF_SHOW_TREND_ARROW,
    CONF_UOM,
    DOMAIN,
    LOGGER,
    GlucoseUnitOfMeasurement,
)


class LibreViewOptionsFlowHandler(OptionsFlow):
    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.entry = entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            for key, value in self.entry.data.items():
                if key not in user_input.keys():
                    user_input[key] = value
            self.hass.config_entries.async_update_entry(
                self.entry, data=user_input, options=self.entry.options
            )
            self.async_abort(reason="configuration updated")
            return self.async_create_entry(title="", data={})

        default_uom = GlucoseUnitOfMeasurement.MMOLL
        if self.entry.data.get(CONF_UOM) is not None:
            default_uom = GlucoseUnitOfMeasurement(self.entry.data.get(CONF_UOM))

        default_duration = 14
        if self.entry.data.get(CONF_SENSOR_DURATION) is not None:
            default_duration = int(self.entry.data.get(CONF_SENSOR_DURATION))

        default_show_trend = False
        if self.entry.data.get(CONF_SHOW_TREND_ARROW) is not None:
            default_show_trend = bool(self.entry.data.get(CONF_SHOW_TREND_ARROW))

        default_region = "Standard"
        if self.entry.data.get(CONF_REGION) is not None:
            default_region = self.entry.data.get(CONF_REGION)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_UOM, default=default_uom): vol.In(
                        GlucoseUnitOfMeasurement
                    ),
                    vol.Required(CONF_SENSOR_DURATION, default=default_duration): int,
                    vol.Required(
                        CONF_SHOW_TREND_ARROW, default=default_show_trend
                    ): bool,
                    vol.Optional(CONF_REGION, default=default_region): vol.In(
                        [
                            "Standard",
                            "AE",
                            "AP",
                            "AU",
                            "CA",
                            "DE",
                            "EU",
                            "EU2",
                            "FR",
                            "JP",
                            "US",
                        ]
                    ),
                }
            ),
        )


class LibreViewConfigFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for LibreView."""

    VERSION = 1
    uom: GlucoseUnitOfMeasurement
    sensor_duration: int
    show_trend_icon: bool
    email: str
    entry: ConfigEntry
    password: str
    connections: Dict[str, str]
    region: str

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # instantiate LibeView and login
                libre = LibreView(
                    username=user_input[CONF_EMAIL], password=user_input[CONF_PASSWORD]
                )
                await self.hass.async_add_executor_job(libre.get_connections)
            except Exception as ex:  # pylint: disable=broad-except
                LOGGER.debug("Could not log in to LibreView, %s", ex)
                errors["base"] = "invalid_auth"
            else:
                self.email = user_input[CONF_EMAIL]
                self.password = user_input[CONF_PASSWORD]
                return await self.async_step_options()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )

    async def async_step_options(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            self.uom = user_input[CONF_UOM]
            self.sensor_duration = user_input[CONF_SENSOR_DURATION]
            self.show_trend_icon = user_input[CONF_SHOW_TREND_ARROW]
            self.region = user_input[CONF_REGION]
            return self.async_create_entry(
                title="LibreView",
                data={
                    CONF_EMAIL: self.email,
                    CONF_PASSWORD: self.password,
                    CONF_UOM: self.uom,
                    CONF_SENSOR_DURATION: int(self.sensor_duration),
                    CONF_SHOW_TREND_ARROW: bool(self.show_trend_icon),
                    CONF_REGION: self.region,
                },
            )
        return self.async_show_form(
            step_id="options",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_UOM): vol.In(GlucoseUnitOfMeasurement),
                    vol.Required(CONF_SENSOR_DURATION, default=14): int,
                    vol.Required(CONF_SHOW_TREND_ARROW, default=False): bool,
                    vol.Optional(CONF_REGION, default="Standard"): vol.In(
                        [
                            "Standard",
                            "AE",
                            "AP",
                            "AU",
                            "CA",
                            "DE",
                            "EU",
                            "EU2",
                            "FR",
                            "JP",
                            "US",
                        ]
                    ),
                },
            ),
        )

    async def async_step_reauth(self, _: dict[str, Any]) -> FlowResult:
        """Handle initiation of re-authentication with LibreView."""
        self.entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle re-authentication with LibreView."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # instantiate LibeView and login
                libre = LibreView(
                    username=user_input[CONF_EMAIL], password=user_input[CONF_PASSWORD]
                )
                await self.hass.async_add_executor_job(libre.get_connections)
            except Exception as ex:  # pylint: disable=broad-except
                LOGGER.debug("Could not log in to LibreView, %s", ex)
                errors["base"] = "invalid_auth"
            else:
                data = self.entry.data.copy()
                self.hass.config_entries.async_update_entry(
                    self.entry,
                    data={
                        **data,
                        CONF_EMAIL: user_input[CONF_EMAIL],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                    },
                )
                self.hass.async_create_task(
                    self.hass.config_entries.async_reload(self.entry.entry_id)
                )
            return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL, default=self.entry.data[CONF_EMAIL]): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlow:
        """Create the options flow."""
        return LibreViewOptionsFlowHandler(config_entry)
