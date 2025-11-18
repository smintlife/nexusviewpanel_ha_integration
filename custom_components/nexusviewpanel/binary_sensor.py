"""Binary sensor platform for NexusViewPanel."""
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, COORDINATOR_CONFIG

CONFIG_SENSORS = [
    ("kioskMode", "Kiosk Mode", "mdi:lock", None),
    ("fullscreen", "Fullscreen", "mdi:fullscreen", None),
    ("reloadOnTabReselect", "Reload on Reselect", "mdi:reload", None),
    ("reloadOnSwipe", "Reload on Swipe", "mdi:reload", None),
    ("reloadOnWakeup", "Reload on Wakeup", "mdi:reload", None),
    ("runOnReboot", "Run on Reboot", "mdi:power", None),
    ("deviceAdminLock", "Device Admin Lock", "mdi:shield-lock", BinarySensorDeviceClass.LOCK),
    ("tabsSwipable", "Tabs Swipable", "mdi:arrow-left-right", None),
]

NESTED_CONFIG_SENSORS = [
    (("floatingView", "enabled"), "Floating View Enabled", "mdi:picture-in-picture-top-right", None),
    (("pinProtection", "enabled"), "PIN Protection", "mdi:lock-pattern", BinarySensorDeviceClass.LOCK),
]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data[COORDINATOR_CONFIG]

    sensors_to_add = []

    for key, name, icon, dev_class in CONFIG_SENSORS:
        sensors_to_add.append(
            NexusConfigBinarySensor(coordinator, entry, key, name, icon, dev_class)
        )
            
    for (key1, key2), name, icon, dev_class in NESTED_CONFIG_SENSORS:
         sensors_to_add.append(
            NexusNestedConfigBinarySensor(coordinator, entry, key1, key2, name, icon, dev_class)
        )

    async_add_entities(sensors_to_add)


class NexusConfigBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Represents a boolean setting from the /api/config endpoint."""

    _attr_has_entity_name = True
    _attr_entity_registry_enabled_default = True

    def __init__(self, coordinator, entry, data_key, name, icon, device_class):
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._data_key = data_key
        self._attr_name = name
        self._attr_icon = icon
        self._attr_device_class = device_class
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Nexus Panel ({entry.data['host']})",
            "manufacturer": "smintlife.de",
        }
        self._attr_unique_id = f"{entry.entry_id}_config_{data_key}"

    @property
    def is_on(self) -> bool | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get(self._data_key)
        return None

class NexusNestedConfigBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Represents a nested boolean setting from the /api/config endpoint."""

    _attr_has_entity_name = True
    _attr_entity_registry_enabled_default = True

    def __init__(self, coordinator, entry, key1, key2, name, icon, device_class):
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._key1 = key1
        self._key2 = key2
        self._attr_name = name
        self._attr_icon = icon
        self._attr_device_class = device_class
        
        self._attr_device_info = { "identifiers": {(DOMAIN, entry.entry_id)} }
        self._attr_unique_id = f"{entry.entry_id}_config_{key1}_{key2}"

    @property
    def is_on(self) -> bool | None:
        """Return the state of the sensor."""
        if self.coordinator.data:
            try:
                return self.coordinator.data[self._key1][self._key2]
            except (KeyError, TypeError):
                return None
        return None
