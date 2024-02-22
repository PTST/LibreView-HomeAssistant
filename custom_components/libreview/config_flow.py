"""Config flow for LibreView integration."""

from __future__ import annotations

from typing import Any, List
from uuid import UUID
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.config_entries import ConfigEntry, ConfigFlow
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_GIID,
    DOMAIN,
    LOGGER,
)

from LibreView import LibreView


class LibreViewConfigFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for LibreView."""

    VERSION = 1

    email: str
    entry: ConfigEntry
    password: str
    connections: Dict[str, str]

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # instantiate LibeView and login
                libre = LibreView(username=user_input[CONF_EMAIL], password=user_input[CONF_PASSWORD])
                await self.hass.async_add_executor_job(libre.get_connections)
            except Exception as ex:
                LOGGER.debug("Could not log in to LibreView, %s", ex)
                errors["base"] = "invalid_auth"
            else:
                self.email = user_input[CONF_EMAIL]
                self.password = user_input[CONF_PASSWORD]
                return self.async_create_entry(
                    title="LibreView",
                    data={
                        CONF_EMAIL: self.email,
                        CONF_PASSWORD: self.password,
                    },
                )

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

    async def async_step_reauth(self, data: dict[str, Any]) -> FlowResult:
        """Handle initiation of re-authentication with LibreView."""
        self.entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle re-authentication with LibreView."""
        errors: dict[str, str] = {}

        if user_input is not None:
            alarm = Alarm(
                username=user_input[CONF_EMAIL], password=user_input[CONF_PASSWORD]
            )
            try:
                await self.hass.async_add_executor_job(alarm.update_status)
            except Exception as ex:
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
