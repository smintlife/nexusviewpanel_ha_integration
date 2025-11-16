"""The Nexus View Panel integration."""
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_TOKEN, CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import NexusViewPanelApiClient, ApiError
from .const import (
    DOMAIN,
    LOGGER,
    COORDINATOR_DEVICE,
    COORDINATOR_CONFIG,
    NEXUS_API_CLIENT,
    DEVICE_UPDATE_INTERVAL,
    CONFIG_UPDATE_INTERVAL,
)

# Define the platforms we want to support
PLATFORMS: list[Platform] = [
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Nexus View Panel from a config entry."""

    api_client = NexusViewPanelApiClient(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        token=entry.data[CONF_API_TOKEN],
        session=async_get_clientsession(hass),
    )

    # --- Coordinator for Device Status (polled frequently) ---
    async def async_update_device_data():
        """Fetch data from /api/device."""
        try:
            return await api_client.async_get_device()
        except ApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    device_coordinator = DataUpdateCoordinator(
        hass,
        LOGGER,
        name=f"{DOMAIN}_device_status",
        update_method=async_update_device_data,
        update_interval=timedelta(seconds=DEVICE_UPDATE_INTERVAL),
    )

    # --- Coordinator for Config (polled infrequently) ---
    async def async_update_config_data():
        """Fetch data from /api/config."""
        try:
            return await api_client.async_get_config()
        except ApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    config_coordinator = DataUpdateCoordinator(
        hass,
        LOGGER,
        name=f"{DOMAIN}_config",
        update_method=async_update_config_data,
        update_interval=timedelta(seconds=CONFIG_UPDATE_INTERVAL),
    )
    
    # Fetch initial data for both coordinators
    await device_coordinator.async_config_entry_first_refresh()
    await config_coordinator.async_config_entry_first_refresh()

    # Store the API client and coordinators in hass.data
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        NEXUS_API_CLIENT: api_client,
        COORDINATOR_DEVICE: device_coordinator,
        COORDINATOR_CONFIG: config_coordinator,
    }

    # Forward the setup to our entity platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
