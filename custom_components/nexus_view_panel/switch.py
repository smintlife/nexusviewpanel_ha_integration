"""Switch platform for Nexus View Panel."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import NexusViewPanelApiClient
from .const import DOMAIN, NEXUS_API_CLIENT

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    api_client = data[NEXUS_API_CLIENT]
    
    async_add_entities([
        NexusDisplaySwitch(api_client, entry)
    ])


class NexusDisplaySwitch(SwitchEntity):
    """Represents the display On/Off switch."""

    _attr_has_entity_name = True
    _attr_name = "Display"
    _attr_icon = "mdi:tablet-dashboard"
    
    # This is an "optimistic" switch. We don't poll its state.
    # We assume it's in the state we last set it to.
    _attr_assumed_state = True

    def __init__(self, api_client: NexusViewPanelApiClient, entry: ConfigEntry):
        """Initialize the switch."""
        self._api_client = api_client
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Nexus Panel ({entry.data['host']})",
            "manufacturer": "smintlife.de",
        }
        self._attr_unique_id = f"{entry.entry_id}_display_switch"

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the display on."""
        await self._api_client.async_display_on()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the display off."""
        await self._api_client.async_display_off()
