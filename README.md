# mcp-gemini-imggen

A lightweight, token-optimized MCP server for generating images using Google's Gemini 2.5 Flash Image model.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-required-green.svg)](https://github.com/astral-sh/uv)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Why This Implementation?

### The Problem with Existing Solutions

Most Gemini image generation MCP servers return base64-encoded image data directly in the response, causing severe issues with Claude Code:

- **Response size**: ~2,400,000 tokens per image
- **Claude Code limit**: 25,000 tokens (hard cap)
- **Result**: `MCP tool response exceeded token limit` error ❌

### Our Solution

This implementation saves images to disk and returns **only the file path**:

- **Response size**: ~20 tokens (120,000× reduction 🚀)
- **Result**: Works perfectly with Claude Code ✅

### Token Optimization (Verified)

| Implementation | Response | Token Usage | Result |
|----------------|----------|-------------|--------|
| **Existing servers** | Base64 data | 2.4M tokens | ❌ Error |
| **This implementation** | File path | ~20 tokens | ✅ Works |


## ✨ Features

- **Token-optimized**: Returns file paths only (~20 tokens vs 2.4M tokens)
- **Claude Code compatible**: Works within the 25,000 token limit
- **Lightweight**: Minimal dependencies
- **Fast**: Quick startup with uv's Rust-powered speed
- **Simple**: No build step, direct execution with uv
- **Modern**: Uses latest Python toolchain (uv + Python 3.10+)

## 📋 Requirements

- **Python 3.10+**
- **[uv](https://github.com/astral-sh/uv)** - Modern Python package manager (required)
- **Gemini API key** from [Google AI Studio](https://aistudio.google.com/apikey)

### Why uv?

- ⚡ **10-100× faster** than pip for installations
- 🔒 **Reliable** dependency resolution
- 🎯 **Simple** project-based execution
- 🆕 **Modern** Python standard (2024-2025)

### Installing uv

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

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/mcp-gemini-imggen.git
cd mcp-gemini-imggen

# 2. Set up your API key
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 3. Add to Claude Code (one command!)
claude mcp add -s user gemini-imggen uv --directory $(pwd) run mcp-gemini-imggen
```

That's it! 🎉

## 🔧 Configuration Details

### Using Claude Code CLI (Recommended)

```bash
claude mcp add -s user gemini-imggen uv --directory /absolute/path/to/mcp-gemini-imggen run mcp-gemini-imggen
```

### Manual Configuration

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

**Important**:
- Use **absolute paths** (not `~`)
- Example: `/Users/yourname/dev/mcp-gemini-imggen` ✅
- Not: `~/dev/mcp-gemini-imggen` ❌

## 💡 Usage

Once configured, use the MCP tool in Claude Code:

```
Generate a flat design style cute cat illustration
```

The server will:
1. Generate the image using Gemini 2.5 Flash Image
2. Save it to `~/Pictures/ai/gemini_YYYY-MM-DD_HH-MM-SS.png`
3. Return only the file path (~20 tokens)

Claude Code will automatically display the generated image.

## 🏗️ Project Structure

```
mcp-gemini-imggen/
├── src/
│   └── mcp_gemini_imggen/
│       ├── __init__.py
│       ├── __main__.py
│       └── server.py          # Main implementation (121 lines)
├── .env.example               # API key template
├── .gitignore                 # Protects API keys
├── LICENSE                    # MIT License
├── pyproject.toml             # Project metadata
└── README.md                  # This file
```

## 🔬 Technical Details

### Token Optimization Breakdown

**Why existing implementations fail**:

1. Base64 encoding increases size by ~33%
2. 1536×1536 PNG ≈ 1.4MB → Base64 ≈ 1.9MB
3. Token conversion: 1.9MB ÷ 4 chars/token ≈ 475,000 tokens
4. Multiple images: 4 × 475,000 ≈ 1,900,000 tokens
5. JSON wrapper: +500,000 tokens
6. **Total: ~2,400,000 tokens** → Exceeds 25,000 limit

**Our approach**:
```python
# ❌ Existing (2.4M tokens)
return {"type": "image", "data": "iVBORw0KGgo...", "mimeType": "image/png"}

# ✅ Ours (20 tokens)
return [{"type": "text", "text": "/Users/name/Pictures/ai/gemini_2025-10-15.png"}]
```

### Using uv vs pip

| Feature | uv | pip |
|---------|----|----|
| **Speed** | 10-100× faster | Standard |
| **Execution** | `uv run` (no install needed) | Requires `pip install` |
| **Path Issues** | None (project-based) | Potential conflicts |
| **This Project** | ✅ Required | ❌ Not supported |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- Uses [Google Gemini API](https://ai.google.dev/)
- Powered by [uv](https://github.com/astral-sh/uv) - Astral's blazing-fast package manager

## 📝 Changelog

### 1.0.0 (2025-10-15)
- Initial release
- Token-optimized implementation (file path only)
- Gemini 2.5 Flash Image support
- Claude Code compatibility verified
- uv-based dependency management

## 🐛 Troubleshooting

### "uv: command not found"
Install uv first:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### "GEMINI_API_KEY environment variable is required"
1. Get your API key from [Google AI Studio](https://aistudio.google.com/apikey)
2. Add to `.env`: `GEMINI_API_KEY=your-key-here`

### Images not generating
1. Check your API key is valid
2. Ensure you have quota remaining
3. Check `~/Pictures/ai/` directory permissions

## 🔗 Links

- [Report Issues](https://github.com/YOUR_USERNAME/mcp-gemini-imggen/issues)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [Google Gemini API](https://ai.google.dev/)
- [uv Documentation](https://docs.astral.sh/uv/)
