"""ZMP MCP client manager."""

from __future__ import annotations

import asyncio
import logging

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import (
    MultiServerMCPClient,
    SSEConnection,
    StdioConnection,
    StreamableHttpConnection,
)

logger = logging.getLogger(__name__)


class ZmpMCPClientManager:
    """ZMP MCP client manager."""

    def __init__(self):
        """Initialize the ZMP MCP client manager."""
        self.connections: dict[
            str, StdioConnection | SSEConnection | StreamableHttpConnection
        ] = {}
        self.client: MultiServerMCPClient | None = None
        self.server_name_to_tools: dict[str, list[BaseTool]] = {}
        self.tools: list[BaseTool] = []

    @classmethod
    async def initialize(cls) -> ZmpMCPClientManager:
        """Initialize the ZMP MCP client manager."""
        return cls()

    async def add_mcp_servers(
        self,
        connections: dict[
            str, StdioConnection | SSEConnection | StreamableHttpConnection
        ],
    ) -> None:
        """Add MCP servers."""
        new_servers: list[str] = []
        if self.connections is not None and len(self.connections.items()) > 0:
            # If the connections are not empty, we need to add only the new servers
            new_servers = list(set(connections.keys()) - set(self.connections.keys()))
        else:
            new_servers = list(connections.keys())

        for server_name in new_servers:
            self.connections[server_name] = connections[server_name]

        self.client = MultiServerMCPClient(connections=self.connections)
        await self._initialize_tools()

    async def add_mcp_server(
        self,
        server_name: str,
        connection: StdioConnection | SSEConnection | StreamableHttpConnection,
    ) -> None:
        """Add a MCP server."""
        if server_name in self.connections:
            raise ValueError(f"MCP server {server_name} already exists")

        self.connections[server_name] = connection
        self.client = MultiServerMCPClient(connections=self.connections)
        await self._initialize_tools()

    async def get_server_name_to_tools(self) -> dict[str, list[BaseTool]]:
        """Get the server name to tools."""
        return self.server_name_to_tools

    async def _initialize_tools(self) -> None:
        """Get the server name to tools."""
        # Reset the tools and server name to tools
        self.tools = []
        self.server_name_to_tools = {}

        load_mcp_tool_tasks = []
        server_names = list(self.connections.keys())

        for server_name in server_names:
            load_mcp_tool_task = asyncio.create_task(
                self.client.get_tools(server_name=server_name)
            )
            load_mcp_tool_tasks.append(load_mcp_tool_task)

        tools_list = await asyncio.gather(*load_mcp_tool_tasks, return_exceptions=True)
        for server_name, tools in zip(server_names, tools_list):
            if isinstance(tools, Exception):
                logger.error(f"Failed to get tools for {server_name}: {tools}")
                if server_name in self.connections:
                    del self.connections[server_name]
                if server_name in self.client.connections:
                    del self.client.connections[server_name]
                continue
            else:
                self.tools.extend(tools)
                self.server_name_to_tools[server_name] = tools

    async def get_tools(self) -> list[BaseTool]:
        """Get all tools or a specific server's tools."""
        return self.tools

    async def get_mcp_server(
        self, server_name: str
    ) -> StdioConnection | SSEConnection | StreamableHttpConnection:
        """Get a MCP server."""
        if server_name not in self.connections:
            raise ValueError(f"MCP server {server_name} not found")

        return self.connections[server_name]

    async def remove_mcp_server(self, server_name: str):
        """Remove a MCP server."""
        if server_name not in self.connections:
            raise ValueError(f"MCP server {server_name} not found")

        del self.connections[server_name]
        logger.info(f"Removed MCP server: {server_name} from connections")

        self.client = MultiServerMCPClient(connections=self.connections)
        await self._initialize_tools()

    async def teardown(self):
        """Teardown the ZMP MCP client manager."""
        self.tools = []
        self.server_name_to_tools = {}
        self.connections = {}
        self.client = None
