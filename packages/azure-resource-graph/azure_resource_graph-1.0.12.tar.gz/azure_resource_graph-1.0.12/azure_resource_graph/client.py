#!/usr/bin/env python3
"""
Azure Resource Graph Client
Complete class for querying Azure resources with authentication
"""

import os
import time
import json
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AzureConfig:
    """Azure authentication configuration"""
    tenant_id: str
    client_id: str
    client_secret: str
    subscription_ids: List[str]


class AzureResourceGraphClient:
    """
    Azure Resource Graph API Client

    Environment Variables Required:
    - AZURE_TENANT_ID: Your Azure tenant ID
    - AZURE_CLIENT_ID: Service principal client ID
    - AZURE_CLIENT_SECRET: Service principal client secret
    - AZURE_SUBSCRIPTION_IDS: Comma-separated list of subscription IDs

    Example Usage:
        client = AzureResourceGraphClient()
        results = client.query_storage_encryption()
        for item in results:
            print(f"{item['Application']} - {item['StorageResource']} - {item['EncryptionMethod']}")
    """

    def __init__(self, config: Optional[AzureConfig] = None):
        """
        Initialize the client with Azure configuration

        Args:
            config: Optional AzureConfig object. If None, reads from environment variables.
        """
        if config:
            self.config = config
        else:
            self.config = self._load_config_from_env()

        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        self._api_base_url = "https://management.azure.com"
        self._auth_url = f"https://login.microsoftonline.com/{self.config.tenant_id}/oauth2/v2.0/token"

    def _load_config_from_env(self) -> AzureConfig:
        """Load configuration from environment variables or .env file"""
        # Try to load from .env file first
        try:
            from dotenv import load_dotenv
            load_dotenv()  # Load .env file from current directory or parent directories
        except ImportError:
            # dotenv not available, continue with regular env vars
            pass

        tenant_id = os.getenv('AZURE_TENANT_ID')
        client_id = os.getenv('AZURE_CLIENT_ID')
        client_secret = os.getenv('AZURE_CLIENT_SECRET')
        subscription_ids_str = os.getenv('AZURE_SUBSCRIPTION_IDS', '')

        if not all([tenant_id, client_id, client_secret]):
            raise ValueError(
                "Missing required environment variables. Please set:\n"
                "- AZURE_TENANT_ID\n"
                "- AZURE_CLIENT_ID\n"
                "- AZURE_CLIENT_SECRET\n"
                "- AZURE_SUBSCRIPTION_IDS (optional, comma-separated)\n\n"
                "You can set these in environment variables or create a .env file with:\n"
                "AZURE_TENANT_ID=your-tenant-id\n"
                "AZURE_CLIENT_ID=your-client-id\n"
                "AZURE_CLIENT_SECRET=your-client-secret\n"
                "AZURE_SUBSCRIPTION_IDS=sub1,sub2"
            )

        # Parse subscription IDs
        subscription_ids = [s.strip() for s in subscription_ids_str.split(',') if s.strip()]
        if not subscription_ids:
            # If no subscription IDs provided, we'll get them from the token
            subscription_ids = []

        return AzureConfig(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
            subscription_ids=subscription_ids
        )

    def _get_access_token(self) -> str:
        """
        Get access token using service principal credentials
        Implements token caching to avoid unnecessary requests
        """
        current_time = time.time()

        # Return cached token if still valid (refresh 5 minutes early)
        if self._access_token and current_time < (self._token_expires_at - 300):
            return self._access_token

        # Request new token
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret,
            'scope': 'https://management.azure.com/.default'
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            response = requests.post(self._auth_url, data=data, headers=headers, timeout=30)
            response.raise_for_status()

            token_data = response.json()
            self._access_token = token_data['access_token']

            # Calculate expiration time (tokens typically last 1 hour)
            expires_in = token_data.get('expires_in', 3600)  # Default to 1 hour
            self._token_expires_at = current_time + expires_in

            return self._access_token

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get access token: {e}")
        except KeyError as e:
            raise Exception(f"Invalid token response format: {e}")

    def query_resource_graph(self, query: str, subscription_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Execute a KQL query against Azure Resource Graph

        Args:
            query: KQL query string
            subscription_ids: Optional list of subscription IDs. Uses config default if None.

        Returns:
            List of dictionaries containing query results
        """
        access_token = self._get_access_token()
        subs = subscription_ids or self.config.subscription_ids

        if not subs:
            raise ValueError(
                "No subscription IDs provided. Set AZURE_SUBSCRIPTION_IDS or pass subscription_ids parameter.")

        url = f"{self._api_base_url}/providers/Microsoft.ResourceGraph/resources?api-version=2021-03-01"

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        payload = {
            'subscriptions': subs,
            'query': query,
            'options': {
                'top': 1000  # Maximum results per page
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            result = response.json()
            return result.get('data', [])

        except requests.exceptions.RequestException as e:
            raise Exception(f"Resource Graph API request failed: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {e}")

    def query_storage_encryption(self, subscription_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Query application storage resources and their encryption status

        Args:
            subscription_ids: Optional list of subscription IDs

        Returns:
            List of storage resources with encryption details
        """
        query = """
        Resources
        | where type in (
            'microsoft.storage/storageaccounts',
            'microsoft.sql/servers/databases',
            'microsoft.documentdb/databaseaccounts', 
            'microsoft.compute/disks'
        )
        | extend Application = case(
            isnotempty(tags.Application), tags.Application,
            isnotempty(tags.app), tags.app,
            isnotempty(tags['application-name']), tags['application-name'],
            'Untagged/Orphaned'
        )
        | extend StorageType = case(
            type == 'microsoft.storage/storageaccounts', 'Storage Account',
            type == 'microsoft.sql/servers/databases', 'SQL Database',
            type == 'microsoft.documentdb/databaseaccounts', 'Cosmos DB',
            type == 'microsoft.compute/disks', 'Managed Disk',
            type
        )
        | extend EncryptionMethod = case(
            type == 'microsoft.storage/storageaccounts',
                case(
                    tostring(properties.encryption.keySource) == 'Microsoft.Keyvault', 'Customer Managed Key (CMK)',
                    tobool(properties.encryption.services.blob.enabled) == true and tobool(properties.supportsHttpsTrafficOnly) == true, 'Platform Managed + HTTPS',
                    tobool(properties.encryption.services.blob.enabled) == true and tobool(properties.supportsHttpsTrafficOnly) == false, 'Platform Managed + HTTP Allowed',
                    'Not Encrypted'
                ),
            type == 'microsoft.compute/disks',
                case(
                    tostring(properties.encryption.type) == 'EncryptionAtRestWithCustomerKey', 'Customer Managed Key (CMK)',
                    tostring(properties.encryption.type) == 'EncryptionAtRestWithPlatformKey', 'Platform Managed Key (PMK)',
                    tostring(properties.encryption.type) == 'EncryptionAtRestWithPlatformAndCustomerKeys', 'Double Encryption (PMK + CMK)',
                    'Not Encrypted'
                ),
            type == 'microsoft.documentdb/databaseaccounts',
                case(
                    isnotempty(tostring(properties.keyVaultKeyUri)), 'Customer Managed Key (CMK)',
                    'Platform Managed Key (PMK)'
                ),
            type == 'microsoft.sql/servers/databases', 'Check TDE Status',
            'Unknown'
        )
        | extend ComplianceStatus = case(
            EncryptionMethod contains 'Not Encrypted', 'Non-Compliant',
            EncryptionMethod contains 'HTTP Allowed', 'Partially Compliant', 
            EncryptionMethod contains 'Check TDE', 'Manual Review Required',
            EncryptionMethod contains 'Platform Managed' or EncryptionMethod contains 'Customer Managed', 'Compliant',
            'Unknown'
        )
        | extend AdditionalDetails = case(
            type == 'microsoft.storage/storageaccounts', 
                strcat('HTTPS: ', case(tobool(properties.supportsHttpsTrafficOnly) == true, 'Required', 'Optional'), 
                       ' | Public: ', case(tobool(properties.allowBlobPublicAccess) == true, 'Allowed', 'Blocked')),
            type == 'microsoft.compute/disks',
                strcat(tostring(properties.diskSizeGB), 'GB | State: ', tostring(properties.diskState)),
            type == 'microsoft.documentdb/databaseaccounts',
                strcat('Consistency: ', tostring(properties.defaultConsistencyLevel)),
            ''
        )
        | project 
            Application,
            StorageResource = name,
            StorageType,
            EncryptionMethod,
            ComplianceStatus,
            ResourceGroup = resourceGroup,
            Location = location,
            AdditionalDetails,
            ResourceId = id
        | order by Application, StorageType, StorageResource
        """

        return self.query_resource_graph(query, subscription_ids)

    def query_application_storage(self, application_name: str, subscription_ids: Optional[List[str]] = None) -> List[
        Dict[str, Any]]:
        """
        Query storage resources for a specific application

        Args:
            application_name: Name of the application to filter by
            subscription_ids: Optional list of subscription IDs

        Returns:
            List of storage resources for the specified application
        """
        query = f"""
        Resources
        | where type in (
            'microsoft.storage/storageaccounts',
            'microsoft.sql/servers/databases',
            'microsoft.documentdb/databaseaccounts', 
            'microsoft.compute/disks'
        )
        | where tags.Application == '{application_name}' or tags.app == '{application_name}'
        | extend StorageType = case(
            type == 'microsoft.storage/storageaccounts', 'Storage Account',
            type == 'microsoft.sql/servers/databases', 'SQL Database',
            type == 'microsoft.documentdb/databaseaccounts', 'Cosmos DB',
            type == 'microsoft.compute/disks', 'Managed Disk',
            type
        )
        | project 
            Application = '{application_name}',
            StorageResource = name,
            StorageType,
            ResourceGroup = resourceGroup,
            Location = location,
            Tags = tags,
            ResourceId = id
        | order by StorageType, StorageResource
        """

        return self.query_resource_graph(query, subscription_ids)

    def get_compliance_summary(self, subscription_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get compliance summary by application

        Args:
            subscription_ids: Optional list of subscription IDs

        Returns:
            List with compliance summary per application
        """
        query = """
        Resources
        | where type in (
            'microsoft.storage/storageaccounts',
            'microsoft.compute/disks',
            'microsoft.documentdb/databaseaccounts'
        )
        | extend Application = case(
            isnotempty(tags.Application), tags.Application,
            isnotempty(tags.app), tags.app,
            'Untagged/Orphaned'
        )
        | extend IsCompliant = case(
            type == 'microsoft.storage/storageaccounts', 
                (tobool(properties.encryption.services.blob.enabled) == true and tobool(properties.supportsHttpsTrafficOnly) == true),
            type == 'microsoft.compute/disks', 
                (tostring(properties.encryption.type) contains 'Encryption'),
            type == 'microsoft.documentdb/databaseaccounts', 
                true,
            false
        )
        | summarize 
            TotalResources = count(),
            CompliantResources = countif(IsCompliant == true),
            NonCompliantResources = countif(IsCompliant == false),
            CompliancePercentage = round(countif(IsCompliant == true) * 100.0 / count(), 1)
        by Application
        | extend ComplianceStatus = case(
            CompliancePercentage == 100, 'Fully Compliant',
            CompliancePercentage >= 80, 'Mostly Compliant', 
            CompliancePercentage >= 50, 'Partially Compliant',
            'Non-Compliant'
        )
        | project 
            Application,
            TotalResources,
            CompliantResources,
            NonCompliantResources,
            CompliancePercentage,
            ComplianceStatus
        | order by Application
        """

        return self.query_resource_graph(query, subscription_ids)


# ==================================================
# EXAMPLE USAGE
# ==================================================

def main():
    """Example usage of the AzureResourceGraphClient"""

    try:
        # Initialize client (reads from environment variables)
        print("🔐 Initializing Azure Resource Graph Client...")
        client = AzureResourceGraphClient()

        # Query storage encryption status
        print("🔍 Querying storage encryption status...")
        results = client.query_storage_encryption()

        print(f"\n📊 Found {len(results)} storage resources:")
        print("=" * 100)

        for item in results:
            status_icon = {
                'Compliant': '✅',
                'Non-Compliant': '❌',
                'Partially Compliant': '⚠️',
                'Manual Review Required': '🔍'
            }.get(item['ComplianceStatus'], '❓')

            print(
                f"{status_icon} {item['Application']:<20} | {item['StorageResource']:<25} | {item['EncryptionMethod']:<30} | {item['ComplianceStatus']}")

        # Get compliance summary
        print("\n📈 Compliance Summary:")
        print("=" * 80)
        summary = client.get_compliance_summary()

        for app in summary:
            print(
                f"{app['Application']:<20} | {app['TotalResources']:>3} resources | {app['CompliantResources']:>3} compliant | {app['CompliancePercentage']:>5.1f}% | {app['ComplianceStatus']}")

        # Save results to file
        output = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
            'storage_resources': results,
            'compliance_summary': summary
        }

        with open('azure_storage_encryption_report.json', 'w') as f:
            json.dump(output, f, indent=2)

        print(f"\n💾 Full report saved to 'azure_storage_encryption_report.json'")

        return results

    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
