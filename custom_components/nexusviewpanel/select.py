"""Select platform for NexusViewPanel."""
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import NexusViewPanelApiClient
from .const import DOMAIN, COORDINATOR_CONFIG, COORDINATOR_STATUS, NEXUS_API_CLIENT, LOGGER


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    api_client = data[NEXUS_API_CLIENT]
    config_coordinator = data[COORDINATOR_CONFIG]
    status_coordinator = data[COORDINATOR_STATUS]

    async_add_entities([
        NexusTabSelect(config_coordinator, status_coordinator, api_client, entry),
    ])


class NexusTabSelect(CoordinatorEntity, SelectEntity):
    """Select entity to switch the active tab."""

    _attr_has_entity_name = True
    _attr_name = "Active Tab"
    _attr_icon = "mdi:tab"

    def __init__(self, config_coordinator, status_coordinator, api_client: NexusViewPanelApiClient, entry: ConfigEntry):
        """Initialize the tab select."""
        super().__init__(config_coordinator)
        self._status_coordinator = status_coordinator
        self._api_client = api_client
        self._entry = entry

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Nexus Panel ({entry.data['host']})",
            "manufacturer": "smintlife",
        }
        self._attr_unique_id = f"{entry.entry_id}_tab_select"

        entry.async_on_unload(
            status_coordinator.async_add_listener(self._handle_status_update)
        )

    @callback
    def _handle_status_update(self) -> None:
        """Handle status coordinator update."""
        self.async_write_ha_state()

    @property
    def options(self) -> list[str]:
        """Return the list of tab titles."""
        if self.coordinator.data is None:
            return []
        tabs = self.coordinator.data.get("tabs", [])
        return [tab.get("title", f"Tab {i}") for i, tab in enumerate(tabs)]

    @property
    def current_option(self) -> str | None:
        """Return the currently active tab title."""
        if self._status_coordinator.data is None:
            return None
        active_index = self._status_coordinator.data.get("activeTabIndex")
        if active_index is None:
            return None
        tabs = self.coordinator.data.get("tabs", []) if self.coordinator.data else []
        if 0 <= active_index < len(tabs):
            return tabs[active_index].get("title", f"Tab {active_index}")
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the active tab."""
        if self.coordinator.data is None:
            return
        tabs = self.coordinator.data.get("tabs", [])
        for i, tab in enumerate(tabs):
            if tab.get("title", f"Tab {i}") == option:
                await self._api_client.async_select_tab(i)
                await self._status_coordinator.async_request_refresh()
                return
        LOGGER.warning(f"Tab '{option}' not found")
