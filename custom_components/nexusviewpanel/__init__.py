"""The NexusViewPanel integration."""
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
    COORDINATOR_STATUS,
    NEXUS_API_CLIENT,
    DEVICE_UPDATE_INTERVAL,
    CONFIG_UPDATE_INTERVAL,
    STATUS_UPDATE_INTERVAL,
)
from .services import async_register_services

PLATFORMS: list[Platform] = [
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.SELECT,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up NexusViewPanel from a config entry."""

    api_client = NexusViewPanelApiClient(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        token=entry.data[CONF_API_TOKEN],
        session=async_get_clientsession(hass),
    )
    
    device_interval = entry.data.get("device_interval", DEVICE_UPDATE_INTERVAL)
    config_interval = entry.data.get("config_interval", CONFIG_UPDATE_INTERVAL)
    status_interval = entry.data.get("status_interval", STATUS_UPDATE_INTERVAL)

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
        update_interval=timedelta(seconds=device_interval),
    )

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
        update_interval=timedelta(seconds=config_interval),
    )

    async def async_update_status_data():
        """Fetch data from /api/status."""
        try:
            return await api_client.async_get_status()
        except ApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    status_coordinator = DataUpdateCoordinator(
        hass,
        LOGGER,
        name=f"{DOMAIN}_status",
        update_method=async_update_status_data,
        update_interval=timedelta(seconds=status_interval),
    )
    
    await device_coordinator.async_config_entry_first_refresh()
    await config_coordinator.async_config_entry_first_refresh()
    await status_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        NEXUS_API_CLIENT: api_client,
        COORDINATOR_DEVICE: device_coordinator,
        COORDINATOR_CONFIG: config_coordinator,
        COORDINATOR_STATUS: status_coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async_register_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
