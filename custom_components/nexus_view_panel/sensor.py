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

from .const import DOMAIN, COORDINATOR_DEVICE

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data[COORDINATOR_DEVICE]

    sensors = [
        NexusBatterySensor(coordinator, entry),
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
            "manufacturer": "smintlife.de",
        }
        self._attr_unique_id = f"{entry.entry_id}_battery"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        key_to_check = "batteryLevel"
        
        if self.coordinator.data and key_to_check in self.coordinator.data:
            return self.coordinator.data[key_to_check]
        return None
