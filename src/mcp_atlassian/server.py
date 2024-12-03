import json
import logging
from collections.abc import Sequence
from typing import Any

from mcp.server import Server
from mcp.types import Resource, TextContent, Tool
from pydantic import AnyUrl

from .confluence import ConfluenceFetcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-atlassian")

# Initialize the content fetcher
fetcher = ConfluenceFetcher()
app = Server("mcp-atlassian")


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available Confluence spaces as resources."""
    spaces = fetcher.get_spaces()
    return [
        Resource(
            uri=AnyUrl(f"confluence://{space['key']}"),
            name=f"Confluence Space: {space['name']}",
            mimeType="text/plain",
            description=space.get("description", {}).get("plain", {}).get("value", ""),
        )
        for space in spaces
    ]


@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Read content from Confluence."""
    parts = str(uri).replace("confluence://", "").split("/")

    # Handle space listing
    if len(parts) == 1:
        space_key = parts[0]
        documents = fetcher.get_space_pages(space_key)
        content = []
        for doc in documents:
            content.append(f"# {doc.metadata['title']}\n\n{doc.page_content}\n---")
        return "\n\n".join(content)

    # Handle specific page
    elif len(parts) >= 3 and parts[1] == "pages":
        space_key = parts[0]
        title = parts[2]
        doc = fetcher.get_page_by_title(space_key, title)

        if not doc:
            raise ValueError(f"Page not found: {title}")

        return doc.page_content

    raise ValueError(f"Invalid resource URI: {uri}")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Confluence tools."""
    return [
        Tool(
            name="search_confluence",
            description="Search Confluence content using CQL",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "CQL query string (e.g. 'type=page AND space=DEV')"},
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results (1-50)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_page_content",
            description="Get content of a specific Confluence page by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {"type": "string", "description": "Confluence page ID"},
                    "include_metadata": {
                        "type": "boolean",
                        "description": "Whether to include page metadata",
                        "default": True,
                    },
                },
                "required": ["page_id"],
            },
        ),
        Tool(
            name="get_page_comments",
            description="Get comments for a specific Confluence page",
            inputSchema={
                "type": "object",
                "properties": {"page_id": {"type": "string", "description": "Confluence page ID"}},
                "required": ["page_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool calls for Confluence operations."""
    try:
        if name == "search_confluence":
            limit = min(int(arguments.get("limit", 10)), 50)
            documents = fetcher.search(arguments["query"], limit)
            search_results = [
                {
                    "page_id": doc.metadata["page_id"],
                    "title": doc.metadata["title"],
                    "space": doc.metadata.get("space_key"),
                    "excerpt": doc.page_content[:500] + "...",
                    "url": doc.metadata.get("url", ""),
                }
                for doc in documents
            ]

            return [TextContent(type="text", text=json.dumps(search_results, indent=2))]

        elif name == "get_page_content":
            doc = fetcher.get_page_content(arguments["page_id"])
            include_metadata = arguments.get("include_metadata", True)

            if include_metadata:
                result = {"content": doc.page_content, "metadata": doc.metadata}
            else:
                result = {"content": doc.page_content}

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_page_comments":
            comments = fetcher.get_page_comments(arguments["page_id"])
            formatted_comments = [
                {
                    "author": comment.metadata["author"],
                    "created": comment.metadata["created"],
                    "content": comment.page_content,
                }
                for comment in comments
            ]

            return [TextContent(type="text", text=json.dumps(formatted_comments, indent=2))]

        raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        raise RuntimeError(f"Tool execution failed: {str(e)}")


async def main():
    # Import here to avoid issues with event loops
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
