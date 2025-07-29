import click
import logging
from link_checker import LinkChecker
import sys


@click.group()
def main():
    pass


@main.command()
@click.option("--verbose", "-v", is_flag=True, help="Show detailed logging information")
@click.option(
    "--remove-dead", "-rmd", is_flag=True, help="Remove dead links from the source"
)
@click.argument("directory", default="content/")  # Default for most SSGs
def check_links(verbose, remove_dead, directory):
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
            level=logging.WARNING,
            format="%(levelname)s: %(message)s",
        )

    logger = logging.getLogger(__name__)

    try:
        click.echo(f"🔍 Checking links in: {directory}")
        checker = LinkChecker(directory)

        checker.check_links()
        total_links = len(checker.links)
        bad_links_count = len(checker.bad_links)
        good_links_count = total_links - bad_links_count

        click.echo("\n📊 Results:")
        click.echo(f"   Total links checked: {total_links}")
        click.echo(f"   ✅ Good links: {good_links_count}")
        click.echo(f"   ❌ Bad links: {bad_links_count}")

        if bad_links_count > 0:
            click.echo("\n💥 Bad links found:")
            for link in checker.bad_links:
                click.echo(f"   - {link}")

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
