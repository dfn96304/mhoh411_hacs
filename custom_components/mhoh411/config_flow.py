"""Config flow for MHO-H411."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak

from .const import CONF_ADDRESS, CONF_POLL_INTERVAL, DEFAULT_POLL_SECONDS, DOMAIN


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MHO-H411."""

    VERSION = 1

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ):
        """Handle discovery via Bluetooth."""
        address = discovery_info.address

        await self.async_set_unique_id(address)
        self._abort_if_unique_id_configured()

        title = discovery_info.name or f"MHO-H411 {address}"

        return self.async_create_entry(
            title=title,
            data={CONF_ADDRESS: address},
            options={CONF_POLL_INTERVAL: DEFAULT_POLL_SECONDS},
        )

    async def async_step_user(self, user_input=None):
        """Handle the initial step (manual add)."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_ADDRESS): str,
                        vol.Optional(CONF_POLL_INTERVAL, default=DEFAULT_POLL_SECONDS): vol.All(
                            int, vol.Range(min=5, max=3600)
                        ),
                    }
                ),
            )

        address = user_input[CONF_ADDRESS]
        poll_interval = int(user_input.get(CONF_POLL_INTERVAL, DEFAULT_POLL_SECONDS))

        await self.async_set_unique_id(address)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=f"MHO-H411 {address}",
            data={CONF_ADDRESS: address},
            options={CONF_POLL_INTERVAL: poll_interval},
        )

    @staticmethod
    @config_entries.callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for MHO-H411."""

    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self.entry = entry

    async def async_step_init(self, user_input=None):
        if user_input is None:
            current = int(self.entry.options.get(CONF_POLL_INTERVAL, DEFAULT_POLL_SECONDS))
            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema(
                    {
                        vol.Optional(CONF_POLL_INTERVAL, default=current): vol.All(
                            int, vol.Range(min=5, max=3600)
                        )
                    }
                ),
            )

        return self.async_create_entry(title="", data=user_input)
