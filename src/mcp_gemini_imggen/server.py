#!/usr/bin/env python3
"""Gemini Image Generation MCP Server - Minimal implementation returning only file paths."""

import os
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from google import genai
from google.genai.types import GenerateContentConfig
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required")

OUTPUT_DIR_STR = os.getenv("OUTPUT_DIR")
if not OUTPUT_DIR_STR:
    raise ValueError("OUTPUT_DIR environment variable is required")

OUTPUT_DIR = Path(OUTPUT_DIR_STR).expanduser()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Initialize Gemini client
client = genai.Client(api_key=API_KEY)

# Create MCP server
app = Server("gemini-image-generator")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="generate_image_from_text",
            description="Generate an image from a text prompt using Gemini 2.5 Flash. Returns only the file path.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Text description of the image to generate",
                    }
                },
                "required": ["prompt"],
            },
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    if name != "generate_image_from_text":
        raise ValueError(f"Unknown tool: {name}")

    prompt = arguments.get("prompt")
    if not prompt:
        raise ValueError("prompt is required")

    try:
        # Generate image
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=prompt,
            config=GenerateContentConfig(
                response_modalities=["image"],
            ),
        )

        # Extract base64 image data from response
        if not response.candidates or not response.candidates[0].content.parts:
            raise ValueError("No image generated")

        part = response.candidates[0].content.parts[0]
        if not hasattr(part, "inline_data") or not part.inline_data:
            raise ValueError("No image data in response")

        image_data = part.inline_data.data

        # Save to file with timestamp (ISO 8601 UTC format)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        filepath = OUTPUT_DIR / f"{timestamp}.png"

        # Save image data (check if it's already binary or base64-encoded)
        import base64
        with open(filepath, "wb") as f:
            # If image_data is bytes, write directly; if string, decode from base64
            if isinstance(image_data, bytes):
                f.write(image_data)
            else:
                f.write(base64.b64decode(image_data))

        # Return ONLY the file path as text
        return [TextContent(type="text", text=str(filepath))]

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        raise RuntimeError(f"Image generation failed: {type(e).__name__}: {str(e)}\n\nTraceback:\n{error_details}")


async def async_main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


def main():
    """Entry point for the MCP server."""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
