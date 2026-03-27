"""Constants for the NexusViewPanel integration."""
from logging import getLogger

DOMAIN = "nexusviewpanel"
LOGGER = getLogger(__package__)

DEVICE_UPDATE_INTERVAL = 60
CONFIG_UPDATE_INTERVAL = 300
STATUS_UPDATE_INTERVAL = 30

COORDINATOR_DEVICE = "device_coordinator"
COORDINATOR_CONFIG = "config_coordinator"
COORDINATOR_STATUS = "status_coordinator"
NEXUS_API_CLIENT = "api_client"
