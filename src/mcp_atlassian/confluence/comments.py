"""Module for Confluence comment operations."""

import logging

import requests

from ..models.confluence import ConfluenceComment
from .client import ConfluenceClient

logger = logging.getLogger("mcp-atlassian")


class CommentsMixin(ConfluenceClient):
    """Mixin for Confluence comment operations."""

    def get_page_comments(
        self, page_id: str, *, return_markdown: bool = True
    ) -> list[ConfluenceComment]:
        """
        Get all comments for a specific page.

        Args:
            page_id: The ID of the page to get comments from
            return_markdown: When True, returns content in markdown format,
                           otherwise returns raw HTML (keyword-only)

        Returns:
            List of ConfluenceComment models containing comment content and metadata
        """
        try:
            # Get page info to extract space details
            page = self.confluence.get_page_by_id(page_id=page_id, expand="space")
            space_key = page.get("space", {}).get("key", "")

            # Get comments with expanded content
            comments_response = self.confluence.get_page_comments(
                content_id=page_id, expand="body.view.value,version", depth="all"
            )

            # Process each comment
            comment_models = []
            for comment_data in comments_response.get("results", []):
                # Get the content based on format
                body = comment_data["body"]["view"]["value"]
                processed_html, processed_markdown = (
                    self.preprocessor.process_html_content(body, space_key=space_key)
                )

                # Create a copy of the comment data to modify
                modified_comment_data = comment_data.copy()

                # Modify the body value based on the return format
                if "body" not in modified_comment_data:
                    modified_comment_data["body"] = {}
                if "view" not in modified_comment_data["body"]:
                    modified_comment_data["body"]["view"] = {}

                # Set the appropriate content based on return format
                modified_comment_data["body"]["view"]["value"] = (
                    processed_markdown if return_markdown else processed_html
                )

                # Create the model with the processed content
                comment_model = ConfluenceComment.from_api_response(
                    modified_comment_data,
                    base_url=self.config.url,
                )

                comment_models.append(comment_model)

            return comment_models

        except KeyError as e:
            logger.error(f"Missing key in comment data: {str(e)}")
            return []
        except requests.RequestException as e:
            logger.error(f"Network error when fetching comments: {str(e)}")
            return []
        except (ValueError, TypeError) as e:
            logger.error(f"Error processing comment data: {str(e)}")
            return []
        except Exception as e:  # noqa: BLE001 - Intentional fallback with full logging
            logger.error(f"Unexpected error fetching comments: {str(e)}")
            logger.debug("Full exception details for comments:", exc_info=True)
            return []

    def add_comment(self, page_id: str, content: str) -> ConfluenceComment | None:
        """
        Add a comment to a Confluence page.

        Args:
            page_id: The ID of the page to add the comment to
            content: The content of the comment (in Confluence storage format)

        Returns:
            ConfluenceComment object if comment was added successfully, None otherwise
        """
        try:
            # Get page info to extract space details
            page = self.confluence.get_page_by_id(page_id=page_id, expand="space")
            space_key = page.get("space", {}).get("key", "")

            # Convert markdown to Confluence storage format if needed
            # The atlassian-python-api expects content in Confluence storage format
            if not content.strip().startswith("<"):
                # If content doesn't appear to be HTML/XML, treat it as markdown
                content = self.preprocessor.markdown_to_confluence_storage(content)

            # Add the comment via the Confluence API
            response = self.confluence.add_comment(page_id, content)

            if not response:
                logger.error("Failed to add comment: empty response")
                return None

            # Process the comment to return a consistent model
            processed_html, processed_markdown = self.preprocessor.process_html_content(
                response.get("body", {}).get("view", {}).get("value", ""),
                space_key=space_key,
            )

            # Modify the response to include processed content
            modified_response = response.copy()
            if "body" not in modified_response:
                modified_response["body"] = {}
            if "view" not in modified_response["body"]:
                modified_response["body"]["view"] = {}

            modified_response["body"]["view"]["value"] = processed_markdown

            # Create and return the comment model
            return ConfluenceComment.from_api_response(
                modified_response,
                base_url=self.config.url,
            )

        except requests.RequestException as e:
            logger.error(f"Network error when adding comment: {str(e)}")
            return None
        except (ValueError, TypeError, KeyError) as e:
            logger.error(f"Error processing comment data: {str(e)}")
            return None
        except Exception as e:  # noqa: BLE001 - Intentional fallback with full logging
            logger.error(f"Unexpected error adding comment: {str(e)}")
            logger.debug("Full exception details for adding comment:", exc_info=True)
            return None
