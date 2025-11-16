"""Config flow for Nexus View Panel integration."""
from typing import Any
from urllib.parse import parse_qs

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_API_TOKEN, CONF_HOST, CONF_PORT
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import NexusViewPanelApiClient, ApiError, AuthError
from .const import DOMAIN, LOGGER

# Schema for the user input form
DATA_SCHEMA = vol.Schema({vol.Required("qr_string"): str})


class NexusConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Nexus View Panel."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            qr_string = user_input["qr_string"]
            
            try:
                # Parse the key-value string:
                # "api_server=1.2.3.4&api_port=80&api_token=abc"
                parsed_data = parse_qs(qr_string)

                if (
                    "api_server" not in parsed_data
                    or "api_port" not in parsed_data
                    or "api_token" not in parsed_data
                ):
                    raise ValueError("Missing required keys in QR string")

                host = parsed_data["api_server"][0]
                port = int(parsed_data["api_port"][0])
                token = parsed_data["api_token"][0]

                # Store the parsed data
                self.data = {
                    CONF_HOST: host,
                    CONF_PORT: port,
                    CONF_API_TOKEN: token,
                }

            except Exception as e:
                LOGGER.warning(f"Failed to parse QR string: {e}")
                errors["base"] = "invalid_qr"
                
            if not errors:
                try:
                    # Get an HTTP session and create our API client
                    session = async_get_clientsession(self.hass)
                    api_client = NexusViewPanelApiClient(
                        host=self.data[CONF_HOST],
                        port=self.data[CONF_PORT],
                        token=self.data[CONF_API_TOKEN],
                        session=session,
                    )

                    # Test the connection by fetching device info
                    # We can use /api/device or /api/config. /api/device is fine.
                    device_info = await api_client.async_get_device()
                    
                    await self.async_set_unique_id(f"nexus_{self.data[CONF_HOST]}")
                    self._abort_if_unique_id_configured()

                    # Data is valid, create the config entry
                    return self.async_create_entry(
                        title=f"Nexus Panel ({self.data[CONF_HOST]})", data=self.data
                    )

                except AuthError:
                    errors["base"] = "invalid_auth"
                except ApiError:
                    errors["base"] = "cannot_connect"
                except Exception as e:
                    LOGGER.error(f"Unexpected error during setup: {e}", exc_info=True)
                    errors["base"] = "cannot_connect"

        # Show the form to the user
        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
