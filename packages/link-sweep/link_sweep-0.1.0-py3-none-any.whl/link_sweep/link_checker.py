import httpx
import markdown_parser
import logging


class LinkChecker:
    def __init__(self, directory):
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing LinkChecker for {directory}")

        self.pages = markdown_parser.get_files(directory)  # content/
        self.links_data = markdown_parser.get_md_links(self.pages)
        # [{'text': 'link1', 'url': 'https:/bla.bla', 'file': 'filepath/post1.md'},
        # {'text': 'link2', 'url': 'https://blabla.bla', 'file': 'filepath/post2'}]

        # get links from group 1 (urls) from get_md_links function
        self.links = [link["url"] for link in self.links_data]

        self.bad_links = []
        self._checked = False

    def check_links(self):
        self.logger.info(f"Starting link check for {len(self.links)} links")

        for i, link in enumerate(self.links):
            self.logger.debug(f"Checking link {i + 1}/{len(self.links)}: {link}")
            try:
                response = httpx.get(link, timeout=10.0)
                if response.status_code >= 400:
                    self.logger.warning(
                        f"Dead link found: {link} (status: {response.status_code})"
                    )
                    self.bad_links.append(link)
                else:
                    self.logger.debug(
                        f"Link OK: {link} (status: {response.status_code})"
                    )
            except Exception as e:
                self.logger.error(f"Error checking {link}: {e}")

        self._checked = True

    def remove_bad_links(self):
        if not self._checked:
            self.check_links()

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
