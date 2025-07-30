"""Tests for MCP server functionality."""

import pytest
from unittest.mock import patch, AsyncMock
import mcp.types as types
from domainr_mcp_server.server import handle_list_tools, handle_call_tool


class TestMCPServer:
    """Test cases for MCP server handlers."""

    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test that all tools are properly listed."""
        tools = await handle_list_tools()
        
        assert len(tools) == 3
        
        tool_names = [tool.name for tool in tools]
        assert "search_domains" in tool_names
        assert "check_domain_status" in tool_names
        assert "register_domain" in tool_names
        
        # Check search_domains tool structure
        search_tool = next(tool for tool in tools if tool.name == "search_domains")
        assert search_tool.description == "Search for domain names based on a query string"
        assert "query" in search_tool.inputSchema["properties"]
        assert "query" in search_tool.inputSchema["required"]
        assert "location" in search_tool.inputSchema["properties"]
        assert "registrar" in search_tool.inputSchema["properties"]
        assert "defaults" in search_tool.inputSchema["properties"] 
        assert "keywords" in search_tool.inputSchema["properties"]

    @pytest.mark.asyncio
    async def test_search_domains_success(self):
        """Test successful domain search through MCP."""
        mock_result = {
            "results": [
                {"domain": "example.com", "zone": "com", "availability": "active"},
                {"domain": "example.org", "zone": "org", "availability": "inactive"}
            ],
            "related": ["sample.com", "demo.com"]
        }

        with patch("domainr_mcp_server.server.domainr_client.search_domains") as mock_search:
            mock_search.return_value = mock_result
            
            result = await handle_call_tool("search_domains", {"query": "example"})
            
            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            assert "Domain search results for 'example'" in result[0].text
            assert "example.com (active) - com" in result[0].text
            assert "example.org (inactive) - org" in result[0].text
            assert "Related suggestions: sample.com, demo.com" in result[0].text
            
            mock_search.assert_called_once_with("example", "us", None, None, None)

    @pytest.mark.asyncio
    async def test_search_domains_with_params(self):
        """Test domain search with all parameters."""
        mock_result = {"results": []}

        with patch("domainr_mcp_server.server.domainr_client.search_domains") as mock_search:
            mock_search.return_value = mock_result
            
            args = {
                "query": "test",
                "location": "uk",
                "registrar": "dnsimple.com", 
                "defaults": "com,org",
                "keywords": "tech,startup"
            }
            
            await handle_call_tool("search_domains", args)
            
            mock_search.assert_called_once_with(
                "test", "uk", "dnsimple.com", "com,org", "tech,startup"
            )

    @pytest.mark.asyncio
    async def test_search_domains_no_query(self):
        """Test domain search without required query parameter."""
        result = await handle_call_tool("search_domains", {})
        
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "Error: query parameter is required" in result[0].text

    @pytest.mark.asyncio
    async def test_search_domains_no_results(self):
        """Test domain search with no results."""
        mock_result = {}

        with patch("domainr_mcp_server.server.domainr_client.search_domains") as mock_search:
            mock_search.return_value = mock_result
            
            result = await handle_call_tool("search_domains", {"query": "nonexistent"})
            
            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            assert "No results found for query: nonexistent" in result[0].text

    @pytest.mark.asyncio
    async def test_check_domain_status_success(self):
        """Test successful domain status check through MCP."""
        mock_result = {
            "status": [
                {"domain": "example.com", "summary": "active"},
                {"domain": "example.org", "summary": "inactive"}
            ]
        }

        with patch("domainr_mcp_server.server.domainr_client.check_status") as mock_check:
            mock_check.return_value = mock_result
            
            result = await handle_call_tool("check_domain_status", {
                "domains": "example.com,example.org"
            })
            
            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            assert "Domain status check:" in result[0].text
            assert "example.com: active" in result[0].text
            assert "example.org: inactive" in result[0].text
            
            mock_check.assert_called_once_with("example.com,example.org")

    @pytest.mark.asyncio
    async def test_check_domain_status_no_domains(self):
        """Test domain status check without required domains parameter."""
        result = await handle_call_tool("check_domain_status", {})
        
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "Error: domains parameter is required" in result[0].text

    @pytest.mark.asyncio
    async def test_check_domain_status_no_results(self):
        """Test domain status check with no results."""
        mock_result = {}

        with patch("domainr_mcp_server.server.domainr_client.check_status") as mock_check:
            mock_check.return_value = mock_result
            
            result = await handle_call_tool("check_domain_status", {
                "domains": "example.com"
            })
            
            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            assert "Could not check status for domains: example.com" in result[0].text

    @pytest.mark.asyncio
    async def test_register_domain_success(self):
        """Test successful domain registration URL generation."""
        expected_url = "https://domainr.p.rapidapi.com/v2/register?domain=example.com"

        with patch("domainr_mcp_server.server.domainr_client.get_register_url") as mock_register:
            mock_register.return_value = expected_url
            
            result = await handle_call_tool("register_domain", {"domain": "example.com"})
            
            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            assert "Registration URL for 'example.com':" in result[0].text
            assert expected_url in result[0].text
            assert "suitable registrar" in result[0].text
            
            mock_register.assert_called_once_with("example.com", None)

    @pytest.mark.asyncio
    async def test_register_domain_with_registrar(self):
        """Test domain registration URL with specific registrar."""
        expected_url = "https://domainr.p.rapidapi.com/v2/register?domain=example.com&registrar=dnsimple.com"

        with patch("domainr_mcp_server.server.domainr_client.get_register_url") as mock_register:
            mock_register.return_value = expected_url
            
            result = await handle_call_tool("register_domain", {
                "domain": "example.com",
                "registrar": "dnsimple.com"
            })
            
            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            assert expected_url in result[0].text
            assert "redirect you to dnsimple.com" in result[0].text
            
            mock_register.assert_called_once_with("example.com", "dnsimple.com")

    @pytest.mark.asyncio
    async def test_register_domain_no_domain(self):
        """Test domain registration without required domain parameter."""
        result = await handle_call_tool("register_domain", {})
        
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "Error: domain parameter is required" in result[0].text

    @pytest.mark.asyncio
    async def test_unknown_tool(self):
        """Test calling unknown tool."""
        result = await handle_call_tool("unknown_tool", {})
        
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "Unknown tool: unknown_tool" in result[0].text

    @pytest.mark.asyncio
    async def test_value_error_handling(self):
        """Test handling of ValueError (missing API key)."""
        with patch("domainr_mcp_server.server.domainr_client.search_domains") as mock_search:
            mock_search.side_effect = ValueError("Domainr API key is required")
            
            result = await handle_call_tool("search_domains", {"query": "test"})
            
            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            assert "Configuration error" in result[0].text
            assert "DOMAINR_API_KEY environment variable" in result[0].text

    @pytest.mark.asyncio
    async def test_http_error_handling(self):
        """Test handling of HTTP errors."""
        import httpx
        
        with patch("domainr_mcp_server.server.domainr_client.search_domains") as mock_search:
            mock_response = AsyncMock()
            mock_response.status_code = 404
            mock_response.text = "Not Found"
            
            mock_search.side_effect = httpx.HTTPStatusError(
                "404 Not Found", request=None, response=mock_response
            )
            
            result = await handle_call_tool("search_domains", {"query": "test"})
            
            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            assert "API error: 404 - Not Found" in result[0].text

    @pytest.mark.asyncio
    async def test_generic_error_handling(self):
        """Test handling of generic exceptions."""
        with patch("domainr_mcp_server.server.domainr_client.search_domains") as mock_search:
            mock_search.side_effect = Exception("Something went wrong")
            
            result = await handle_call_tool("search_domains", {"query": "test"})
            
            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            assert "Error: Something went wrong" in result[0].text