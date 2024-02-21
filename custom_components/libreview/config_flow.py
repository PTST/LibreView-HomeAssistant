"""Config flow for LibreView integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_GIID,
    DOMAIN,
    LOGGER,
)


class LibreViewConfigFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for LibreView."""

    VERSION = 1

    email: str
    entry: ConfigEntry
    password: str

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # instantiate LibeView and login
                # libre = ...
                await self.hass.async_add_executor_job(libre)
            except Exception as ex:
                LOGGER.debug("Could not log in to LibreView, %s", ex)
                errors["base"] = "invalid_auth"
            else:
                self.email = user_input[CONF_EMAIL]
                self.password = user_input[CONF_PASSWORD]
                return await self.async_step_installation()

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

    async def async_step_installation(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Select LibreView users to add."""
        if len(self.installations) == 1:
            user_input = {CONF_GIID: list(self.installations)[0]}

        if user_input is None:
            return self.async_show_form(
                step_id="installation",
                data_schema=vol.Schema(
                    {vol.Required(CONF_GIID): vol.In(self.installations)}
                ),
            )

        await self.async_set_unique_id(user_input[CONF_GIID])
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=self.installations[user_input[CONF_GIID]],
            data={
                CONF_EMAIL: self.email,
                CONF_PASSWORD: self.password,
                CONF_GIID: user_input[CONF_GIID],
            },
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
