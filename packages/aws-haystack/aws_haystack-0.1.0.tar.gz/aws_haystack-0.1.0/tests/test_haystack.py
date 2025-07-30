"""Basic tests for Haystack CLI."""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from haystack.cli import main


def test_cli_help():
    """Test that CLI help works."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert (
        "Find CloudFormation stacks containing the search term across AWS accounts"
        in result.output
    )


def test_cli_missing_stack_name():
    """Test CLI behavior when stack name is missing."""
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code == 0  # Shows help when no args provided


@patch("haystack.stack_finder.StackFinder")
def test_cli_basic_search(mock_stack_finder):
    """Test basic stack search functionality."""
    # Mock the StackFinder
    mock_finder_instance = MagicMock()
    mock_finder_instance.find_stack.return_value = [
        {
            "stack_name": "test-stack-prod",
            "account_id": "123456789012",
            "account_name": "Test Account",
            "region": "us-east-1",
            "stack_status": "CREATE_COMPLETE",
        }
    ]
    mock_stack_finder.return_value = mock_finder_instance

    runner = CliRunner()
    result = runner.invoke(main, ["test-stack"])

    # Should not crash and should call find_stack
    mock_finder_instance.find_stack.assert_called_once_with("test-stack", region=None)


@patch("haystack.stack_finder.StackFinder")
def test_cli_no_results(mock_stack_finder):
    """Test CLI behavior when no stacks are found."""
    mock_finder_instance = MagicMock()
    mock_finder_instance.find_stack.return_value = []
    mock_stack_finder.return_value = mock_finder_instance

    runner = CliRunner()
    result = runner.invoke(main, ["nonexistent-stack"])

    assert "No stacks containing" in result.output
