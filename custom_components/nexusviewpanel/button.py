"""Button platform for NexusViewPanel."""
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import NexusViewPanelApiClient
from .const import (
    DOMAIN, 
    COORDINATOR_CONFIG, 
    COORDINATOR_DEVICE, 
    NEXUS_API_CLIENT, 
    LOGGER
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    api_client = data[NEXUS_API_CLIENT]
    
    config_coordinator = data[COORDINATOR_CONFIG]
    device_coordinator = data[COORDINATOR_DEVICE]

    static_buttons = [
        NexusCloseFloatButton(api_client, entry),
        NexusGetDeviceInfoButton(device_coordinator, entry),
        NexusGetConfigButton(config_coordinator, entry),
    ]
    async_add_entities(static_buttons)

    manager = NexusTabButtonManager(entry, api_client, config_coordinator, async_add_entities)
    
    entry.async_on_unload(
        config_coordinator.async_add_listener(manager.async_update_buttons)
    )
    
    manager.async_update_buttons()


class NexusTabButtonManager:
    """Manages the creation and removal of dynamic tab buttons."""
    
    def __init__(
        self,
        entry: ConfigEntry,
        api_client: NexusViewPanelApiClient,
        coordinator: DataUpdateCoordinator,
        async_add_entities: AddEntitiesCallback
    ):
        self.entry = entry
        self.api_client = api_client
        self.coordinator = coordinator
        self.async_add_entities = async_add_entities
        self._current_tab_indices = set()

    @callback
    def async_update_buttons(self) -> None:
        """Update buttons based on coordinator data."""
        if self.coordinator.data is None:
            return

        tabs_data = self.coordinator.data.get("tabs", [])
        
        new_buttons = []
        for i, tab in enumerate(tabs_data):
            tab_index = i
            tab_title = tab.get("title", f"Tab {tab_index}")
            
            if tab_index not in self._current_tab_indices:
                LOGGER.debug(f"Creating new buttons for tab: {tab_title} (Index {tab_index})")
                new_buttons.append(NexusReloadTabButton(self.api_client, self.entry, tab_index, tab_title))
                new_buttons.append(NexusFloatTabButton(self.api_client, self.entry, tab_index, tab_title))
                self._current_tab_indices.add(tab_index)

        if new_buttons:
            self.async_add_entities(new_buttons)


class NexusBaseButton(ButtonEntity):
    """Base class for Nexus buttons."""
    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry):
        """Initialize the base button."""
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Nexus Panel ({entry.data['host']})",
            "manufacturer": "smintlife",
        }


class NexusCloseFloatButton(NexusBaseButton):
    """Button to close the floating window."""
    _attr_name = "Close Floating View"
    _attr_icon = "mdi:window-close"

    def __init__(self, api_client: NexusViewPanelApiClient, entry: ConfigEntry):
        super().__init__(entry)
        self._api_client = api_client
        self._attr_unique_id = f"{entry.entry_id}_close_float"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._api_client.async_close_floating()


class NexusReloadTabButton(NexusBaseButton):
    """Button to reload a specific tab."""
    _attr_icon = "mdi:reload"

    def __init__(self, api_client: NexusViewPanelApiClient, entry: ConfigEntry, tab_index: int, tab_title: str):
        super().__init__(entry)
        self._api_client = api_client
        self._tab_index = tab_index
        self._attr_name = f"Reload {tab_title}"
        self._attr_unique_id = f"{entry.entry_id}_reload_tab_{tab_index}"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._api_client.async_reload_tab(self._tab_index)


class NexusFloatTabButton(NexusBaseButton):
    """Button to float a specific tab."""
    _attr_icon = "mdi:picture-in-picture-top-right"

    def __init__(self, api_client: NexusViewPanelApiClient, entry: ConfigEntry, tab_index: int, tab_title: str):
        super().__init__(entry)
        self._api_client = api_client
        self._tab_index = tab_index
        self._attr_name = f"Float {tab_title}"
        self._attr_unique_id = f"{entry.entry_id}_float_tab_{tab_index}"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._api_client.async_float_tab(self._tab_index)


class NexusGetDeviceInfoButton(NexusBaseButton):
    """Button to force-refresh the device info coordinator."""
    _attr_name = "Get Device Info"
    _attr_icon = "mdi:update"

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry):
        """Initialize the button."""
        super().__init__(entry)
        self.coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_get_device_info"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_request_refresh()


class NexusGetConfigButton(NexusBaseButton):
    """Button to force-refresh the config coordinator."""
    _attr_name = "Get Config"
    _attr_icon = "mdi:update"

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry):
        """Initialize the button."""
        super().__init__(entry)
        self.coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_get_config"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.async_request_refresh()
