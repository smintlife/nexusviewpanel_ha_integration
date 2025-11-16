"""API Client for Nexus View Panel."""
import asyncio
from typing import Any
from aiohttp import ClientSession, ClientResponseError

from .const import LOGGER

# Define custom exceptions
class ApiError(Exception):
    """Exception to indicate a general API error."""

class AuthError(ApiError):
    """Exception to indicate an authentication error."""


class NexusViewPanelApiClient:
    """Class to manage API calls."""

    def __init__(
        self, host: str, port: int, token: str, session: ClientSession
    ) -> None:
        """Initialize the API client."""
        self._base_url = f"http://{host}:{port}/api"
        self._headers = {"Authorization": f"Bearer {token}"}
        self._session = session

    async def _request(self, method: str, path: str, **kwargs) -> dict[str, Any] | None:
        """Make an API request."""
        url = f"{self._base_url}{path}"
        
        LOGGER.debug(f"Sending {method} to {url} with data: {kwargs.get('json') or kwargs.get('params')}")

        try:
            async with self._session.request(
                method, url, headers=self._headers, timeout=10, **kwargs
            ) as response:
                
                LOGGER.debug(f"Response status from {url}: {response.status}")
                LOGGER.debug(f"Response content-type: {response.content_type}")
                
                # Hebe den Fehler für 4xx/5xx-Status hervor
                response.raise_for_status() 
                
                if response.status == 200:
                    if response.content_type == "application/json":
                        json_data = await response.json()
                        LOGGER.debug(f"Response JSON: {json_data}")
                        return json_data
                    else:
                        # API hat 200 OK zurückgegeben, aber nicht als JSON. Das ist das Problem!
                        text_data = await response.text()
                        LOGGER.warning(
                            f"API-Anfrage an {url} war erfolgreich (Status 200), aber der Content-Type ist '{response.content_type}', nicht 'application/json'. "
                            f"Empfangener Text: {text_data}"
                        )
                        return None # Gib None zurück, aber wir wissen jetzt warum
                
                return None

        except ClientResponseError as err:
            if err.status == 401 or err.status == 403:
                LOGGER.error("Authentifizierungsfehler: API-Token prüfen.")
                raise AuthError("Authentifizierung fehlgeschlagen") from err
            else:
                LOGGER.error(f"API-Anfrage fehlgeschlagen (ClientResponseError): {err}")
                raise ApiError(f"API-Anfrage fehlgeschlagen: {err}") from err
        except asyncio.TimeoutError:
            LOGGER.error(f"Timeout beim Verbinden mit {url}")
            raise ApiError("Anfrage-Timeout") from None
        except Exception as e:
            LOGGER.error(f"Unerwarteter Fehler bei der API-Anfrage: {e}")
            raise ApiError(f"Unerwarteter API-Fehler: {e}") from e

    # --- GET Endpoints ---

    async def async_get_device(self) -> dict[str, Any]:
        """Get device status (battery, brightness, etc.)."""
        return await self._request("GET", "/device")

    async def async_get_config(self) -> dict[str, Any]:
        """Get the full app configuration."""
        return await self._request("GET", "/config")

    # --- POST Endpoints (Commands) ---
    
    async def async_display_on(self) -> None:
        """Turn the display on."""
        await self._request("POST", "/display/on")

    async def async_display_off(self) -> None:
        """Turn the display off."""
        await self._request("POST", "/display/off")

    async def async_set_brightness(self, brightness: int) -> None:
        """Set display brightness (0-100)."""
        await self._request("POST", "/display/brightness", params={"value": brightness})

    async def async_close_floating(self) -> None:
        """Close the floating window."""
        await self._request("POST", "/floating/close")

    async def async_float_tab(self, tab_index: int) -> None:
        """Float a specific tab."""
        await self._request("POST", f"/tabs/{tab_index}/float")

    async def async_reload_tab(self, tab_index: int) -> None:
        """Reload a specific tab."""
        await self._request("POST", f"/tabs/{tab_index}/reload")
