"""Config flow for Nexus View Panel integration."""
from typing import Any
from urllib.parse import parse_qs, urlparse

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, AbortFlow
from homeassistant.const import CONF_API_TOKEN, CONF_HOST, CONF_PORT
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import NexusViewPanelApiClient, ApiError, AuthError
from .const import DOMAIN, LOGGER

# Schema for the manual input form
MANUAL_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=8080): int,
        vol.Required(CONF_API_TOKEN): str,
    }
)

# Schema for the QR string input form
QR_DATA_SCHEMA = vol.Schema({vol.Required("qr_string"): str})


class NexusConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Nexus View Panel."""

    VERSION = 1
    
    # Class variable to hold data between steps
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
        # Test the connection by fetching device info
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
                # Parse the URL: "http://<ip>:<port>/swagger?api_token=<token>"
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

                # Validate connection
                await self._async_validate_connection(host, port, token)

                # Set unique ID and check if already configured
                await self.async_set_unique_id(f"nexus_{host}")
                self._abort_if_unique_id_configured()

                # Store data for the next step
                self.config_data = {
                    CONF_HOST: host,
                    CONF_PORT: port,
                    CONF_API_TOKEN: token,
                }
                
                # Proceed to the naming step
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

        # Show the QR input form
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
                # Validate connection
                await self._async_validate_connection(host, port, token)

                # Set unique ID and check if already configured
                await self.async_set_unique_id(f"nexus_{host}")
                self._abort_if_unique_id_configured()

                # Store data for the next step
                self.config_data = {
                    CONF_HOST: host,
                    CONF_PORT: port,
                    CONF_API_TOKEN: token,
                }

                # Proceed to the naming step
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

        # Show the manual input form
        return self.async_show_form(
            step_id="manual", data_schema=MANUAL_DATA_SCHEMA, errors=errors
        )

    async def async_step_name(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Handle the device naming step."""
        
        # This step should only be reached after config_data is set
        if not self.config_data:
            # This should not happen, but as a safeguard:
            return self.async_abort(reason="unknown")

        if user_input is not None:
            # User has submitted a name, create the entry
            title = user_input["name"]
            return self.async_create_entry(title=title, data=self.config_data)

        # Show the naming form
        # Suggest a default name, e.g., "Nexus Panel (192.168.1.50)"
        default_name = f"Nexus Panel ({self.config_data[CONF_HOST]})"
        
        name_schema = vol.Schema(
            {vol.Required("name", default=default_name): str}
        )

        return self.async_show_form(
            step_id="name", data_schema=name_schema
        )
