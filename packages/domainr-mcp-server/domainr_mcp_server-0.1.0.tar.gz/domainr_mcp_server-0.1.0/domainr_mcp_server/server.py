import asyncio
import os
from typing import Any, Dict, List, Optional
import httpx
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio


class DomainrClient:
    """Client for interacting with the Domainr API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DOMAINR_API_KEY")
        self.base_url = "https://domainr.p.rapidapi.com/v2"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "domainr.p.rapidapi.com",
        }

    async def search_domains(
        self,
        query: str,
        location: str = "us",
        registrar: Optional[str] = None,
        defaults: Optional[str] = None,
        keywords: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search for domains based on a query."""
        if not self.api_key:
            raise ValueError("Domainr API key is required")

        params = {"query": query, "location": location}
        if registrar:
            params["registrar"] = registrar
        if defaults:
            params["defaults"] = defaults
        if keywords:
            params["keywords"] = keywords

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/search", headers=self.headers, params=params
            )
            response.raise_for_status()
            return response.json()

    async def check_status(self, domains: str) -> Dict[str, Any]:
        """Check the status of one or more domains."""
        if not self.api_key:
            raise ValueError("Domainr API key is required")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/status",
                headers=self.headers,
                params={"domain": domains},
            )
            response.raise_for_status()
            return response.json()

    async def get_register_url(
        self, domain: str, registrar: Optional[str] = None
    ) -> str:
        """Get registration URL for a domain."""
        if not self.api_key:
            raise ValueError("Domainr API key is required")

        params = {"domain": domain}
        if registrar:
            params["registrar"] = registrar

        # Build the registration URL
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.base_url}/register?{query_string}"


# Initialize the MCP server
server = Server("domainr-server")

# Initialize Domainr client
domainr_client = DomainrClient()


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="search_domains",
            description="Search for domain names based on a query string",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query for domain names",
                    },
                    "location": {
                        "type": "string",
                        "description": "Location code for search context (default: 'us')",
                        "default": "us",
                    },
                    "registrar": {
                        "type": "string",
                        "description": "Filter results by zones supported by this registrar (e.g. 'dnsimple.com')",
                    },
                    "defaults": {
                        "type": "string",
                        "description": "Comma-separated list of default zones to include (e.g. 'club,org')",
                    },
                    "keywords": {
                        "type": "string",
                        "description": "Comma-separated keywords for seeding results (e.g. 'food,kitchen')",
                    },
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="check_domain_status",
            description="Check the availability status of one or more domains",
            inputSchema={
                "type": "object",
                "properties": {
                    "domains": {
                        "type": "string",
                        "description": "Comma-separated list of domain names to check",
                    }
                },
                "required": ["domains"],
            },
        ),
        types.Tool(
            name="register_domain",
            description="Get registration URL for a domain name",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Domain name to register (e.g. 'example.com')",
                    },
                    "registrar": {
                        "type": "string",
                        "description": "Preferred registrar URL (e.g. 'dnsimple.com') - optional",
                    },
                },
                "required": ["domain"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """Handle tool calls."""
    try:
        if name == "search_domains":
            query = arguments.get("query")
            location = arguments.get("location", "us")
            registrar = arguments.get("registrar")
            defaults = arguments.get("defaults")
            keywords = arguments.get("keywords")

            if not query:
                return [
                    types.TextContent(
                        type="text", text="Error: query parameter is required"
                    )
                ]

            result = await domainr_client.search_domains(
                query, location, registrar, defaults, keywords
            )

            # Format the results nicely
            if "results" in result:
                formatted_results = []
                for domain in result["results"]:
                    status = domain.get("availability", "unknown")
                    zone = domain.get("zone", "")
                    formatted_results.append(
                        f"• {domain['domain']} ({status}) - {zone}"
                    )

                response = f"Domain search results for '{query}':\n\n" + "\n".join(
                    formatted_results
                )

                if "related" in result and result["related"]:
                    response += (
                        f"\n\nRelated suggestions: {', '.join(result['related'])}"
                    )
            else:
                response = f"No results found for query: {query}"

            return [types.TextContent(type="text", text=response)]

        elif name == "check_domain_status":
            domains = arguments.get("domains")

            if not domains:
                return [
                    types.TextContent(
                        type="text", text="Error: domains parameter is required"
                    )
                ]

            result = await domainr_client.check_status(domains)

            # Format the status results
            if "status" in result:
                formatted_status = []
                for status_info in result["status"]:
                    domain = status_info.get("domain", "unknown")
                    summary = status_info.get("summary", "unknown")
                    formatted_status.append(f"• {domain}: {summary}")

                response = "Domain status check:\n\n" + "\n".join(formatted_status)
            else:
                response = f"Could not check status for domains: {domains}"

            return [types.TextContent(type="text", text=response)]

        elif name == "register_domain":
            domain = arguments.get("domain")
            registrar = arguments.get("registrar")

            if not domain:
                return [
                    types.TextContent(
                        type="text", text="Error: domain parameter is required"
                    )
                ]

            register_url = await domainr_client.get_register_url(domain, registrar)

            response = f"Registration URL for '{domain}':\n\n{register_url}"
            if registrar:
                response += f"\n\nThis URL will redirect you to {registrar} to complete the registration."
            else:
                response += "\n\nThis URL will redirect you to a suitable registrar to complete the registration."

            return [types.TextContent(type="text", text=response)]

        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

    except ValueError as e:
        return [
            types.TextContent(
                type="text",
                text=f"Configuration error: {str(e)}. Please set DOMAINR_API_KEY environment variable.",
            )
        ]
    except httpx.HTTPStatusError as e:
        return [
            types.TextContent(
                type="text",
                text=f"API error: {e.response.status_code} - {e.response.text}",
            )
        ]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def run_server():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="domainr-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def main():
    """Entry point for the MCP server."""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()