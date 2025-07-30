# Domainr MCP Server

[![PyPI version](https://badge.fury.io/py/domainr-mcp-server.svg)](https://badge.fury.io/py/domainr-mcp-server)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A Model Context Protocol (MCP) server that provides domain search and availability checking functionality using the Domainr API. Perfect for AI assistants and domain research workflows.

## Features

- 🔍 **Domain Search** - Search for domains with intelligent suggestions
- ✅ **Availability Checking** - Check if domains are available for registration
- 🌐 **Registration URLs** - Get direct links to register domains
- 🎯 **Advanced Filtering** - Filter by registrar, keywords, and location
- ⚡ **Async Performance** - Built with modern async Python

## Installation

### Option 1: uvx (Recommended - No Installation Required)
```bash
uvx domainr-mcp-server
```

### Option 2: uv (Modern Package Manager)
```bash
uv tool install domainr-mcp-server
```

### Option 3: pip (Traditional)
```bash
pip install domainr-mcp-server
```

## Setup

### 1. Get a Domainr API Key
1. Sign up at [RapidAPI](https://rapidapi.com/domainr/api/domainr/)
2. Subscribe to the Domainr API
3. Copy your API key

### 2. Set Environment Variable
```bash
# Linux/macOS
export DOMAINR_API_KEY="your_api_key_here"

# Windows
set DOMAINR_API_KEY=your_api_key_here
```

### 3. Configure Your MCP Client

#### For Claude Desktop:
Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "domainr": {
      "command": "domainr-mcp-server",
      "env": {
        "DOMAINR_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

#### For uvx users:
```json
{
  "mcpServers": {
    "domainr": {
      "command": "uvx",
      "args": ["domainr-mcp-server"],
      "env": {
        "DOMAINR_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Available Tools

### 🔍 search_domains
Search for domain names with intelligent suggestions and filtering.

**Parameters:**
- `query` (required) - Search terms for domain names
- `location` (optional) - Country code for localized results (default: "us")  
- `registrar` (optional) - Filter by registrar (e.g., "dnsimple.com")
- `defaults` (optional) - Always include specific TLDs (e.g., "com,org")
- `keywords` (optional) - Seed results with keywords (e.g., "tech,startup")

**Example:**
```json
{
  "query": "awesome startup",
  "keywords": "tech,software",
  "defaults": "com,io"
}
```

### ✅ check_domain_status  
Check availability status of specific domains.

**Parameters:**
- `domains` (required) - Comma-separated list of domains to check

**Example:**
```json
{
  "domains": "example.com,example.io,example.org"
}
```

### 🌐 register_domain
Get registration URLs for domains.

**Parameters:**
- `domain` (required) - Domain name to register
- `registrar` (optional) - Preferred registrar

**Example:**
```json
{
  "domain": "myawesomesite.com",
  "registrar": "dnsimple.com"
}
```

## Usage Examples

### Basic Domain Search
```
User: "Find domains for a coffee shop"
Assistant: [searches domains with coffee-related keywords]
→ Returns: coffeeshop.com, mycafe.coffee, brew.cafe, etc.
```

### Availability Check
```
User: "Is example.com available?"
Assistant: [checks domain status]
→ Returns: example.com: active (not available)
```

### Complete Workflow
```
User: "I need a domain for my tech startup"
Assistant: 
1. [searches with tech keywords]
2. [checks availability of top options]  
3. [provides registration links for available domains]
```

## Development

### Local Development
```bash
git clone https://github.com/yourusername/domainr-mcp-server
cd domainr-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run locally
python -m domainr_mcp_server.server
```

### Testing
```bash
# Set your API key
export DOMAINR_API_KEY="your_test_key"

# Test the server
echo '{"method":"tools/list","params":{},"jsonrpc":"2.0","id":1}' | python -m domainr_mcp_server.server
```

## API Reference

This server integrates with the [Domainr API v2](https://domainr.com/api/docs/) endpoints:

- **Search**: `/v2/search` - Domain search with suggestions
- **Status**: `/v2/status` - Domain availability checking  
- **Register**: `/v2/register` - Registration URL generation

---

**Made with ❤️ for the MCP ecosystem**