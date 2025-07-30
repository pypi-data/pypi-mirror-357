"""Main CLI interface for Haystack."""

from typing import Optional

import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.command()
@click.argument("search_term", required=False)
@click.option(
    "--region",
    "-r",
    help="Specific region to search (searches all regions if not specified)",
)
@click.option("--sso-start-url", help="AWS SSO start URL (will prompt if not provided)")
@click.option(
    "--sso-region", default="us-east-1", help="AWS SSO region (default: us-east-1)"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option(
    "--clear", is_flag=True, help="Clear saved configuration and cached credentials"
)
@click.pass_context
def main(
    ctx: click.Context,
    search_term: Optional[str] = None,
    region: Optional[str] = None,
    sso_start_url: Optional[str] = None,
    sso_region: str = "us-east-1",
    verbose: bool = False,
    clear: bool = False,
) -> None:
    """Find CloudFormation stacks containing the search term across AWS accounts using SSO.

    SEARCH_TERM: Text to search for in CloudFormation stack names (partial matches supported)

    This tool uses AWS SSO to dynamically discover all accounts and roles
    you have access to, then searches for CloudFormation stacks containing
    the search term across all accessible accounts and regions.
    """
    # Handle clear flag
    if clear:
        from .config import HaystackConfig

        config = HaystackConfig()
        config.clear_config()
        console.print("[green]✓ Configuration and cache cleared![/green]")
        console.print(
            "[blue]You'll be prompted for SSO configuration on next run.[/blue]"
        )
        return

    # If no search term provided, show help
    if not search_term:
        console.print(ctx.get_help())
        return

    # Perform the search
    if verbose:
        console.print(f"[blue]Searching for stacks containing: '{search_term}'[/blue]")
        if region:
            console.print(f"[blue]Limiting search to region: {region}[/blue]")
        if sso_start_url:
            console.print(f"[blue]Using SSO start URL: {sso_start_url}[/blue]")

    try:
        from .stack_finder import StackFinder

        finder = StackFinder(
            sso_start_url=sso_start_url, sso_region=sso_region, verbose=verbose
        )
        results = finder.find_stack(search_term, region=region)

        if not results:
            console.print(
                f"[red]No stacks containing '{search_term}' found in any accessible accounts.[/red]"
            )
            return

        table = Table(
            title=f"CloudFormation Stacks containing '{search_term}' ({len(results)} found)"
        )
        table.add_column("Stack Name", style="cyan", no_wrap=False)
        table.add_column("Account ID", style="green")
        table.add_column("Account Name", style="green")
        table.add_column("Region", style="yellow")
        table.add_column("Status", style="magenta")

        for result in results:
            table.add_row(
                result["stack_name"],
                result["account_id"],
                result["account_name"],
                result["region"],
                result["stack_status"],
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        if verbose:
            import traceback

            console.print(traceback.format_exc())


if __name__ == "__main__":
    main()
