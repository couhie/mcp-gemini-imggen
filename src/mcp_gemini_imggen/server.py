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
from google.genai.types import GenerateContentConfig, Part
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
        ),
        Tool(
            name="generate_image_from_image",
            description="Transform or edit an existing image using Gemini 2.5 Flash. Returns only the file path.",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_image_path": {
                        "type": "string",
                        "description": "Path to the input image file (supports ~/ expansion)",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Instruction for how to transform or edit the image",
                    }
                },
                "required": ["input_image_path", "prompt"],
            },
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    if name == "generate_image_from_text":
        return await _generate_image_from_text(arguments)
    elif name == "generate_image_from_image":
        return await _generate_image_from_image(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def _generate_image_from_text(arguments: Any) -> list[TextContent]:
    """Generate image from text prompt."""
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

        # Extract and save image
        return _save_generated_image(response)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        raise RuntimeError(f"Image generation failed: {type(e).__name__}: {str(e)}\n\nTraceback:\n{error_details}")


async def _generate_image_from_image(arguments: Any) -> list[TextContent]:
    """Generate image from existing image and prompt."""
    input_image_path = arguments.get("input_image_path")
    prompt = arguments.get("prompt")

    if not input_image_path:
        raise ValueError("input_image_path is required")
    if not prompt:
        raise ValueError("prompt is required")

    try:
        # Expand and validate input path
        input_path = Path(input_image_path).expanduser().resolve()
        if not input_path.exists():
            raise ValueError(f"Input image not found: {input_path}")
        if not input_path.is_file():
            raise ValueError(f"Input path is not a file: {input_path}")

        # Read input image
        with open(input_path, "rb") as f:
            image_data = f.read()

        # Determine MIME type
        suffix = input_path.suffix.lower()
        mime_type_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
        }
        mime_type = mime_type_map.get(suffix, "image/png")

        # Generate image with input image and prompt
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[
                Part.from_bytes(data=image_data, mime_type=mime_type),
                prompt
            ],
            config=GenerateContentConfig(
                response_modalities=["image"],
            ),
        )

        # Extract and save image
        return _save_generated_image(response)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        raise RuntimeError(f"Image transformation failed: {type(e).__name__}: {str(e)}\n\nTraceback:\n{error_details}")


def _save_generated_image(response) -> list[TextContent]:
    """Extract image from response and save to file."""
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
