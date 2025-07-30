"""
AzPaddyPy - A standardized Python package for Azure cloud services integration.
"""

__version__ = "0.1.0"

from azpaddypy.mgmt.logging import AzureLogger
from azpaddypy.mgmt.identity import AzureIdentity
from azpaddypy.mgmt.local_development import LocalDevelopmentSettings, set_local_dev_environment

__all__ = [
    "AzureLogger", 
    "AzureIdentity",
    "LocalDevelopmentSettings",
    "set_local_dev_environment",
]
