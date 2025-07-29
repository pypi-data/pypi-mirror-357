"""Command line interface for Link Sweep."""

import asyncio
import logging
import sys

import click

from .link_checker import LinkChecker


@click.group()
def main():
    """Link Sweep CLI - A tool for checking and cleaning dead links in Markdown files."""  # noqa: E501
    pass


@main.command()
@click.option("--verbose", "-v", is_flag=True, help="Show detailed logging information")
@click.option(
    "--remove-dead", "-rmd", is_flag=True, help="Remove dead links from the source"
)
@click.option(
    "--timeout",
    "-t",
    default=10.0,
    type=float,
    help="Timeout in seconds for HTTP requests (default: 10.0)",
)
@click.argument("directory", default="content/")  # Default for most SSGs
def check_links(verbose, remove_dead, timeout, directory):
    """Check for dead links in the provided source."""

    # Set up logging - minimal for normal mode, detailed for verbose
    if verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        # For normal mode, only show warnings and errors with minimal format
        logging.basicConfig(
            level=logging.INFO,
            format="%(levelname)s: %(message)s",
        )

    logger = logging.getLogger(__name__)

    try:
        click.echo(f"🔍 Checking links in: {directory}")
        click.echo(f"⏱️  Using timeout: {timeout} seconds")

        checker = LinkChecker(directory, timeout=timeout)

        # Run the async check_links method
        asyncio.run(checker.check_links())

        total_links = len(checker.links)
        bad_links_count = len(checker.bad_links)
        timed_out_count = len(checker.timed_out_links)
        good_links_count = total_links - bad_links_count

        click.echo("\n📊 Results:")
        click.echo(f"   Total links checked: {total_links}")
        click.echo(f"   ✅ Good links: {good_links_count}")
        click.echo(f"   ❌ Bad links: {bad_links_count}")
        if timed_out_count > 0:
            click.echo(f"   ⏰ Timed out links: {timed_out_count}")

        if bad_links_count > 0:
            click.echo("\n💥 Bad links found:")
            for link in checker.bad_links:
                status_icon = "⏰" if link in checker.timed_out_links else "❌"
                click.echo(f"   {status_icon} {link}")

            if remove_dead:
                click.echo(f"\n🔧 Removing {bad_links_count} bad links...")
                checker.remove_bad_links()
                click.echo("✅ Bad links have been replaced with their text!")
            else:
                click.echo("\n💡 Use -rmd flag to replace bad links with their text")
        else:
            click.echo("\n🎉 All links are working!")

    except FileNotFoundError:
        click.echo(f"❌ Error: Directory '{directory}' not found", err=True)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
