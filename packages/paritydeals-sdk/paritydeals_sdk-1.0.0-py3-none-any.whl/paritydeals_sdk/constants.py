# paritydeals/constants.py

from typing import Literal

# Defines the allowed choices for the 'behaviour' parameter in usage reporting.
# 'SET': Indicates that the reported value is an absolute value.
# 'DELTA': Indicates that the reported value is a change increment to a previous value.
BEHAVIOUR_CHOICES = Literal['SET', 'DELTA']

# For example:
DEFAULT_API_URL = "https://api.paritydeals.com"
API_BASE_PATH_PREFIX = "/api"
DEFAULT_API_VERSION = "v1"
MAX_RETRIES = 3

EDGE_API_URL = "https://edge.api.paritydeals.com"