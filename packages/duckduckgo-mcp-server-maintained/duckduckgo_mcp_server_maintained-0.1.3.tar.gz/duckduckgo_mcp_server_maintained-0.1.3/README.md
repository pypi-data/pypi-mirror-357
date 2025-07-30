# DuckDuckGo Search MCP Server (Maintained Fork)

> **This is a maintained fork** of the original [duckduckgo-mcp-server](https://github.com/nickclyde/duckduckgo-mcp-server) by [Nick Clyde](https://github.com/nickclyde). 
>
> **Why this fork?** This version includes updated dependencies, enhanced features, active maintenance, and improved release automation while maintaining full compatibility with the original.

[![smithery badge](https://smithery.ai/badge/@nickclyde/duckduckgo-mcp-server)](https://smithery.ai/server/@nickclyde/duckduckgo-mcp-server)

A Model Context Protocol (MCP) server that provides web search capabilities through DuckDuckGo, with additional features for content fetching and parsing.

<a href="https://glama.ai/mcp/servers/phcus2gcpn">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/phcus2gcpn/badge" alt="DuckDuckGo Server MCP server" />
</a>

## What's New in This Fork

- 🔄 **Active Maintenance**: Regular updates and dependency management
- 🚀 **Enhanced Release Process**: Automated publishing to PyPI, Docker, and GitHub Releases
- 🛡️ **Security Updates**: Latest dependency versions with security patches
- 📦 **Multi-Platform Support**: Docker images for AMD64 and ARM64
- 🔧 **Developer Experience**: Improved tooling and documentation

## Features

- **Web Search**: Search DuckDuckGo with advanced rate limiting and result formatting
- **Content Fetching**: Retrieve and parse webpage content with intelligent text extraction
- **Rate Limiting**: Built-in protection against rate limits for both search and content fetching
- **Error Handling**: Comprehensive error handling and logging
- **LLM-Friendly Output**: Results formatted specifically for large language model consumption

## Installation

### Installing via Smithery

To install DuckDuckGo Search Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@nickclyde/duckduckgo-mcp-server):

```bash
npx -y @smithery/cli install @nickclyde/duckduckgo-mcp-server --client claude
```

### Installing via `uv`

Install directly from PyPI using `uv`:

```bash
uv pip install duckduckgo-mcp-server-maintained
```

### Installing via `Docker`
```bash
docker build . -t duckduckgo-mcp-server:latest
```

## Usage

### Running with Claude Desktop

1. Download [Claude Desktop](https://claude.ai/download)
2. Create or edit your Claude Desktop configuration:
   - On macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - On Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Add the following configuration:

```json
{
    "mcpServers": {
        "ddg-search": {
            "command": "uvx",
            "args": ["duckduckgo-mcp-server-maintained"]
        }
    }
}
```

3. Restart Claude Desktop

### Development

For local development, you can use the MCP CLI:

```bash
# Run with the MCP Inspector
mcp dev server.py

# Install locally for testing with Claude Desktop
mcp install server.py
```
## Available Tools

### 1. Search Tool

```python
async def search(query: str, max_results: int = 10) -> str
```

Performs a web search on DuckDuckGo and returns formatted results.

**Parameters:**
- `query`: Search query string
- `max_results`: Maximum number of results to return (default: 10)

**Returns:**
Formatted string containing search results with titles, URLs, and snippets.

### 2. Content Fetching Tool

```python
async def fetch_content(url: str) -> str
```

Fetches and parses content from a webpage.

**Parameters:**
- `url`: The webpage URL to fetch content from

**Returns:**
Cleaned and formatted text content from the webpage.

## Features in Detail

### Rate Limiting

- Search: Limited to 30 requests per minute
- Content Fetching: Limited to 20 requests per minute
- Automatic queue management and wait times

### Result Processing

- Removes ads and irrelevant content
- Cleans up DuckDuckGo redirect URLs
- Formats results for optimal LLM consumption
- Truncates long content appropriately

### Error Handling

- Comprehensive error catching and reporting
- Detailed logging through MCP context
- Graceful degradation on rate limits or timeouts

## Publishing to GitHub Container Registry

To publish the Docker image to GitHub Container Registry, follow these steps:

1.  **Build the Docker image:**
    ```bash
    docker buildx build --platform linux/amd64 -t ghcr.io/scalabresegd/duckduckgo-mcp-server:latest .
    ```
    Replace `YOUR_USERNAME` with your GitHub username and `YOUR_REPOSITORY` with your GitHub repository name.

2.  **Log in to GitHub Container Registry:**
    ```bash
    echo $CR_PAT | docker login ghcr.io -u scalabreseGD --password-stdin
    ```
    Replace `CR_PAT` with your Personal Access Token (PAT) that has `write:packages` scope. Replace `USERNAME` with your GitHub username.

3.  **Push the Docker image:**
    ```bash
    docker push ghcr.io/scalabresegd/duckduckgo-mcp-server:latest
    ```
    Again, replace `YOUR_USERNAME` and `YOUR_REPOSITORY` accordingly.

## Original Project

This fork is based on the excellent work by [Nick Clyde](https://github.com/nickclyde). Please consider:

- ⭐ **Star the original repo**: [nickclyde/duckduckgo-mcp-server](https://github.com/nickclyde/duckduckgo-mcp-server)
- 🙏 **Give credit**: When using this fork, please mention both projects
- 🤝 **Contribute upstream**: Consider contributing improvements to the original project when possible

## Contributing

Issues and pull requests are welcome! Some areas for potential improvement:

- Additional search parameters (region, language, etc.)
- Enhanced content parsing options
- Caching layer for frequently accessed content
- Additional rate limiting strategies

When contributing, please:
1. Test your changes thoroughly
2. Update documentation as needed  
3. Consider if the improvement should also go to the original project

## License

This project is licensed under the MIT License, same as the original project.
