"""Markdown file parsing utilities for link extraction and replacement."""

from pathlib import Path
import re


def get_files(directory):
    """Simple recursive search for .md files in target directory."""
    p = Path(directory)
    md_files = []
    for file in p.rglob("*.md"):
        md_files.append(str(file))
    if not md_files:
        raise Exception("No markdown files in this directory")
    return md_files


def get_md_links(md_file_path: list):
    """Creates two groups out of markdown links."""
    pattern = r'\[([^\]]+)\]\((https?:\/\/[^\s\)"]+)\)'
    links = []

    for file in md_file_path:
        try:
            with open(file, "r", encoding="utf-8") as md:
                content = md.read()
                matches = re.findall(pattern, content)
                for text, url in matches:
                    links.append({"text": text, "url": url, "file": file})
        except FileNotFoundError:
            print(f"File not found: {file}")
        except Exception as e:
            print(f"Error reading {file}: {e}")
    return links


def replace_link(md_file_path, bad_links):
    """Replace bad links with their text content in markdown files."""
    try:
        with open(md_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Apply all replacements
        for link in bad_links:
            escaped_url = re.escape(link["url"])
            escaped_text = re.escape(link["text"])
            pattern = rf"\[{escaped_text}\]\({escaped_url}\)"
            content = re.sub(pattern, link["text"], content)

        with open(md_file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return True

    except Exception as e:
        print(f"Error updating {md_file_path}: {e}")
        return False