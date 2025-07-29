# Grep MCP Server

A **Model Context Protocol (MCP)** server that provides GitHub code search capabilities through the [grep.app](https://grep.app) API. This server enables AI assistants to search through millions of GitHub repositories for specific code patterns, functions, and implementations.

## 🚀 Features

- **🔍 GitHub Code Search**: Search across millions of GitHub repositories using grep.app's powerful search index
- **🎯 Advanced Filtering**: Filter results by programming language, repository, and file path
- **📊 Smart Formatting**: Results include syntax highlighting, repository grouping, and summary statistics
- **⚡ High Performance**: Async implementation with proper error handling and rate limiting
- **🛠️ Multiple Transport Modes**: Supports both stdio and SSE (Server-Sent Events) transport
- **📝 Rich Results**: Returns file paths, line numbers, code snippets, and repository information

## 📋 Requirements

- **Python**: 3.10 or higher
- **Dependencies**:
  - `mcp` - Model Context Protocol framework
  - `starlette` - Web framework for SSE transport
  - `uvicorn` - ASGI server
  - `aiohttp` - Async HTTP client for API requests

## 🔧 Installation

### Using uv (Recommended)

```bash
# Install directly from PyPI
uv add grep-mcp

# Or install from source
git clone https://github.com/galperetz/grep-mcp.git
cd grep-mcp
uv sync
```

### Using pip

```bash
pip install grep-mcp
```

## 🎯 Usage

### As MCP Server (Recommended)

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "grep-mcp": {
      "command": "uvx",
      "args": ["grep-mcp"]
    }
  }
}
```

### Direct Execution

```bash
# Run with stdio transport (default)
python -m grep_mcp

# Run with SSE transport
python -m grep_mcp --transport sse --host 0.0.0.0 --port 8080
```

### Command Line Arguments

- `--transport`: Choose between `stdio` (default) or `sse`
- `--host`: Host to bind to for SSE mode (default: `0.0.0.0`)
- `--port`: Port to listen on for SSE mode (default: `8080`)

## 🔧 Available Tools

### `grep_query`

Search GitHub repositories for specific code patterns.

**Parameters:**

- `query` (required): The search query string
- `language` (optional): Programming language filter (e.g., "Python", "JavaScript")
- `repo` (optional): Repository filter in format "owner/repo" (e.g., "fastapi/fastapi")
- `path` (optional): Path filter for specific directories (e.g., "src/")

**Examples:**

```python
# Basic search
grep_query("async def main")

# Search Python files only
grep_query("FastAPI", language="Python")

# Search specific repository
grep_query("class Config", repo="fastapi/fastapi")

# Search in specific directory
grep_query("import", path="src/")

# Combined filters
grep_query("async def", language="Python", repo="fastapi/fastapi")
```

## 📊 Response Format

The tool returns structured JSON with:

````json
{
  "query": "your search query",
  "summary": {
    "total_results": 12345,
    "results_shown": 10,
    "repositories_found": 4,
    "top_languages": [
      { "language": "Python", "count": 8500 },
      { "language": "JavaScript", "count": 2000 }
    ],
    "top_repositories": [{ "repository": "owner/repo", "count": 150 }]
  },
  "results_by_repository": [
    {
      "repository": "owner/repo",
      "matches_count": 89,
      "files": [
        {
          "file_path": "src/main.py",
          "branch": "main",
          "total_matches": 5,
          "line_numbers": [10, 25, 30],
          "language": "python",
          "code_snippet": "```python\nasync def main():\n    app = FastAPI()\n    return app\n```"
        }
      ]
    }
  ]
}
````

## 🏗️ Architecture

- **FastMCP Framework**: Built on the FastMCP framework for easy MCP server development
- **Async HTTP Client**: Uses aiohttp for non-blocking API requests
- **Response Formatting**: Intelligent parsing and formatting of grep.app responses
- **Error Handling**: Comprehensive error handling for API failures, timeouts, and rate limits
- **Transport Flexibility**: Supports both stdio and web-based SSE transport modes

## 🛡️ Error Handling

The server handles various error conditions gracefully:

- **Rate Limiting**: Automatic detection and user-friendly error messages
- **Network Timeouts**: 30-second timeout with proper error reporting
- **API Failures**: Graceful handling of grep.app API issues
- **Invalid Parameters**: Comprehensive parameter validation with helpful error messages

## 🧪 Testing

Run the test suite:

```bash
# Using uv
uv run pytest

# Using pytest directly
pytest tests/
```

Test coverage includes:

- MCP server initialization
- Tool parameter validation
- Error handling scenarios
- Response formatting
- Platform compatibility

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes with tests
4. Run the test suite: `uv run pytest`
5. Format code: `uv run black . && uv run isort .`
6. Commit changes: `git commit -m 'Add amazing feature'`
7. Push to branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [grep.app](https://grep.app) for providing the excellent GitHub search API
- [MCP (Model Context Protocol)](https://github.com/modelcontextprotocol) for the protocol specification
- [FastMCP](https://github.com/jlowin/fastmcp) for the server framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/galperetz/grep-mcp/issues)
- **Repository**: [GitHub Repository](https://github.com/galperetz/grep-mcp)

---

**Made with ❤️ for the AI development community**
