from contextlib import asynccontextmanager
from typing import Dict, Optional
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
import os
from dotenv import load_dotenv
from typing import List
import json

load_dotenv(override=True)


class PayLinkClient:
    """
    Client for interacting with the PayLink MCP server over streamable HTTP.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        tracing: Optional[str] = None,
        project: Optional[str] = None,
        payment_provider: Optional[List[str]] = None,
    ):
        self.server_url = "http://localhost:8050/mcp"

        # Initialize headers
        self.headers = {}

        # Use provided value or fall back to .env
        self.api_key = api_key or os.getenv("PAYLINK_API_KEY")
        self.tracing = tracing or os.getenv("PAYLINK_TRACING")
        self.project = project or os.getenv("PAYLINK_PROJECT")
        self.payment_provider = payment_provider or json.loads(
            os.getenv("PAYMENT_PROVIDER", "[]")
        )

        # Add specific PayLink headers if provided
        if self.api_key:
            self.headers["PAYLINK_API_KEY"] = self.api_key
        if self.tracing and self.tracing.lower() == "enabled":
            self.headers["PAYLINK_TRACING"] = "enabled"
        if self.project:
            self.headers["PAYLINK_PROJECT"] = self.project
        if self.payment_provider:
            self.headers["PAYMENT_PROVIDER"] = json.dumps(self.payment_provider)

        # M-Pesa specific headers
        self.mpesa_settings = {}
        if "mpesa" in self.payment_provider:
            self.mpesa_settings = {
                "MPESA_BUSINESS_SHORTCODE": os.getenv("MPESA_BUSINESS_SHORTCODE"),
                "MPESA_CONSUMER_SECRET": os.getenv("MPESA_CONSUMER_SECRET"),
                "MPESA_CONSUMER_KEY": os.getenv("MPESA_CONSUMER_KEY"),
                "MPESA_CALLBACK_URL": os.getenv("MPESA_CALLBACK_URL"),
                "MPESA_PASSKEY": os.getenv("MPESA_PASSKEY"),
                "MPESA_BASE_URL": os.getenv("MPESA_BASE_URL"),
            }

            # Validate required M-Pesa settings
            required = [
                "MPESA_BUSINESS_SHORTCODE",
                "MPESA_CONSUMER_SECRET",
                "MPESA_CONSUMER_KEY",
                "MPESA_CALLBACK_URL",
                "MPESA_PASSKEY",
                "MPESA_BASE_URL",
            ]
            missing = [k for k in required if not self.mpesa_settings.get(k)]
            if missing:
                raise ValueError(f"Missing M-Pesa settings: {', '.join(missing)}")

            # Add M-Pesa settings directly to headers
            for key, value in self.mpesa_settings.items():
                self.headers[key] = value
                
        self._validate_headers()

    def _validate_headers(self):
        """
        Validate that all required headers are present and not empty
        """
        required_headers = ["PAYLINK_API_KEY", "PAYLINK_PROJECT", "PAYLINK_TRACING", "PAYMENT_PROVIDER"]

        for key in required_headers:
            if key not in self.headers or not self.headers[key]:
                raise ValueError(f"Missing required header: {key}")

    @asynccontextmanager
    async def connect(self):
        """
        Async context manager to connect to the MCP server using streamable HTTP.
        """
        async with streamablehttp_client(self.server_url, headers=self.headers) as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                yield session

    async def list_tools(self):
        """
        List all available tools from the server.
        Returns:
            list: A list of ToolDescription objects.
        """
        async with self.connect() as session:
            tools_result = await session.list_tools()
            return tools_result.tools

    async def call_tool(self, tool_name: str, tool_args: dict):
        """Call a tool by name with arguments and return the results

        Args:
            tool_name (str): Name of the tool to invoke
            tool_args (dict): Input arguments for the tool

        Returns:
            Dict: result from the tool execution
        """

        async with self.connect() as session:
            # Step 1: List available tools to confirm it exists
            tools_result = await session.list_tools()
            tool = next((t for t in tools_result.tools if t.name == tool_name), None)

            if not tool:
                raise ValueError(f"Tool '{tool_name}' not found in server's tool list.")

            result = await session.call_tool(tool_name, tool_args)

            return result