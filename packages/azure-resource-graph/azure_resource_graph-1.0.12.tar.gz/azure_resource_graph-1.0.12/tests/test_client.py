#!/usr/bin/env python3
"""
Pytest tests for Azure Resource Graph Client
"""

import json
import pytest
import time
import os
from typing import Dict, Any, List

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")

from azure_resource_graph import AzureResourceGraphClient, AzureConfig


class TestClientInitialization:
    """Test client initialization and configuration"""

    def test_import_client(self):
        """Test that we can import the client successfully"""
        from azure_resource_graph import AzureResourceGraphClient, AzureConfig
        assert AzureResourceGraphClient is not None
        assert AzureConfig is not None

    def test_client_initialization(self, client):
        """Test basic client initialization"""
        assert client is not None
        assert isinstance(client, AzureResourceGraphClient)

    def test_client_configuration(self, client_config):
        """Test client configuration loading"""
        assert client_config is not None
        assert isinstance(client_config, AzureConfig)
        assert client_config.tenant_id is not None
        assert client_config.client_id is not None
        assert client_config.client_secret is not None
        assert len(client_config.tenant_id) > 10  # Basic validation
        assert len(client_config.client_id) > 10

    def test_subscription_ids(self, client_config):
        """Test subscription IDs configuration"""
        # Should either have subscription IDs or be an empty list
        assert isinstance(client_config.subscription_ids, list)


@pytest.mark.auth
class TestAuthentication:
    """Test authentication functionality"""

    @pytest.mark.integration
    def test_token_retrieval(self, client, access_token):
        """Test access token retrieval"""
        assert access_token is not None
        assert isinstance(access_token, str)
        assert len(access_token) > 50  # Azure tokens are long
        assert access_token.startswith("eyJ")  # JWT tokens start with eyJ

    @pytest.mark.integration
    def test_token_caching(self, client):
        """Test that tokens are cached properly"""
        # Get token twice and verify caching works
        token1 = client._get_access_token()
        token2 = client._get_access_token()

        assert token1 == token2  # Should be same cached token

    @pytest.mark.integration
    def test_token_properties(self, access_token):
        """Test token properties and format"""
        # Basic token validation
        assert "." in access_token  # JWT tokens have dots
        parts = access_token.split(".")
        assert len(parts) >= 2  # JWT has at least 2 parts


@pytest.mark.query
class TestBasicQueries:
    """Test basic Resource Graph queries"""

    @pytest.mark.integration
    def test_basic_resource_query(self, client, sample_basic_query):
        """Test basic resource group query"""
        results = client.query_resource_graph(sample_basic_query)

        assert isinstance(results, list)
        # Should have at least 0 results (empty Azure subscriptions are possible)
        assert len(results) >= 0

        # If we have results, validate structure
        if results:
            assert isinstance(results[0], dict)
            # Basic query should return resource groups with names
            assert "name" in results[0]

    @pytest.mark.integration
    def test_empty_query_results(self, client):
        """Test query that returns no results"""
        # Query for non-existent resource type
        query = "Resources | where type == 'microsoft.nonexistent/faketype' | limit 1"
        results = client.query_resource_graph(query)

        assert isinstance(results, list)
        assert len(results) == 0

    @pytest.mark.integration
    def test_query_with_specific_subscription(self, client, client_config):
        """Test query with specific subscription IDs"""
        if not client_config.subscription_ids:
            pytest.skip("No subscription IDs configured")

        query = "Resources | where type == 'microsoft.resources/resourcegroups' | limit 3"
        results = client.query_resource_graph(query, client_config.subscription_ids[:1])

        assert isinstance(results, list)


@pytest.mark.storage
class TestStorageEncryption:
    """Test storage encryption analysis functionality"""

    @pytest.mark.integration
    def test_storage_encryption_query(self, storage_encryption_results):
        """Test storage encryption query execution"""
        assert isinstance(storage_encryption_results, list)
        # Results can be empty if no tagged storage resources exist

        # If we have results, validate structure
        for result in storage_encryption_results[:5]:  # Check first 5
            assert isinstance(result, dict)

            # Check required fields
            required_fields = [
                "Application", "StorageResource", "StorageType",
                "EncryptionMethod", "ComplianceStatus", "ResourceGroup"
            ]
            for field in required_fields:
                assert field in result, f"Missing field: {field}"

            # Validate field types
            assert isinstance(result["Application"], str)
            assert isinstance(result["StorageResource"], str)
            assert isinstance(result["StorageType"], str)
            assert isinstance(result["EncryptionMethod"], str)
            assert isinstance(result["ComplianceStatus"], str)
            assert isinstance(result["ResourceGroup"], str)

    @pytest.mark.integration
    def test_storage_encryption_compliance_values(self, storage_encryption_results):
        """Test that compliance status values are valid"""
        if not storage_encryption_results:
            pytest.skip("No storage encryption results to validate")

        valid_compliance_statuses = {
            "Compliant", "Non-Compliant", "Partially Compliant",
            "Manual Review Required", "Unknown"
        }

        for result in storage_encryption_results:
            status = result["ComplianceStatus"]
            assert status in valid_compliance_statuses, f"Invalid compliance status: {status}"

    @pytest.mark.integration
    def test_storage_types_are_valid(self, storage_encryption_results):
        """Test that storage types are valid Azure resource types"""
        if not storage_encryption_results:
            pytest.skip("No storage encryption results to validate")

        valid_storage_types = {
            "Storage Account", "SQL Database", "Cosmos DB", "Managed Disk"
        }

        for result in storage_encryption_results:
            storage_type = result["StorageType"]
            assert storage_type in valid_storage_types, f"Invalid storage type: {storage_type}"


@pytest.mark.compliance
class TestComplianceSummary:
    """Test compliance summary functionality"""

    @pytest.mark.integration
    def test_compliance_summary_query(self, compliance_summary_results):
        """Test compliance summary query execution"""
        assert isinstance(compliance_summary_results, list)

        # If we have results, validate structure
        for result in compliance_summary_results:
            assert isinstance(result, dict)

            # Check required fields
            required_fields = [
                "Application", "TotalResources", "CompliantResources",
                "NonCompliantResources", "CompliancePercentage", "ComplianceStatus"
            ]
            for field in required_fields:
                assert field in result, f"Missing field: {field}"

            # Validate field types and values
            assert isinstance(result["Application"], str)
            assert isinstance(result["TotalResources"], (int, float))
            assert isinstance(result["CompliantResources"], (int, float))
            assert isinstance(result["NonCompliantResources"], (int, float))
            assert isinstance(result["CompliancePercentage"], (int, float))
            assert isinstance(result["ComplianceStatus"], str)

            # Validate logical relationships
            total = result["TotalResources"]
            compliant = result["CompliantResources"]
            non_compliant = result["NonCompliantResources"]

            assert total >= 0
            assert compliant >= 0
            assert non_compliant >= 0
            assert compliant + non_compliant == total, "Compliant + Non-compliant should equal total"

    @pytest.mark.integration
    def test_compliance_percentages(self, compliance_summary_results):
        """Test compliance percentage calculations"""
        if not compliance_summary_results:
            pytest.skip("No compliance results to validate")

        for result in compliance_summary_results:
            percentage = result["CompliancePercentage"]
            total = result["TotalResources"]
            compliant = result["CompliantResources"]

            # Percentage should be between 0 and 100
            assert 0 <= percentage <= 100

            # If we have resources, percentage should match calculation
            if total > 0:
                expected_percentage = (compliant / total) * 100
                assert abs(percentage - expected_percentage) < 0.1, "Percentage calculation mismatch"


@pytest.mark.query
class TestApplicationSpecificQueries:
    """Test application-specific query functionality"""

    @pytest.mark.integration
    @pytest.mark.parametrize("app_name", ["ECommerceApp", "AnalyticsApp", "TestApp", "NonExistentApp"])
    def test_application_storage_query(self, client, app_name):
        """Test querying storage for specific applications"""
        results = client.query_application_storage(app_name)

        assert isinstance(results, list)

        # If we have results, validate they're for the correct application
        for result in results:
            assert isinstance(result, dict)
            assert "Application" in result
            assert result["Application"] == app_name


class TestErrorHandling:
    """Test error handling and edge cases"""

    @pytest.mark.integration
    def test_invalid_query_handling(self, client, invalid_query):
        """Test handling of invalid KQL queries"""
        with pytest.raises(Exception) as exc_info:
            client.query_resource_graph(invalid_query)

        # Should get a meaningful error message from Azure API
        error_msg = str(exc_info.value).lower()
        assert any(keyword in error_msg for keyword in ["query", "invalid", "bad request", "400", "client error", "request failed"]), \
            f"Expected meaningful error message, got: {exc_info.value}"

    @pytest.mark.integration
    def test_empty_subscription_list(self, client):
        """Test query with empty subscription list"""
        query = "Resources | limit 1"

        # Should either work with default subscriptions or raise meaningful error
        try:
            results = client.query_resource_graph(query, [])
            assert isinstance(results, list)
        except Exception as e:
            assert "subscription" in str(e).lower()

    def test_invalid_subscription_id_format(self, client):
        """Test query with invalid subscription ID format"""
        query = "Resources | limit 1"
        invalid_sub_ids = ["invalid-sub-id", "not-a-guid"]

        with pytest.raises(Exception):
            client.query_resource_graph(query, invalid_sub_ids)


@pytest.mark.slow
class TestPerformance:
    """Test performance characteristics"""

    @pytest.mark.integration
    def test_query_performance(self, client, performance_timer, sample_basic_query):
        """Test that queries complete within reasonable time"""
        performance_timer.start()
        results = client.query_resource_graph(sample_basic_query)
        duration = performance_timer.stop()

        # Should complete within 30 seconds
        assert duration < 30, f"Query took too long: {duration:.2f} seconds"

        # Log performance for monitoring
        print(f"\nQuery performance: {duration:.2f} seconds for {len(results)} results")

    @pytest.mark.integration
    def test_token_retrieval_performance(self, client, performance_timer):
        """Test token retrieval performance"""
        # Clear any cached token first
        client._access_token = None
        client._token_expires_at = 0

        performance_timer.start()
        token = client._get_access_token()
        duration = performance_timer.stop()

        assert token is not None
        assert duration < 10, f"Token retrieval took too long: {duration:.2f} seconds"


class TestDataValidation:
    """Test data validation and formatting"""

    def test_mock_storage_resource_structure(self, mock_storage_resource):
        """Test mock storage resource has correct structure"""
        required_fields = [
            "Application", "StorageResource", "StorageType",
            "EncryptionMethod", "ComplianceStatus", "ResourceGroup"
        ]

        for field in required_fields:
            assert field in mock_storage_resource

    def test_mock_compliance_summary_structure(self, mock_compliance_summary):
        """Test mock compliance summary has correct structure"""
        required_fields = [
            "Application", "TotalResources", "CompliantResources",
            "NonCompliantResources", "CompliancePercentage", "ComplianceStatus"
        ]

        for field in required_fields:
            assert field in mock_compliance_summary


class TestResultSaving:
    """Test result saving functionality"""

    @pytest.mark.integration
    def test_save_storage_results(self, storage_encryption_results, temp_results_file):
        """Test saving storage encryption results"""
        if not storage_encryption_results:
            pytest.skip("No storage results to save")

        # Save results to temp file
        test_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
            'total_resources': len(storage_encryption_results),
            'results': storage_encryption_results
        }

        temp_results_file.write_text(json.dumps(test_data, indent=2))

        # Verify file was created and has content
        assert temp_results_file.exists()
        assert temp_results_file.stat().st_size > 0

        # Verify content can be loaded back
        loaded_data = json.loads(temp_results_file.read_text())
        assert loaded_data['total_resources'] == len(storage_encryption_results)
        assert len(loaded_data['results']) == len(storage_encryption_results)


# Integration test class that requires everything to work
@pytest.mark.integration
class TestFullWorkflow:
    """Test complete end-to-end workflows"""

    def test_complete_encryption_analysis_workflow(self, client):
        """Test complete storage encryption analysis workflow"""
        # Step 1: Get storage encryption results
        storage_results = client.query_storage_encryption()
        assert isinstance(storage_results, list)

        # Step 2: Get compliance summary
        compliance_results = client.get_compliance_summary()
        assert isinstance(compliance_results, list)

        # Step 3: If we have storage results, test application-specific queries
        if storage_results:
            # Get unique applications
            applications = set(result["Application"] for result in storage_results)

            for app in list(applications)[:3]:  # Test first 3 applications
                app_results = client.query_application_storage(app)
                assert isinstance(app_results, list)

        print(f"\n✅ Complete workflow test passed:")
        print(f"   - Storage resources found: {len(storage_results)}")
        print(f"   - Applications analyzed: {len(compliance_results)}")
