import logging
import os
from dataclasses import dataclass
from typing import Dict, Optional

from atlassian import Confluence
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from markdownify import markdownify as md

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger("mcp-atlassian")


@dataclass
class Document:
    """Class to represent a document with content and metadata."""

    page_content: str
    metadata: Dict[str, any]


class ConfluenceFetcher:
    """Handles fetching and parsing content from Confluence."""

    def __init__(self):
        self.url = os.getenv("CONFLUENCE_CLOUD_URL")
        self.username = os.getenv("CONFLUENCE_CLOUD_USER")
        self.api_key = os.getenv("CONFLUENCE_CLOUD_TOKEN")

        if not all([self.url, self.username, self.api_key]):
            raise ValueError("Missing required Confluence environment variables")

        self.confluence = Confluence(url=self.url, username=self.username, password=self.api_key, cloud=True)

    def _process_html_content(self, html_content: str, space_key: str) -> tuple[str, str]:
        """Process HTML content to replace user refs and page links."""
        soup = BeautifulSoup(html_content, "html.parser")

        # Handle user references
        user_refs = soup.find_all("ri:user")
        account_ids = [user_ref.get("ri:account-id") for user_ref in user_refs if user_ref.get("ri:account-id")]
        unique_account_ids = list(set(account_ids))

        # Fetch user info for all account IDs
        user_info_map = {}
        for account_id in unique_account_ids:
            try:
                endpoint = "/rest/api/user"
                params = {"accountId": account_id}
                user_info = self.confluence.get(endpoint, params=params)
                user_info_map[account_id] = user_info.get("displayName", account_id)
            except Exception as e:
                logger.error(f"Error getting user info for {account_id}: {str(e)}")
                user_info_map[account_id] = account_id

        # Handle page references
        page_refs = soup.find_all("ri:page")
        for page_ref in page_refs:
            title = page_ref.get("ri:content-title")
            if title:
                try:
                    page = self.confluence.get_page_by_title(space=space_key, title=title)
                    if page:
                        page_url = f"{self.url}/wiki/spaces/{space_key}/pages/{page['id']}"
                        # Create new link tag
                        new_tag = soup.new_tag("a", href=page_url)
                        new_tag.string = title
                        # Find the parent ac:link and replace it
                        parent_link = page_ref.find_parent("ac:link")
                        if parent_link:
                            parent_link.replace_with(new_tag)
                except Exception as e:
                    logger.error(f"Error getting page '{title}': {str(e)}")

        # Replace user IDs with names
        for user_ref in user_refs:
            account_id = user_ref.get("ri:account-id")
            if account_id and account_id in user_info_map:
                new_tag = soup.new_tag("span")
                new_tag.string = user_info_map[account_id]
                user_ref.parent.replace_with(new_tag)

        processed_html = str(soup)
        processed_markdown = md(processed_html)

        return processed_html, processed_markdown

    def get_spaces(self, start: int = 0, limit: int = 10):
        """Get all available spaces."""
        return self.confluence.get_all_spaces(start=start, limit=limit)

    def get_page_content(self, page_id: str, clean_html: bool = True) -> Document:
        """Get content of a specific page."""
        page = self.confluence.get_page_by_id(page_id=page_id, expand="body.storage,version,space")
        space_key = page.get("space", {}).get("key", "")

        content = page["body"]["storage"]["value"]
        processed_html, processed_markdown = self._process_html_content(content, space_key)

        # Get author information from version
        version = page.get("version", {})
        author = version.get("by", {})

        metadata = {
            "page_id": page_id,
            "title": page["title"],
            "version": version.get("number"),
            "url": f"{self.url}/wiki/spaces/{space_key}/pages/{page_id}",
            "space_key": space_key,
            "author_name": author.get("displayName"),
            "space_name": page.get("space", {}).get("name", ""),
            "last_modified": version.get("when"),
        }

        return Document(page_content=processed_markdown if clean_html else processed_html, metadata=metadata)

    def get_page_by_title(self, space_key: str, title: str, clean_html: bool = True) -> Optional[Document]:
        """Get page content by space key and title."""
        try:
            page = self.confluence.get_page_by_title(space=space_key, title=title, expand="body.storage,version")

            if not page:
                return None

            content = page["body"]["storage"]["value"]
            if clean_html:
                content = self._clean_html_content(content)

            metadata = {
                "page_id": page["id"],
                "title": page["title"],
                "version": page.get("version", {}).get("number"),
                "space_key": space_key,
                "url": f"{self.url}/wiki/spaces/{space_key}/pages/{page['id']}",
            }

            return Document(page_content=content, metadata=metadata)

        except Exception as e:
            logger.error(f"Error fetching page: {str(e)}")
            return None

    def get_space_pages(
        self, space_key: str, start: int = 0, limit: int = 10, clean_html: bool = True
    ) -> list[Document]:
        """Get all pages from a specific space."""
        pages = self.confluence.get_all_pages_from_space(
            space=space_key, start=start, limit=limit, expand="body.storage"
        )

        documents = []
        for page in pages:
            content = page["body"]["storage"]["value"]
            if clean_html:
                content = self._clean_html_content(content)

            metadata = {
                "page_id": page["id"],
                "title": page["title"],
                "space_key": space_key,
                "version": page.get("version", {}).get("number"),
                "url": f"{self.url}/wiki/spaces/{space_key}/pages/{page['id']}",
            }

            documents.append(Document(page_content=content, metadata=metadata))

        return documents

    def get_page_comments(self, page_id: str, clean_html: bool = True) -> list[Document]:
        """Get all comments for a specific page."""
        page = self.confluence.get_page_by_id(page_id=page_id, expand="space")
        space_key = page.get("space", {}).get("key", "")
        space_name = page.get("space", {}).get("name", "")

        comments = self.confluence.get_page_comments(content_id=page_id, expand="body.view.value,version", depth="all")[
            "results"
        ]

        comment_documents = []
        for comment in comments:
            body = comment["body"]["view"]["value"]
            processed_html, processed_markdown = self._process_html_content(body, space_key)

            # Get author information from version.by instead of author
            author = comment.get("version", {}).get("by", {})

            metadata = {
                "page_id": page_id,
                "comment_id": comment["id"],
                "last_modified": comment.get("version", {}).get("when"),
                "type": "comment",
                "author_name": author.get("displayName"),
                "space_key": space_key,
                "space_name": space_name,
            }

            comment_documents.append(
                Document(page_content=processed_markdown if clean_html else processed_html, metadata=metadata)
            )

        return comment_documents

    def search(self, cql: str, limit: int = 10, clean_html: bool = True) -> list[Document]:
        """Search content using Confluence Query Language (CQL)."""
        results = self.confluence.cql(cql=cql, limit=limit, expand="body.storage,version")

        documents = []
        for result in results.get("results", []):
            content = result.get("content", {})
            if content.get("type") == "page":
                # Get the full page details to access all metadata
                doc = self.get_page_content(content["id"], clean_html)
                documents.append(doc)

        return documents
