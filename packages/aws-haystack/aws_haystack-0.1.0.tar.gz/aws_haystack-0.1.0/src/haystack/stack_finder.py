"""CloudFormation stack finder across AWS accounts."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional

from botocore.exceptions import ClientError  # type: ignore
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)

from .aws_client import AWSClient

console = Console()


class StackFinder:
    """Find CloudFormation stacks across AWS accounts and regions."""

    def __init__(
        self,
        sso_start_url: Optional[str] = None,
        sso_region: str = "us-east-1",
        verbose: bool = False,
    ):
        self.aws_client = AWSClient(
            sso_start_url=sso_start_url, sso_region=sso_region, verbose=verbose
        )
        self.verbose = verbose

    def find_stack(
        self, stack_name: str, region: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """Find CloudFormation stack across all accessible accounts and regions."""
        if region:
            # If specific region requested, just get accounts
            accounts = self.aws_client.get_accounts()
            regions = [region]
        else:
            # Get both accounts and regions in parallel for maximum efficiency
            accounts, regions = self.aws_client.get_accounts_and_regions_parallel()

        if self.verbose:
            console.print(
                f"[blue]Searching {len(accounts)} account(s) across {len(regions)} region(s) - one role per account[/blue]"
            )

        results = []

        # Calculate total search operations
        total_searches = len(accounts) * len(regions)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
            disable=not console.is_terminal,
        ) as progress:

            task = progress.add_task(
                f"Searching {total_searches} account/region combinations...",
                total=total_searches,
            )

            # Use ThreadPoolExecutor to search accounts/regions in parallel
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = []

                for account in accounts:
                    for region_name in regions:
                        future = executor.submit(
                            self._search_stack_in_account_region,
                            stack_name,
                            account,
                            region_name,
                        )
                        futures.append(future)

                for future in as_completed(futures):
                    try:
                        account_region_results = future.result()
                        if account_region_results:
                            results.extend(account_region_results)
                            if self.verbose:
                                for result in account_region_results:
                                    console.print(
                                        f"[green]Found '{result['stack_name']}' in {result['account_id']}:{result['region']}[/green]"
                                    )
                    except Exception as e:
                        if self.verbose:
                            console.print(f"[red]Error in search: {str(e)}[/red]")
                    finally:
                        # Always advance progress, whether successful or failed
                        progress.advance(task)

        # Remove duplicates based on stack_name + account_id + region
        return self._deduplicate_results(results)

    def _deduplicate_results(
        self, results: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Remove duplicate stack results based on stack name, account ID, and region."""
        seen = set()
        deduplicated = []

        for result in results:
            # Create unique key for each stack
            key = (result["stack_name"], result["account_id"], result["region"])

            if key not in seen:
                seen.add(key)
                deduplicated.append(result)

        return deduplicated

    def _search_stack_in_account_region(
        self, search_term: str, account: Dict[str, str], region: str
    ) -> List[Dict[str, str]]:
        """Search for stacks containing the search term in specific account and region."""
        try:
            cf_client = self.aws_client.get_cloudformation_client(
                account["account_id"], region, account.get("role_name")
            )

            # List all stacks in this region
            paginator = cf_client.get_paginator("list_stacks")
            matching_stacks = []

            for page in paginator.paginate(
                StackStatusFilter=[
                    "CREATE_COMPLETE",
                    "CREATE_FAILED",
                    "CREATE_IN_PROGRESS",
                    "DELETE_FAILED",
                    "DELETE_IN_PROGRESS",
                    "ROLLBACK_COMPLETE",
                    "ROLLBACK_FAILED",
                    "ROLLBACK_IN_PROGRESS",
                    "UPDATE_COMPLETE",
                    "UPDATE_COMPLETE_CLEANUP_IN_PROGRESS",
                    "UPDATE_FAILED",
                    "UPDATE_IN_PROGRESS",
                    "UPDATE_ROLLBACK_COMPLETE",
                    "UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS",
                    "UPDATE_ROLLBACK_FAILED",
                    "UPDATE_ROLLBACK_IN_PROGRESS",
                    "REVIEW_IN_PROGRESS",
                    "IMPORT_COMPLETE",
                    "IMPORT_IN_PROGRESS",
                    "IMPORT_ROLLBACK_COMPLETE",
                    "IMPORT_ROLLBACK_FAILED",
                    "IMPORT_ROLLBACK_IN_PROGRESS",
                ]
            ):
                for stack_summary in page["StackSummaries"]:
                    stack_name = stack_summary["StackName"]

                    # Check if search term is contained in stack name (case-insensitive)
                    if search_term.lower() in stack_name.lower():
                        matching_stacks.append(
                            {
                                "account_id": account["account_id"],
                                "account_name": account["account_name"],
                                "region": region,
                                "stack_name": stack_name,
                                "stack_status": stack_summary["StackStatus"],
                                "creation_time": (
                                    stack_summary.get("CreationTime", "").isoformat()
                                    if stack_summary.get("CreationTime")
                                    else ""
                                ),
                                "description": stack_summary.get(
                                    "TemplateDescription", ""
                                ),
                                "role_name": account.get("role_name", "Unknown"),
                            }
                        )

            return matching_stacks

        except ClientError as e:
            error_code = e.response["Error"]["Code"]

            # Access denied or other permission issues - this is expected for some accounts/regions
            if error_code in ["AccessDenied", "UnauthorizedOperation"]:
                if self.verbose:
                    role_info = f" (role: {account.get('role_name', 'unknown')})"
                    console.print(
                        f"[yellow]Access denied to {account['account_id']}:{region}{role_info}[/yellow]"
                    )
                return []

            # Log other errors if verbose
            if self.verbose:
                role_info = f" (role: {account.get('role_name', 'unknown')})"
                console.print(
                    f"[yellow]Warning: {error_code} in {account['account_id']}:{region}{role_info}[/yellow]"
                )

            return []

        except Exception as e:
            if self.verbose:
                role_info = f" (role: {account.get('role_name', 'unknown')})"
                console.print(
                    f"[red]Unexpected error in {account['account_id']}:{region}{role_info}: {str(e)}[/red]"
                )
            return []
