"""Sensor platform for NexusViewPanel."""
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, COORDINATOR_DEVICE, COORDINATOR_STATUS

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data[COORDINATOR_DEVICE]
    status_coordinator = data[COORDINATOR_STATUS]

    sensors = [
        NexusBatterySensor(coordinator, entry),
        NexusActiveTabSensor(status_coordinator, entry),
    ]
    async_add_entities(sensors)


class NexusBatterySensor(CoordinatorEntity, SensorEntity):
    """Represents the device battery sensor."""

    _attr_has_entity_name = True
    _attr_name = "Battery"
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator, entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Nexus Panel ({entry.data['host']})",
            "manufacturer": "smintlife",
        }
        self._attr_unique_id = f"{entry.entry_id}_battery"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        key_to_check = "batteryLevel"
        
        if self.coordinator.data and key_to_check in self.coordinator.data:
            return self.coordinator.data[key_to_check]
        return None


class NexusActiveTabSensor(CoordinatorEntity, SensorEntity):
    """Represents the currently active tab title."""

    _attr_has_entity_name = True
    _attr_name = "Active Tab"
    _attr_icon = "mdi:tab"

    def __init__(self, coordinator, entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(coordinator)

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Nexus Panel ({entry.data['host']})",
            "manufacturer": "smintlife",
        }
        self._attr_unique_id = f"{entry.entry_id}_active_tab"

    @property
    def native_value(self) -> str | None:
        """Return the active tab title."""
        if self.coordinator.data:
            return self.coordinator.data.get("activeTabTitle")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, str | int | bool]:
        """Return additional state attributes."""
        if self.coordinator.data:
            return {
                "active_tab_index": self.coordinator.data.get("activeTabIndex"),
                "is_floating_tab_active": self.coordinator.data.get("isFloatingTabActive"),
            }
        return {}
