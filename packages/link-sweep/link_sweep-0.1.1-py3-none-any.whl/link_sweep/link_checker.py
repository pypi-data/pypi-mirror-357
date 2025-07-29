"""Asynchronous link checker module for markdown files."""

import asyncio
import logging

import httpx

from . import markdown_parser


class LinkChecker:
    """Asynchronous link checker for markdown files."""

    def __init__(self, directory, timeout=10.0):
        """Initialize LinkChecker with directory path and timeout settings."""
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing LinkChecker for {directory}")
        self.timeout = timeout

        self.pages = markdown_parser.get_files(directory)  # content/
        self.links_data = markdown_parser.get_md_links(self.pages)
        # [{'text': 'link1', 'url': 'https:/bla.bla', 'file': 'filepath/post1.md'},
        # {'text': 'link2', 'url': 'https://blabla.bla', 'file': 'filepath/post2'}]

        # get links from group 1 (urls) from get_md_links function
        self.links = [link["url"] for link in self.links_data]

        self.bad_links = []
        self.timed_out_links = []
        self._checked = False

    async def _check_single_link(self, session, link):
        """Check a single link asynchronously."""
        try:
            response = await session.get(link, timeout=self.timeout)
            if response.status_code >= 400:
                self.logger.warning(
                    f"Dead link found: {link} (status: {response.status_code})"
                )
                return link, "dead"
            else:
                self.logger.debug(f"Link OK: {link} (status: {response.status_code})")
                return link, "ok"
        except (httpx.TimeoutException, asyncio.TimeoutError):
            self.logger.warning(f"Link timed out: {link}")
            return link, "timeout"
        except Exception as e:
            self.logger.error(f"Error checking {link}: {e}")
            return link, "error"

    async def check_links(self):
        """Check all links asynchronously."""
        self.logger.info(f"Starting async link check for {len(self.links)} links")

        async with httpx.AsyncClient() as session:
            # Create tasks for all links
            tasks = [self._check_single_link(session, link) for link in self.links]

            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for i, result in enumerate(results):
                if isinstance(result, BaseException):
                    self.logger.error(f"Unexpected error for {self.links[i]}: {result}")
                    self.bad_links.append(self.links[i])
                else:
                    link, status = result
                    if status in ["dead", "error"]:
                        self.bad_links.append(link)
                    elif status == "timeout":
                        self.bad_links.append(link)
                        self.timed_out_links.append(link)

        self._checked = True

    def remove_bad_links(self):
        """Remove bad links from markdown files by replacing them with their text content."""  # noqa: E501
        if not self._checked:
            # Run the async method synchronously if not already checked
            asyncio.run(self.check_links())

        if not self.bad_links:
            self.logger.info("No bad links to remove")
            return

        files_to_update = {}
        for link_data in self.links_data:
            if link_data["url"] in self.bad_links:
                target_file = link_data["file"]
                if target_file not in files_to_update:
                    files_to_update[target_file] = []
                files_to_update[target_file].append(link_data)

        for target_file, bad_links in files_to_update.items():
            self.logger.info(f"Removing {len(bad_links)} bad links from {target_file}")
            markdown_parser.replace_link(target_file, bad_links)
