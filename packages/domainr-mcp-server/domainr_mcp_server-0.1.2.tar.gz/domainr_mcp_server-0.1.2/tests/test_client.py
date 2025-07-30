"""Tests for DomainrClient."""

import pytest
import httpx
from unittest.mock import patch
from domainr_mcp_server.server import DomainrClient


class TestDomainrClient:
    """Test cases for DomainrClient class."""

    def test_init_with_api_key(self):
        """Test client initialization with API key."""
        client = DomainrClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.base_url == "https://domainr.p.rapidapi.com/v2"
        assert client.headers["X-RapidAPI-Key"] == "test_key"
        assert client.headers["X-RapidAPI-Host"] == "domainr.p.rapidapi.com"

    @patch.dict("os.environ", {"DOMAINR_API_KEY": "env_key"})
    def test_init_with_env_var(self):
        """Test client initialization with environment variable."""
        client = DomainrClient()
        assert client.api_key == "env_key"

    def test_init_without_api_key(self):
        """Test client initialization without API key."""
        with patch.dict("os.environ", {}, clear=True):
            client = DomainrClient()
            assert client.api_key is None

    @pytest.mark.asyncio
    async def test_search_domains_success(self, httpx_mock):
        """Test successful domain search."""
        client = DomainrClient(api_key="test_key")

        mock_response = {
            "results": [
                {"domain": "example.com", "zone": "com", "availability": "active"},
                {"domain": "example.org", "zone": "org", "availability": "inactive"},
            ],
            "related": ["sample.com", "demo.com"],
        }

        httpx_mock.add_response(
            url="https://domainr.p.rapidapi.com/v2/search?query=example&location=us",
            json=mock_response,
        )

        result = await client.search_domains("example")
        assert result == mock_response

    @pytest.mark.asyncio
    async def test_search_domains_with_all_params(self, httpx_mock):
        """Test domain search with all optional parameters."""
        client = DomainrClient(api_key="test_key")

        httpx_mock.add_response(
            url="https://domainr.p.rapidapi.com/v2/search?query=test&location=uk&registrar=dnsimple.com&defaults=com%2Corg&keywords=tech%2Cstartup",
            json={"results": []},
        )

        result = await client.search_domains(
            query="test",
            location="uk",
            registrar="dnsimple.com",
            defaults="com,org",
            keywords="tech,startup",
        )

        assert result == {"results": []}

    @pytest.mark.asyncio
    async def test_search_domains_no_api_key(self):
        """Test domain search without API key raises error."""
        client = DomainrClient()

        with pytest.raises(ValueError, match="Domainr API key is required"):
            await client.search_domains("example")

    @pytest.mark.asyncio
    async def test_search_domains_http_error(self, httpx_mock):
        """Test domain search with HTTP error."""
        client = DomainrClient(api_key="test_key")

        httpx_mock.add_response(
            url="https://domainr.p.rapidapi.com/v2/search?query=example&location=us",
            status_code=404,
            text="Not Found",
        )

        with pytest.raises(httpx.HTTPStatusError):
            await client.search_domains("example")

    @pytest.mark.asyncio
    async def test_check_status_success(self, httpx_mock):
        """Test successful domain status check."""
        client = DomainrClient(api_key="test_key")

        mock_response = {
            "status": [
                {
                    "domain": "example.com",
                    "zone": "com",
                    "status": "active",
                    "summary": "active",
                }
            ]
        }

        httpx_mock.add_response(
            url="https://domainr.p.rapidapi.com/v2/status?domain=example.com%2Cexample.org",
            json=mock_response,
        )

        result = await client.check_status("example.com,example.org")
        assert result == mock_response

    @pytest.mark.asyncio
    async def test_check_status_no_api_key(self):
        """Test status check without API key raises error."""
        client = DomainrClient()

        with pytest.raises(ValueError, match="Domainr API key is required"):
            await client.check_status("example.com")

    @pytest.mark.asyncio
    async def test_check_status_http_error(self, httpx_mock):
        """Test status check with HTTP error."""
        client = DomainrClient(api_key="test_key")

        httpx_mock.add_response(
            url="https://domainr.p.rapidapi.com/v2/status?domain=example.com",
            status_code=500,
            text="Internal Server Error",
        )

        with pytest.raises(httpx.HTTPStatusError):
            await client.check_status("example.com")

    @pytest.mark.asyncio
    async def test_get_register_url_basic(self):
        """Test basic registration URL generation."""
        client = DomainrClient(api_key="test_key")

        url = await client.get_register_url("example.com")

        assert url == "https://domainr.p.rapidapi.com/v2/register?domain=example.com"

    @pytest.mark.asyncio
    async def test_get_register_url_with_registrar(self):
        """Test registration URL generation with registrar."""
        client = DomainrClient(api_key="test_key")

        url = await client.get_register_url("example.com", "dnsimple.com")

        expected = "https://domainr.p.rapidapi.com/v2/register?domain=example.com&registrar=dnsimple.com"
        assert url == expected

    @pytest.mark.asyncio
    async def test_get_register_url_no_api_key(self):
        """Test registration URL generation without API key raises error."""
        client = DomainrClient()

        with pytest.raises(ValueError, match="Domainr API key is required"):
            await client.get_register_url("example.com")
