"""Services for NexusViewPanel integration."""
from typing import Any

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import config_validation as cv

from .api import NexusViewPanelApiClient, ApiError
from .const import DOMAIN, LOGGER, NEXUS_API_CLIENT

SERVICE_SELECT_TAB = "select_tab"
SERVICE_RELOAD_TAB = "reload_tab"
SERVICE_FLOAT_TAB = "float_tab"
SERVICE_RELOAD_ALL_TABS = "reload_all_tabs"
SERVICE_UPDATE_WEBVIEW_TAB = "update_webview_tab"
SERVICE_UPDATE_RTSP_TAB = "update_rtsp_tab"

ATTR_TAB_INDEX = "tab_index"
ATTR_TITLE = "title"
ATTR_URL = "url"
ATTR_SCALE = "scale"
ATTR_OFFSET_X = "offset_x"
ATTR_OFFSET_Y = "offset_y"
ATTR_RTSP_TRANSPORT = "rtsp_transport"
ATTR_RTSP_DECODER = "rtsp_decoder"
ATTR_AUDIO_ENABLED = "audio_enabled"

SCHEMA_TAB_INDEX = vol.Schema({
    vol.Required(ATTR_TAB_INDEX): vol.All(vol.Coerce(int), vol.Range(min=0)),
})

SCHEMA_UPDATE_WEBVIEW = vol.Schema({
    vol.Required(ATTR_TAB_INDEX): vol.All(vol.Coerce(int), vol.Range(min=0)),
    vol.Optional(ATTR_TITLE): cv.string,
    vol.Optional(ATTR_URL): cv.string,
    vol.Optional(ATTR_SCALE): vol.All(vol.Coerce(int), vol.Range(min=1)),
    vol.Optional(ATTR_OFFSET_X): vol.Coerce(int),
    vol.Optional(ATTR_OFFSET_Y): vol.Coerce(int),
})

SCHEMA_UPDATE_RTSP = vol.Schema({
    vol.Required(ATTR_TAB_INDEX): vol.All(vol.Coerce(int), vol.Range(min=0)),
    vol.Optional(ATTR_TITLE): cv.string,
    vol.Optional(ATTR_URL): cv.string,
    vol.Optional(ATTR_RTSP_TRANSPORT): vol.In(["AUTO", "UDP", "TCP"]),
    vol.Optional(ATTR_RTSP_DECODER): vol.In(["AUTO", "SOFTWARE", "HARDWARE"]),
    vol.Optional(ATTR_AUDIO_ENABLED): cv.boolean,
})


def _get_api_client(hass: HomeAssistant) -> NexusViewPanelApiClient | None:
    """Get the API client from the first config entry."""
    if DOMAIN not in hass.data:
        return None
    for entry_data in hass.data[DOMAIN].values():
        return entry_data[NEXUS_API_CLIENT]
    return None


@callback
def async_register_services(hass: HomeAssistant) -> None:
    """Register all services."""

    async def handle_select_tab(call: ServiceCall) -> None:
        """Handle the select_tab service call."""
        api_client = _get_api_client(hass)
        if api_client is None:
            LOGGER.error("No NexusViewPanel API client available")
            return
        tab_index = call.data[ATTR_TAB_INDEX]
        try:
            await api_client.async_select_tab(tab_index)
        except ApiError as err:
            LOGGER.error(f"Failed to select tab {tab_index}: {err}")

    async def handle_reload_tab(call: ServiceCall) -> None:
        """Handle the reload_tab service call."""
        api_client = _get_api_client(hass)
        if api_client is None:
            LOGGER.error("No NexusViewPanel API client available")
            return
        tab_index = call.data[ATTR_TAB_INDEX]
        try:
            await api_client.async_reload_tab(tab_index)
        except ApiError as err:
            LOGGER.error(f"Failed to reload tab {tab_index}: {err}")

    async def handle_float_tab(call: ServiceCall) -> None:
        """Handle the float_tab service call."""
        api_client = _get_api_client(hass)
        if api_client is None:
            LOGGER.error("No NexusViewPanel API client available")
            return
        tab_index = call.data[ATTR_TAB_INDEX]
        try:
            await api_client.async_float_tab(tab_index)
        except ApiError as err:
            LOGGER.error(f"Failed to float tab {tab_index}: {err}")

    async def handle_reload_all_tabs(call: ServiceCall) -> None:
        """Handle the reload_all_tabs service call."""
        api_client = _get_api_client(hass)
        if api_client is None:
            LOGGER.error("No NexusViewPanel API client available")
            return
        try:
            await api_client.async_reload_all()
        except ApiError as err:
            LOGGER.error(f"Failed to reload all tabs: {err}")

    async def handle_update_webview_tab(call: ServiceCall) -> None:
        """Handle the update_webview_tab service call."""
        api_client = _get_api_client(hass)
        if api_client is None:
            LOGGER.error("No NexusViewPanel API client available")
            return
        tab_index = call.data[ATTR_TAB_INDEX]
        try:
            await api_client.async_update_webview_tab(
                tab_index=tab_index,
                title=call.data.get(ATTR_TITLE),
                url=call.data.get(ATTR_URL),
                scale=call.data.get(ATTR_SCALE),
                offset_x=call.data.get(ATTR_OFFSET_X),
                offset_y=call.data.get(ATTR_OFFSET_Y),
            )
        except ApiError as err:
            LOGGER.error(f"Failed to update WebView tab {tab_index}: {err}")

    async def handle_update_rtsp_tab(call: ServiceCall) -> None:
        """Handle the update_rtsp_tab service call."""
        api_client = _get_api_client(hass)
        if api_client is None:
            LOGGER.error("No NexusViewPanel API client available")
            return
        tab_index = call.data[ATTR_TAB_INDEX]
        try:
            await api_client.async_update_rtsp_tab(
                tab_index=tab_index,
                title=call.data.get(ATTR_TITLE),
                url=call.data.get(ATTR_URL),
                rtsp_transport=call.data.get(ATTR_RTSP_TRANSPORT),
                rtsp_decoder=call.data.get(ATTR_RTSP_DECODER),
                audio_enabled=call.data.get(ATTR_AUDIO_ENABLED),
            )
        except ApiError as err:
            LOGGER.error(f"Failed to update RTSP tab {tab_index}: {err}")

    hass.services.async_register(DOMAIN, SERVICE_SELECT_TAB, handle_select_tab, schema=SCHEMA_TAB_INDEX)
    hass.services.async_register(DOMAIN, SERVICE_RELOAD_TAB, handle_reload_tab, schema=SCHEMA_TAB_INDEX)
    hass.services.async_register(DOMAIN, SERVICE_FLOAT_TAB, handle_float_tab, schema=SCHEMA_TAB_INDEX)
    hass.services.async_register(DOMAIN, SERVICE_RELOAD_ALL_TABS, handle_reload_all_tabs, schema=vol.Schema({}))
    hass.services.async_register(DOMAIN, SERVICE_UPDATE_WEBVIEW_TAB, handle_update_webview_tab, schema=SCHEMA_UPDATE_WEBVIEW)
    hass.services.async_register(DOMAIN, SERVICE_UPDATE_RTSP_TAB, handle_update_rtsp_tab, schema=SCHEMA_UPDATE_RTSP)
