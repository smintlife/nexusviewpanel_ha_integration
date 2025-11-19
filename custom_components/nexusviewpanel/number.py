"""Number platform for NexusViewPanel."""
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, COORDINATOR_CONFIG, NEXUS_API_CLIENT

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        NexusBrightnessNumber(
            coordinator=data[COORDINATOR_CONFIG],
            api_client=data[NEXUS_API_CLIENT],
            entry=entry,
        )
    ])


class NexusBrightnessNumber(CoordinatorEntity, NumberEntity):
    """Represents the brightness setting slider."""

    _attr_has_entity_name = True
    _attr_name = "Configured Brightness"
    _attr_icon = "mdi:brightness-5"
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator, api_client, entry: ConfigEntry):
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._api_client = api_client
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Nexus Panel ({entry.data['host']})",
            "manufacturer": "smintlife",
        }
        self._attr_unique_id = f"{entry.entry_id}_brightness"

    @property
    def native_value(self) -> float | None:
        """Return the current brightness setting."""
        if self.coordinator.data and "brightness" in self.coordinator.data:
            return self.coordinator.data["brightness"]
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Update the brightness setting."""
        await self._api_client.async_set_brightness(int(value))
        await self.coordinator.async_request_refresh()
