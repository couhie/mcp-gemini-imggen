# Gemini Image Generation MCP Server

A token-optimized MCP server that enables Gemini image generation in MCP clients by returning file paths instead of base64 data.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-required-green.svg)](https://github.com/astral-sh/uv)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why This Exists

Existing Gemini image generation MCP servers fail in Claude Code with `MCP tool response exceeded token limit` errors. They return base64-encoded image data (~2.4M tokens per image), exceeding Claude Code's 25,000 token limit.

**This implementation solves the problem** by saving images to disk and returning only file paths (~20 tokens) — a **120,000× reduction** in token usage.

| Implementation | Response | Tokens | Result |
|----------------|----------|--------|--------|
| Existing servers | Base64 data | 2.4M | ❌ Error |
| This server | File path | ~20 | ✅ Works |

## Features

- Token-optimized: Returns file paths only
- Claude Code compatible: Works within 25,000 token limit
- Lightweight: Minimal dependencies
- Fast: uv-powered startup
- Simple: No build step required

## Requirements

- **Python 3.10+**
- **[uv](https://github.com/astral-sh/uv)** - Modern Python package manager (10-100× faster than pip)
- **Gemini API key** from [Google AI Studio](https://aistudio.google.com/apikey)

### Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Homebrew
brew install uv

# Verify installation
uv --version
```

## Quick Start

```bash
# 1. Clone and navigate
git clone https://github.com/couhie/mcp-gemini-imggen.git
cd mcp-gemini-imggen

# 2. Configure settings
cp .env.example .env
# Edit .env and set:
#   GEMINI_API_KEY - Your API key from Google AI Studio
#   OUTPUT_DIR - Directory for generated images (e.g., ~/Pictures/ai)
#                Directory will be created automatically if it doesn't exist

# 3. Add to Claude Code
claude mcp add -s user gemini-imggen uv -- --directory $(pwd) run mcp-gemini-imggen
```

## Configuration

### Claude Code CLI (Recommended)

```bash
claude mcp add -s user gemini-imggen uv -- --directory /absolute/path/to/mcp-gemini-imggen run mcp-gemini-imggen
```

### Manual Setup

Add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "gemini-imggen": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/mcp-gemini-imggen",
        "run",
        "mcp-gemini-imggen"
      ],
      "env": {}
    }
  }
}
```

**Note**: Use absolute paths, not `~` (e.g., `/Users/yourname/dev/mcp-gemini-imggen`)

## Usage

Once configured, use the MCP tool in Claude Code:

```
Generate a flat design style cute cat illustration
```

The server will:
1. Generate the image using Gemini 2.5 Flash Image
2. Save it to `$OUTPUT_DIR/gemini_YYYY-MM-DD_HH-MM-SS.png`
3. Return only the file path (~20 tokens)

Claude Code will automatically display the generated image.

## Technical Details

### Token Optimization

Base64-encoded responses cause token explosion:

1. 1536×1536 PNG ≈ 1.4MB → Base64 ≈ 1.9MB (33% overhead)
2. Token conversion: 1.9MB ÷ 4 chars/token ≈ 475,000 tokens
3. Multiple images (4×): ~1,900,000 tokens
4. JSON wrapper: +500,000 tokens
5. **Total: ~2,400,000 tokens** (exceeds 25,000 limit)

**Solution**: Return file path instead of data

```python
# ❌ Existing: 2.4M tokens
{"type": "image", "data": "iVBORw0KGgo...", "mimeType": "image/png"}

# ✅ This server: ~20 tokens
[{"type": "text", "text": "/Users/name/Pictures/ai/gemini_2025-10-15.png"}]
```

## Troubleshooting

### "uv: command not found"
Install uv first:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### "GEMINI_API_KEY environment variable is required"
Get your API key from [Google AI Studio](https://aistudio.google.com/apikey) and add to `.env`

### "OUTPUT_DIR environment variable is required"
Set your desired output directory in `.env` (e.g., `OUTPUT_DIR=~/Pictures/ai`). The directory will be created automatically if it doesn't exist.

### Images not generating
- Verify API key is valid at [Google AI Studio](https://aistudio.google.com/)
- Check API quota limits
- Verify OUTPUT_DIR path is valid (parent directories must be writable)

## Contributing

Contributions are welcome! Please submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Google Gemini API](https://ai.google.dev/)
- [uv Package Manager](https://github.com/astral-sh/uv)
