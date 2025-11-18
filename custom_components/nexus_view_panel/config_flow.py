"""Config flow for Nexus View Panel integration."""
import json
import os
from typing import Any
from urllib.parse import parse_qs, urlparse

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_API_TOKEN, CONF_HOST, CONF_PORT
from homeassistant.data_entry_flow import AbortFlow
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import NexusViewPanelApiClient, ApiError, AuthError
from .const import (
    DOMAIN, 
    LOGGER, 
    DEVICE_UPDATE_INTERVAL,
    CONFIG_UPDATE_INTERVAL
)

MANUAL_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=8080): int,
        vol.Required(CONF_API_TOKEN): str,
    }
)

QR_DATA_SCHEMA = vol.Schema({vol.Required("qr_string"): str})


class NexusConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Nexus View Panel."""

    VERSION = 1
    
    config_data: dict[str, Any] = {}

    async def _async_validate_connection(
        self, host: str, port: int, token: str
    ) -> None:
        """
        Helper function to validate connection.
        Raises ApiError or AuthError on failure.
        """
        session = async_get_clientsession(self.hass)
        api_client = NexusViewPanelApiClient(
            host=host, port=port, token=token, session=session
        )
        await api_client.async_get_device()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Show the setup method menu."""
        return self.async_show_menu(step_id="user", menu_options=["qr", "manual"])

    async def async_step_qr(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Handle the QR string input."""
        errors: dict[str, str] = {}

        if user_input is not None:
            qr_string = user_input["qr_string"]
            try:
                parsed_url = urlparse(qr_string)
                query_params = parse_qs(parsed_url.query)

                if not (
                    parsed_url.hostname
                    and parsed_url.port
                    and "api_token" in query_params
                ):
                    raise ValueError("Incomplete URL components")

                host = parsed_url.hostname
                port = parsed_url.port
                token = query_params["api_token"][0]

                await self._async_validate_connection(host, port, token)

                await self.async_set_unique_id(f"nexus_{host}")
                self._abort_if_unique_id_configured()

                self.config_data = {
                    CONF_HOST: host,
                    CONF_PORT: port,
                    CONF_API_TOKEN: token,
                }
                
                return await self.async_step_name()

            except (ValueError, KeyError, IndexError, AttributeError):
                errors["base"] = "invalid_qr"
            except AuthError:
                errors["base"] = "invalid_auth"
            except ApiError:
                errors["base"] = "cannot_connect"
            except AbortFlow as e:
                return self.async_abort(reason=e.reason)
            except Exception as e:
                LOGGER.error(f"Unexpected error during QR setup: {e}", exc_info=True)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="qr", data_schema=QR_DATA_SCHEMA, errors=errors
        )

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Handle the manual input."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            token = user_input[CONF_API_TOKEN]

            try:
                await self._async_validate_connection(host, port, token)

                await self.async_set_unique_id(f"nexus_{host}")
                self._abort_if_unique_id_configured()

                self.config_data = {
                    CONF_HOST: host,
                    CONF_PORT: port,
                    CONF_API_TOKEN: token,
                }

                return await self.async_step_name()

            except AuthError:
                errors["base"] = "invalid_auth"
            except ApiError:
                errors["base"] = "cannot_connect"
            except AbortFlow as e:
                return self.async_abort(reason=e.reason)
            except Exception as e:
                LOGGER.error(f"Unexpected error during manual setup: {e}", exc_info=True)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="manual", data_schema=MANUAL_DATA_SCHEMA, errors=errors
        )

    async def async_step_name(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Handle the device naming and interval step."""
        
        if not self.config_data:
            return self.async_abort(reason="unknown")

        if user_input is not None:
            title = user_input["name"]
            
            self.config_data["device_interval"] = user_input["device_interval"]
            self.config_data["config_interval"] = user_input["config_interval"]
            
            return self.async_create_entry(title=title, data=self.config_data)
        
        default_name = f"Nexus Panel ({self.config_data[CONF_HOST]})"
        
        name_schema = vol.Schema(
            {
                vol.Required("name", default=default_name): str,
                vol.Required(
                    "device_interval", default=DEVICE_UPDATE_INTERVAL
                ): vol.All(vol.Coerce(int), vol.Range(min=5)),
                vol.Required(
                    "config_interval", default=CONFIG_UPDATE_INTERVAL
                ): vol.All(vol.Coerce(int), vol.Range(min=60)),
            }
        )

        return self.async_show_form(
            step_id="name", data_schema=name_schema
        )
