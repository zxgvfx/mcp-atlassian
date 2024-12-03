import logging
import os
from dataclasses import dataclass
from typing import Dict, Optional

from atlassian import Confluence
from bs4 import BeautifulSoup
from dotenv import load_dotenv

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

    def _clean_html_content(self, html_content: str) -> str:
        """Clean HTML content and return plain text."""
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text(separator=" ", strip=True)

    def get_spaces(self, start: int = 0, limit: int = 10):
        """Get all available spaces."""
        return self.confluence.get_all_spaces(start=start, limit=limit)

    def get_page_content(self, page_id: str, clean_html: bool = True) -> Document:
        """Get content of a specific page."""
        page = self.confluence.get_page_by_id(page_id=page_id, expand="body.storage,version")

        content = page["body"]["storage"]["value"]
        if clean_html:
            content = self._clean_html_content(content)

        metadata = {
            "page_id": page_id,
            "title": page["title"],
            "version": page.get("version", {}).get("number"),
            "url": f"{self.url}/wiki/spaces/{page.get('space', {}).get('key')}/pages/{page_id}",
        }

        return Document(page_content=content, metadata=metadata)

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
        comments = self.confluence.get_page_comments(content_id=page_id, expand="body.view.value", depth="all")[
            "results"
        ]

        comment_documents = []
        for comment in comments:
            body = comment["body"]["view"]["value"]
            if clean_html:
                body = self._clean_html_content(body)

            metadata = {
                "page_id": page_id,
                "comment_id": comment["id"],
                "created": comment.get("created"),
                "type": "comment",
                "author": comment.get("author", {}).get("displayName"),
            }

            comment_documents.append(Document(page_content=body, metadata=metadata))

        return comment_documents

    def search(self, cql: str, limit: int = 10, clean_html: bool = True) -> list[Document]:
        """Search content using Confluence Query Language (CQL)."""
        results = self.confluence.cql(cql=cql, limit=limit, expand="body.storage")

        documents = []
        for result in results.get("results", []):
            content = result.get("content", {})
            if content.get("type") == "page":
                doc = self.get_page_content(content["id"], clean_html)
                # Add page ID to metadata if not already present
                if "page_id" not in doc.metadata:
                    doc.metadata["page_id"] = content["id"]
                documents.append(doc)

        return documents
