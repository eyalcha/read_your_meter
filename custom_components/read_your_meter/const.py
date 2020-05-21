"""Constant"""

DOMAIN = "read_your_meter"
DOMAIN_DATA = "{}_data".format(DOMAIN)

CONF_DAILY="daily"
CONF_MONTHLY="monthly"

DEFAULT_HOST = "http://localhost:4444"
DEFAULT_SCAN_INTERVAL = 1800
DEFAULT_DAILY=[0]
DEFAULT_MONTHLY=[0]
DEFAULT_NAME = "Read your meter"
DEFAULT_ICON = "mdi:speedometer-medium"
DEFAULT_UNIT_OF_MEASUREMENT = "m³"

DATA = "data"
DATA_CLIENT = "client"