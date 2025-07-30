"""AWS client wrapper for Identity Center integration."""

import json
import os
import time
import webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Tuple

import boto3  # type: ignore
from botocore.exceptions import ClientError, NoCredentialsError  # type: ignore
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)
from rich.prompt import Confirm, Prompt

from .config import HaystackConfig

console = Console()


class AWSClient:
    """Handle AWS operations with Identity Center integration."""

    def __init__(
        self,
        sso_start_url: Optional[str] = None,
        sso_region: str = "us-east-1",
        verbose: bool = False,
    ):
        self.verbose = verbose
        self.access_token = None
        self.token_expires_at: Optional[Any] = None
        self.client_name = "haystack-cli"
        self.config = HaystackConfig()

        # Get SSO configuration (from params, config, or user input)
        self._setup_sso_config(sso_start_url, sso_region)

        # Authenticate and get access token
        self._authenticate()

    def _setup_sso_config(self, sso_start_url: Optional[str], sso_region: str) -> None:
        """Setup SSO configuration from various sources."""
        # Try to get from saved config first
        saved_config = self.config.get_sso_config()

        if sso_start_url:
            # Use provided parameters
            self.sso_start_url = sso_start_url
            self.sso_region = sso_region
            # Save for future use
            self.config.set_sso_config(sso_start_url, sso_region)
        elif saved_config:
            # Use saved configuration
            self.sso_start_url = saved_config["start_url"]
            self.sso_region = saved_config["region"]
            if self.verbose:
                console.print(
                    f"[blue]Using saved SSO configuration: {self.sso_start_url}[/blue]"
                )
        else:
            # Ask user for configuration (first time setup)
            self._get_sso_config_from_user()

    def _get_sso_config_from_user(self) -> None:
        """Get SSO configuration from user input."""
        console.print("[yellow]First-time setup: AWS SSO configuration needed[/yellow]")
        sso_start_url = Prompt.ask(
            "Enter your AWS SSO start URL (e.g., https://example.awsapps.com/start)"
        )

        # Validate URL format
        if not sso_start_url.startswith("https://"):
            raise Exception("SSO start URL must be a valid HTTPS URL")

        # Optional: ask for SSO region
        sso_region = Prompt.ask("Enter SSO region", default="us-east-1")

        # Save configuration
        self.sso_start_url = sso_start_url
        self.sso_region = sso_region
        self.config.set_sso_config(sso_start_url, sso_region)

        console.print(
            "[green]Configuration saved! You won't need to enter this again.[/green]"
        )

    def _get_cache_file_path(self) -> str:
        """Get path to SSO token cache file."""
        return self.config.get_token_cache_path(self.sso_start_url)

    def _load_cached_token(self) -> bool:
        """Load cached SSO token if valid."""
        cache_file = self._get_cache_file_path()

        if not os.path.exists(cache_file):
            return False

        try:
            with open(cache_file, "r") as f:
                cache_data = json.load(f)

            self.access_token = cache_data.get("accessToken")
            expires_at_str = cache_data.get("expiresAt")

            if self.access_token and expires_at_str:
                # Parse expiration time (ISO format)
                from datetime import datetime

                self.token_expires_at = datetime.fromisoformat(
                    expires_at_str.replace("Z", "+00:00")
                )

                # Check if token is still valid (with 5 minute buffer)
                from datetime import datetime, timedelta, timezone

                if datetime.now(timezone.utc) < (
                    self.token_expires_at - timedelta(minutes=5)
                ):
                    if self.verbose:
                        console.print("[green]Using cached SSO token[/green]")
                    return True

            return False

        except Exception as e:
            if self.verbose:
                console.print(f"[yellow]Failed to load cached token: {str(e)}[/yellow]")
            return False

    def _save_token_to_cache(self, token_data: Dict) -> None:
        """Save SSO token to cache."""
        cache_file = self._get_cache_file_path()

        try:
            with open(cache_file, "w") as f:
                json.dump(token_data, f, indent=2)
        except Exception as e:
            if self.verbose:
                console.print(f"[yellow]Failed to cache token: {str(e)}[/yellow]")

    def _authenticate(self) -> None:
        """Authenticate with AWS SSO using browser flow."""
        # First try to load cached token
        if self._load_cached_token():
            if self.verbose:
                console.print("[green]✓ Using cached authentication[/green]")
            return

        # If no valid cached token, start browser-based auth flow
        if self.verbose:
            console.print("[blue]Starting AWS SSO authentication...[/blue]")
        else:
            console.print("[blue]Authenticating with AWS SSO...[/blue]")

        try:
            self._device_auth_flow()  # Use device flow as primary method
        except Exception as e:
            if self.verbose:
                console.print(f"[red]Device auth failed: {str(e)}[/red]")
            raise

    def _device_auth_flow(self) -> None:
        """Fallback device authorization flow."""
        sso_oidc = boto3.client("sso-oidc", region_name=self.sso_region)

        # Register client
        register_response = sso_oidc.register_client(
            clientName=self.client_name, clientType="public"
        )

        client_id = register_response["clientId"]
        client_secret = register_response["clientSecret"]

        # Start device authorization
        device_auth_response = sso_oidc.start_device_authorization(
            clientId=client_id, clientSecret=client_secret, startUrl=self.sso_start_url
        )

        device_code = device_auth_response["deviceCode"]
        user_code = device_auth_response["userCode"]
        verification_uri = device_auth_response["verificationUri"]
        expires_in = device_auth_response["expiresIn"]
        interval = device_auth_response.get("interval", 5)

        # Display instructions
        console.print(
            f"\n[bold yellow]Complete authentication in your browser:[/bold yellow]"
        )
        console.print(f"1. Browser will open: {verification_uri}")
        console.print(f"2. Enter this code: [bold cyan]{user_code}[/bold cyan]")
        console.print(f"3. Sign in with your AWS SSO credentials")

        # Open browser
        webbrowser.open(verification_uri)
        console.print(f"\n[blue]Waiting for you to complete authentication...[/blue]")
        console.print(f"[dim]Code expires in {expires_in//60} minutes[/dim]")

        # Poll for token
        start_time = time.time()
        while time.time() - start_time < expires_in:
            try:
                time.sleep(interval)

                token_response = sso_oidc.create_token(
                    clientId=client_id,
                    clientSecret=client_secret,
                    grantType="urn:ietf:params:oauth:grant-type:device_code",
                    deviceCode=device_code,
                )

                # Success! Save token
                self.access_token = token_response["accessToken"]

                from datetime import datetime, timedelta, timezone

                expires_in_seconds = token_response.get("expiresIn", 3600)
                self.token_expires_at = datetime.now(timezone.utc) + timedelta(
                    seconds=expires_in_seconds
                )

                cache_data = {
                    "accessToken": self.access_token,
                    "expiresAt": self.token_expires_at.isoformat(),
                }
                self._save_token_to_cache(cache_data)

                console.print("[green]✓ Authentication successful![/green]")
                return

            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                if error_code == "AuthorizationPendingException":
                    continue
                elif error_code == "SlowDownException":
                    time.sleep(interval)
                    continue
                elif error_code in ["ExpiredTokenException", "AccessDeniedException"]:
                    raise Exception("Authentication failed or expired")
                else:
                    raise e

        raise Exception("Authentication timed out")

    def _ensure_authenticated(self) -> None:
        """Ensure we have a valid authentication token, refreshing if necessary."""
        if not self.access_token:
            self._authenticate()
            return

        # Check if token is expired or expires soon (within 5 minutes)
        from datetime import datetime, timedelta, timezone

        if self.token_expires_at and datetime.now(timezone.utc) >= (
            self.token_expires_at - timedelta(minutes=5)
        ):
            if self.verbose:
                console.print("[yellow]Token expired, re-authenticating...[/yellow]")
            self._authenticate()

    def get_accounts(self) -> List[Dict[str, str]]:
        """Get all AWS accounts accessible via SSO."""
        self._ensure_authenticated()

        try:
            # Create SSO client
            sso_client = boto3.client("sso", region_name=self.sso_region)

            # First, get list of all accounts (fast)
            console.print("[blue]Getting account list...[/blue]")
            paginator = sso_client.get_paginator("list_accounts")
            raw_accounts = []

            for page in paginator.paginate(accessToken=self.access_token):
                raw_accounts.extend(page["accountList"])

            if not raw_accounts:
                raise Exception("No accessible accounts found via SSO.")

            console.print(f"[green]✓ Found {len(raw_accounts)} accounts[/green]")

            # Now get roles for each account in parallel with progress bar
            accounts = []

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console,
                disable=not console.is_terminal,
            ) as progress:

                task = progress.add_task(
                    "Selecting best role per account...", total=len(raw_accounts)
                )

                # Use ThreadPoolExecutor to get roles in parallel
                with ThreadPoolExecutor(
                    max_workers=3
                ) as executor:  # Reduced to avoid rate limits
                    # Submit all role-fetching tasks
                    future_to_account = {
                        executor.submit(self._get_account_with_roles, account): account
                        for account in raw_accounts
                    }

                    # Collect results as they complete
                    for future in as_completed(future_to_account):
                        account_data = future_to_account[future]
                        try:
                            account_roles = future.result()
                            accounts.extend(account_roles)
                            if self.verbose and account_roles:
                                account_info = account_roles[
                                    0
                                ]  # Only one role per account now
                                console.print(
                                    f"[green]✓ {account_info['account_name']} using role: {account_info['role_name']}[/green]"
                                )
                            progress.advance(task)
                        except Exception as e:
                            console.print(
                                f"[yellow]⚠ Skipped {account_data['accountName']} ({account_data['accountId']}): {self._get_friendly_error(str(e))}[/yellow]"
                            )
                            progress.advance(task)

            console.print(f"[green]✓ Found {len(accounts)} accessible accounts[/green]")

            if not accounts:
                raise Exception("No accessible accounts found via SSO.")

            return accounts

        except ClientError as e:
            if "UnauthorizedException" in str(e) or "InvalidRequestException" in str(e):
                # Token might be invalid, try to re-authenticate once
                if self.verbose:
                    console.print(
                        "[yellow]Token invalid, attempting re-authentication...[/yellow]"
                    )
                self._authenticate()
                return self.get_accounts()  # Retry once
            raise Exception(f"Failed to list accounts: {str(e)}")

    def _get_account_with_roles(self, account_data: Dict) -> List[Dict[str, str]]:
        """Get account with best single role - used for parallel processing."""
        account_id = account_data["accountId"]
        account_name = account_data["accountName"]

        roles = self._get_account_roles(account_id)

        if not roles:
            return []

        # Pick the best role using priority: admin > power > first available
        best_role = self._select_best_role(roles)

        # Return single account entry with the best role
        return [
            {
                "account_id": account_id,
                "account_name": account_name,
                "role_name": best_role["roleName"],
                "role_arn": f"arn:aws:iam::{account_id}:role/{best_role['roleName']}",
            }
        ]

    def _select_best_role(self, roles: List[Dict[str, str]]) -> Dict[str, str]:
        """Select the best role from available roles using priority logic."""
        if not roles:
            raise ValueError("No roles provided")

        # Priority 1: Roles containing "admin" (case-insensitive)
        admin_roles = [role for role in roles if "admin" in role["roleName"].lower()]
        if admin_roles:
            return admin_roles[0]

        # Priority 2: Roles containing "power" (case-insensitive)
        power_roles = [role for role in roles if "power" in role["roleName"].lower()]
        if power_roles:
            return power_roles[0]

        # Priority 3: Any available role (first one)
        return roles[0]

    def _get_account_roles(self, account_id: str) -> List[Dict[str, str]]:
        """Get available roles for a specific account."""
        import time

        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                sso_client = boto3.client("sso", region_name=self.sso_region)

                paginator = sso_client.get_paginator("list_account_roles")
                roles = []

                for page in paginator.paginate(
                    accessToken=self.access_token, accountId=account_id
                ):
                    roles.extend(page["roleList"])

                return roles

            except ClientError as e:
                error_code = e.response["Error"]["Code"]

                # Retry on throttling
                if (
                    error_code in ["Throttling", "RequestLimitExceeded"]
                    and attempt < max_retries
                ):
                    wait_time = (attempt + 1) * 0.5  # 0.5s, 1s
                    time.sleep(wait_time)
                    continue

                # Don't retry other errors
                if self.verbose:
                    console.print(
                        f"[yellow]Warning: Could not list roles for account {account_id}: {str(e)}[/yellow]"
                    )
                return []

        return []

    def get_cloudformation_client(
        self, account_id: str, region: str, role_name: Optional[str] = None
    ) -> boto3.client:
        """Get CloudFormation client for specific account and region."""
        try:
            # Get temporary credentials for this account
            credentials = self._get_role_credentials(account_id, role_name)

            # Create CloudFormation client with temporary credentials
            return boto3.client(
                "cloudformation",
                region_name=region,
                aws_access_key_id=credentials["accessKeyId"],
                aws_secret_access_key=credentials["secretAccessKey"],
                aws_session_token=credentials["sessionToken"],
            )

        except Exception as e:
            raise Exception(
                f"Failed to create CloudFormation client for {account_id}:{region}: {str(e)}"
            )

    def _get_role_credentials(
        self, account_id: str, role_name: Optional[str] = None
    ) -> Dict[str, str]:
        """Get temporary credentials by assuming a role via SSO."""
        self._ensure_authenticated()

        try:
            sso_client = boto3.client("sso", region_name=self.sso_region)

            # If no specific role provided, use the same selection logic
            if not role_name:
                roles = self._get_account_roles(account_id)
                if not roles:
                    raise Exception(f"No roles available for account {account_id}")

                # Use same priority logic: admin > power > first available
                best_role = self._select_best_role(roles)
                role_name = best_role["roleName"]

            # Get role credentials
            response = sso_client.get_role_credentials(
                roleName=role_name, accountId=account_id, accessToken=self.access_token
            )

            credentials = response["roleCredentials"]
            return {
                "accessKeyId": credentials["accessKeyId"],
                "secretAccessKey": credentials["secretAccessKey"],
                "sessionToken": credentials["sessionToken"],
            }

        except ClientError as e:
            if "UnauthorizedException" in str(e):
                # Try re-authentication once
                self._authenticate()
                return self._get_role_credentials(account_id, role_name)
            elif "ForbiddenException" in str(e):
                raise Exception(
                    f"Access denied to role {role_name} in account {account_id}"
                )
            raise Exception(
                f"Failed to get credentials for account {account_id}: {str(e)}"
            )

    def get_available_regions(
        self, accounts: Optional[List[Dict[str, str]]] = None
    ) -> List[str]:
        """Get list of available AWS regions."""
        try:
            console.print("[blue]Getting AWS regions...[/blue]")
            # Use provided accounts or get them if not provided
            if not accounts:
                accounts = self.get_accounts()

            if accounts:
                first_account = accounts[0]
                credentials = self._get_role_credentials(
                    first_account["account_id"], first_account["role_name"]
                )
                ec2_client = boto3.client(
                    "ec2",
                    region_name="us-east-1",
                    aws_access_key_id=credentials["accessKeyId"],
                    aws_secret_access_key=credentials["secretAccessKey"],
                    aws_session_token=credentials["sessionToken"],
                )
                response = ec2_client.describe_regions()
                regions = [region["RegionName"] for region in response["Regions"]]
                console.print(
                    f"[green]✓ Found {len(regions)} available regions[/green]"
                )
                return regions
        except Exception as e:
            if self.verbose:
                console.print(
                    f"[yellow]Could not fetch regions dynamically: {str(e)}[/yellow]"
                )

        # Fallback to common regions
        console.print("[yellow]Using common regions[/yellow]")
        return [
            "us-east-1",
            "us-east-2",
            "us-west-1",
            "us-west-2",
            "eu-west-1",
            "eu-west-2",
            "eu-central-1",
            "eu-north-1",
            "ap-southeast-1",
            "ap-southeast-2",
            "ap-northeast-1",
            "ap-south-1",
            "ca-central-1",
            "sa-east-1",
        ]

    def get_accounts_and_regions_parallel(
        self,
    ) -> Tuple[List[Dict[str, str]], List[str]]:
        """Get accounts and regions in parallel for maximum efficiency."""
        self._ensure_authenticated()

        # Create SSO client
        sso_client = boto3.client("sso", region_name=self.sso_region)

        # First, get list of all accounts (fast)
        console.print("[blue]Getting account list...[/blue]")
        paginator = sso_client.get_paginator("list_accounts")
        raw_accounts = []

        for page in paginator.paginate(accessToken=self.access_token):
            raw_accounts.extend(page["accountList"])

        if not raw_accounts:
            raise Exception("No accessible accounts found via SSO.")

        console.print(f"[green]✓ Found {len(raw_accounts)} accounts[/green]")

        # Start both account role discovery and region discovery in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit region discovery task (as soon as we have one account)
            regions_future = executor.submit(
                self._get_regions_from_account, raw_accounts[0]
            )

            # Submit account role discovery tasks
            accounts = []
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console,
                disable=not console.is_terminal,
            ) as progress:

                task = progress.add_task(
                    "Selecting best role per account...", total=len(raw_accounts)
                )

                # Submit all role-fetching tasks
                future_to_account = {
                    executor.submit(self._get_account_with_roles, account): account
                    for account in raw_accounts
                }

                # Collect results as they complete
                for future in as_completed(future_to_account):
                    account_data = future_to_account[future]
                    try:
                        account_roles = future.result()
                        accounts.extend(account_roles)
                        if self.verbose and account_roles:
                            account_info = account_roles[
                                0
                            ]  # Only one role per account now
                            console.print(
                                f"[green]✓ {account_info['account_name']} using role: {account_info['role_name']}[/green]"
                            )
                        progress.advance(task)
                    except Exception as e:
                        console.print(
                            f"[yellow]⚠ Skipped {account_data['accountName']} ({account_data['accountId']}): {self._get_friendly_error(str(e))}[/yellow]"
                        )
                        progress.advance(task)

            # Get regions result
            try:
                regions = regions_future.result()
            except Exception as e:
                if self.verbose:
                    console.print(
                        f"[yellow]Could not fetch regions dynamically: {str(e)}[/yellow]"
                    )
                console.print("[yellow]Using common regions[/yellow]")
                regions = [
                    "us-east-1",
                    "us-east-2",
                    "us-west-1",
                    "us-west-2",
                    "eu-west-1",
                    "eu-west-2",
                    "eu-central-1",
                    "eu-north-1",
                    "ap-southeast-1",
                    "ap-southeast-2",
                    "ap-northeast-1",
                    "ap-south-1",
                    "ca-central-1",
                    "sa-east-1",
                ]

        console.print(f"[green]✓ Found {len(accounts)} accessible accounts[/green]")
        console.print(f"[green]✓ Found {len(regions)} available regions[/green]")

        if not accounts:
            raise Exception("No accessible accounts found via SSO.")

        return accounts, regions

    def _get_regions_from_account(self, account_data: Dict) -> List[str]:
        """Get regions using the first available account - used for parallel processing."""
        console.print("[blue]Getting AWS regions...[/blue]")

        account_id = account_data["accountId"]
        # Get first available role for this account
        roles = self._get_account_roles(account_id)
        if not roles:
            raise Exception(f"No roles available for account {account_id}")

        role_name = roles[0]["roleName"]
        credentials = self._get_role_credentials(account_id, role_name)

        ec2_client = boto3.client(
            "ec2",
            region_name="us-east-1",
            aws_access_key_id=credentials["accessKeyId"],
            aws_secret_access_key=credentials["secretAccessKey"],
            aws_session_token=credentials["sessionToken"],
        )
        response = ec2_client.describe_regions()
        return [region["RegionName"] for region in response["Regions"]]

    def _get_friendly_error(self, error_message: str) -> str:
        """Convert technical error messages to user-friendly explanations."""
        if "AccessDenied" in error_message or "UnauthorizedException" in error_message:
            return "No permissions"
        elif "Forbidden" in error_message:
            return "Access forbidden"
        elif "Throttling" in error_message or "RequestLimitExceeded" in error_message:
            return "API rate limited"
        elif "InvalidRequest" in error_message:
            return "Invalid request"
        elif "ServiceUnavailable" in error_message:
            return "AWS service unavailable"
        else:
            # Keep it short for the progress display
            return (
                error_message.split(":")[0]
                if ":" in error_message
                else error_message[:50]
            )
