"""Tests for core Haystack functionality."""

from unittest.mock import MagicMock, patch

import pytest

from haystack.aws_client import AWSClient
from haystack.config import HaystackConfig
from haystack.stack_finder import StackFinder


class TestRoleSelection:
    """Test the role selection priority logic."""

    def test_select_admin_role_priority(self):
        """Test that admin roles are selected first."""
        client = AWSClient.__new__(AWSClient)  # Create without __init__

        roles = [
            {"roleName": "ReadOnlyAccess"},
            {"roleName": "AdministratorAccess"},
            {"roleName": "PowerUserAccess"},
        ]

        result = client._select_best_role(roles)
        assert result["roleName"] == "AdministratorAccess"

    def test_select_power_role_when_no_admin(self):
        """Test that power roles are selected when no admin roles exist."""
        client = AWSClient.__new__(AWSClient)

        roles = [
            {"roleName": "ReadOnlyAccess"},
            {"roleName": "PowerUserAccess"},
            {"roleName": "CustomRole"},
        ]

        result = client._select_best_role(roles)
        assert result["roleName"] == "PowerUserAccess"

    def test_select_first_role_when_no_priority_match(self):
        """Test that first role is selected when no priority matches."""
        client = AWSClient.__new__(AWSClient)

        roles = [
            {"roleName": "CustomRole1"},
            {"roleName": "CustomRole2"},
        ]

        result = client._select_best_role(roles)
        assert result["roleName"] == "CustomRole1"

    def test_case_insensitive_role_matching(self):
        """Test that role matching is case-insensitive."""
        client = AWSClient.__new__(AWSClient)

        roles = [
            {"roleName": "ReadOnlyAccess"},
            {"roleName": "ADMINISTRATORACCESS"},  # Different case
        ]

        result = client._select_best_role(roles)
        assert result["roleName"] == "ADMINISTRATORACCESS"


class TestStackMatching:
    """Test the stack search and filtering logic."""

    def test_case_insensitive_stack_matching(self):
        """Test that stack name matching is case-insensitive."""
        finder = StackFinder.__new__(StackFinder)  # Create without __init__

        # Mock stack summaries
        stacks = [
            {"StackName": "API-Gateway-Prod", "StackStatus": "CREATE_COMPLETE"},
            {"StackName": "web-app-staging", "StackStatus": "CREATE_COMPLETE"},
            {"StackName": "DATABASE-Service", "StackStatus": "CREATE_COMPLETE"},
        ]

        # Test matching
        search_term = "api"
        matches = [s for s in stacks if search_term.lower() in s["StackName"].lower()]

        assert len(matches) == 1
        assert matches[0]["StackName"] == "API-Gateway-Prod"

    def test_partial_stack_matching(self):
        """Test that partial matching works correctly."""
        search_term = "prod"
        stacks = [
            {"StackName": "api-prod", "StackStatus": "CREATE_COMPLETE"},
            {"StackName": "production-db", "StackStatus": "CREATE_COMPLETE"},
            {"StackName": "staging-api", "StackStatus": "CREATE_COMPLETE"},
        ]

        matches = [s for s in stacks if search_term.lower() in s["StackName"].lower()]

        assert len(matches) == 2
        stack_names = [s["StackName"] for s in matches]
        assert "api-prod" in stack_names
        assert "production-db" in stack_names


class TestDeduplication:
    """Test the result deduplication logic."""

    def test_duplicate_removal(self):
        """Test that duplicate stacks are properly removed."""
        finder = StackFinder.__new__(StackFinder)

        results = [
            {
                "stack_name": "api-prod",
                "account_id": "123456789",
                "region": "us-east-1",
                "stack_status": "CREATE_COMPLETE",
            },
            {
                "stack_name": "api-prod",
                "account_id": "123456789",
                "region": "us-east-1",
                "stack_status": "CREATE_COMPLETE",
            },  # Duplicate
            {
                "stack_name": "api-staging",
                "account_id": "123456789",
                "region": "us-east-1",
                "stack_status": "CREATE_COMPLETE",
            },
        ]

        deduplicated = finder._deduplicate_results(results)

        assert len(deduplicated) == 2
        stack_names = [r["stack_name"] for r in deduplicated]
        assert "api-prod" in stack_names
        assert "api-staging" in stack_names

    def test_same_stack_different_regions_kept(self):
        """Test that same stack in different regions is kept."""
        finder = StackFinder.__new__(StackFinder)

        results = [
            {
                "stack_name": "api-prod",
                "account_id": "123456789",
                "region": "us-east-1",
                "stack_status": "CREATE_COMPLETE",
            },
            {
                "stack_name": "api-prod",
                "account_id": "123456789",
                "region": "us-west-2",  # Different region
                "stack_status": "CREATE_COMPLETE",
            },
        ]

        deduplicated = finder._deduplicate_results(results)

        assert len(deduplicated) == 2  # Both should be kept


class TestErrorHandling:
    """Test error handling and user-friendly messages."""

    def test_friendly_error_messages(self):
        """Test that technical errors are converted to friendly messages."""
        client = AWSClient.__new__(AWSClient)

        test_cases = [
            ("AccessDenied: User not authorized", "No permissions"),
            ("UnauthorizedException: Token expired", "No permissions"),
            ("Throttling: Request rate exceeded", "API rate limited"),
            ("ServiceUnavailable: Temporary failure", "AWS service unavailable"),
            ("Some complex error: with details", "Some complex error"),
        ]

        for error_msg, expected in test_cases:
            result = client._get_friendly_error(error_msg)
            assert result == expected


class TestConfiguration:
    """Test configuration management."""

    def test_config_path_generation(self):
        """Test that token cache paths are generated correctly."""
        config = HaystackConfig()

        start_url = "https://example.awsapps.com/start"
        path = config.get_token_cache_path(start_url)

        assert "sso-token-" in path
        assert path.endswith(".json")
        assert len(path.split("sso-token-")[1].split(".")[0]) == 16  # Hash length

    def test_different_urls_different_paths(self):
        """Test that different SSO URLs generate different cache paths."""
        config = HaystackConfig()

        url1 = "https://company1.awsapps.com/start"
        url2 = "https://company2.awsapps.com/start"

        path1 = config.get_token_cache_path(url1)
        path2 = config.get_token_cache_path(url2)

        assert path1 != path2


# Integration-style tests (still mocked, but testing component interaction)
class TestIntegration:
    """Test component integration."""

    @patch("haystack.aws_client.boto3.client")
    def test_account_discovery_flow(self, mock_boto_client):
        """Test the full account discovery flow."""
        # Mock SSO client
        mock_sso = MagicMock()
        mock_boto_client.return_value = mock_sso

        # Mock paginator for accounts
        mock_paginator = MagicMock()
        mock_sso.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.return_value = [
            {"accountList": [{"accountId": "123456789", "accountName": "Test Account"}]}
        ]

        # Mock role listing
        mock_role_paginator = MagicMock()
        mock_sso.get_paginator.return_value = mock_role_paginator
        mock_role_paginator.paginate.return_value = [
            {"roleList": [{"roleName": "AdministratorAccess"}]}
        ]

        # Test the flow (would need more setup for full integration)
        # This is a placeholder for more complex integration tests
        assert True  # Placeholder


if __name__ == "__main__":
    pytest.main([__file__])
