"""Constants for the MHO-H411 integration."""

DOMAIN = "mhoh411"

CONF_ADDRESS = "address"
CONF_POLL_INTERVAL = "poll_interval"

DEFAULT_POLL_SECONDS = 30

# GATT UUIDs (from elsemieni-mho-h411)
UUID_TEMP_READ = "ebe0ccc1-7a0a-4b0c-8a1a-6ff2997da3a6"
UUID_BATTERY_READ = "ebe0ccc4-7a0a-4b0c-8a1a-6ff2997da3a6"
