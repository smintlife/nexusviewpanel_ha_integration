"""Constants for the Nexus View Panel integration."""
from logging import getLogger

DOMAIN = "nexus_view_panel"
LOGGER = getLogger(__package__)

# Coordinator update intervals
DEVICE_UPDATE_INTERVAL = 30  # Poll device status (battery) every 30 seconds
CONFIG_UPDATE_INTERVAL = 300 # Poll config (tabs, settings) every 5 minutes

# Data keys
COORDINATOR_DEVICE = "device_coordinator"
COORDINATOR_CONFIG = "config_coordinator"
NEXUS_API_CLIENT = "api_client"
