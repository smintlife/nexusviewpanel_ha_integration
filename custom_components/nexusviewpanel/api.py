"""API Client for NexusViewPanel."""
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
                
                response.raise_for_status() 
                
                if response.status == 200:
                    if response.content_type == "application/json":
                        json_data = await response.json()
                        LOGGER.debug(f"Response JSON: {json_data}")
                        return json_data
                    else:
                        text_data = await response.text()
                        LOGGER.warning(
                            f"API-Anfrage an {url} war erfolgreich (Status 200), aber der Content-Type ist '{response.content_type}', nicht 'application/json'. "
                            f"Empfangener Text: {text_data}"
                        )
                        return None
                
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

    async def async_get_device(self) -> dict[str, Any]:
        """Get device status (battery, brightness, etc.)."""
        return await self._request("GET", "/device")

    async def async_get_config(self) -> dict[str, Any]:
        """Get the full app configuration."""
        return await self._request("GET", "/config")
    
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

    async def async_get_tabs(self) -> list[dict[str, Any]]:
        """Get all configured tabs."""
        return await self._request("GET", "/tabs")

    async def async_get_tab(self, tab_index: int) -> dict[str, Any]:
        """Get a single tab by index."""
        return await self._request("GET", f"/tabs/{tab_index}")

    async def async_get_status(self) -> dict[str, Any]:
        """Get app status (active tab, floating view state)."""
        return await self._request("GET", "/status")

    async def async_get_version(self) -> dict[str, Any]:
        """Get app version info."""
        return await self._request("GET", "/version")

    async def async_select_tab(self, tab_index: int) -> None:
        """Select/switch to a tab."""
        await self._request("POST", f"/tabs/{tab_index}/select")

    async def async_update_webview_tab(
        self,
        tab_index: int,
        title: str | None = None,
        url: str | None = None,
        scale: int | None = None,
        offset_x: int | None = None,
        offset_y: int | None = None,
    ) -> None:
        """Update an existing WebView tab."""
        body = {}
        if title is not None:
            body["title"] = title
        if url is not None:
            body["url"] = url
        if scale is not None:
            body["scale"] = scale
        if offset_x is not None:
            body["offsetX"] = offset_x
        if offset_y is not None:
            body["offsetY"] = offset_y
        await self._request("POST", f"/tabs/{tab_index}/update_webview", json=body)

    async def async_update_rtsp_tab(
        self,
        tab_index: int,
        title: str | None = None,
        url: str | None = None,
        rtsp_transport: str | None = None,
        rtsp_decoder: str | None = None,
        audio_enabled: bool | None = None,
    ) -> None:
        """Update an existing RTSP tab."""
        body = {}
        if title is not None:
            body["title"] = title
        if url is not None:
            body["url"] = url
        if rtsp_transport is not None:
            body["rtspTransport"] = rtsp_transport
        if rtsp_decoder is not None:
            body["rtspDecoder"] = rtsp_decoder
        if audio_enabled is not None:
            body["audioEnabled"] = audio_enabled
        await self._request("POST", f"/tabs/{tab_index}/update_rtsp", json=body)

    async def async_reload_all(self) -> None:
        """Reload all tabs."""
        await self._request("POST", "/reload/all")
