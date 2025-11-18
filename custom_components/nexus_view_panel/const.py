"""Constants for the Nexus View Panel integration."""
from logging import getLogger

DOMAIN = "nexus_view_panel"
LOGGER = getLogger(__package__)

DEVICE_UPDATE_INTERVAL = 60
CONFIG_UPDATE_INTERVAL = 300

COORDINATOR_DEVICE = "device_coordinator"
COORDINATOR_CONFIG = "config_coordinator"
NEXUS_API_CLIENT = "api_client"
