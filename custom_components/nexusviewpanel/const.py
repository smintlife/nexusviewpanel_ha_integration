"""Constants for the NexusViewPanel integration."""
from logging import getLogger

DOMAIN = "nexusviewpanel"
LOGGER = getLogger(__package__)

DEVICE_UPDATE_INTERVAL = 60
CONFIG_UPDATE_INTERVAL = 300

COORDINATOR_DEVICE = "device_coordinator"
COORDINATOR_CONFIG = "config_coordinator"
NEXUS_API_CLIENT = "api_client"
