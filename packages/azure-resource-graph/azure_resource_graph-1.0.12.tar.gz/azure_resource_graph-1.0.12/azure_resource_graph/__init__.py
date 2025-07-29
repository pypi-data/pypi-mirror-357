#!/usr/bin/env python3
"""
Azure Resource Graph - Python client for Azure Resource Graph API.

This package provides tools for querying Azure resources and analyzing
storage encryption compliance across applications using the Azure Resource Graph API.
"""

from .client import AzureResourceGraphClient, AzureConfig

__version__ = "1.0.12"
__author__ = "Kenneth Stott"
__email__ = "ken@hasura.io"

# Make key classes available at package level
__all__ = [
    'AzureResourceGraphClient',
    'AzureConfig'
]

__description__ = "Python client for Azure Resource Graph API with storage encryption analysis"
