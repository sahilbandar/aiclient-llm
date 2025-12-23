import contextlib
import asyncio
from typing import Dict, Any, List, Optional
from .client import MCPClient

class MCPServerManager:
    """
    Manages the lifecycle of MCP servers.
    """
    def __init__(self):
        self._clients: Dict[str, MCPClient] = {}
        self._exit_stack = contextlib.AsyncExitStack()

    def add_server(self, name: str, command: str, args: List[str], env: Optional[Dict[str, str]] = None):
        """
        Register a server config. Does not connect yet.
        """
        self._clients[name] = MCPClient(command, args, env)

    async def __aenter__(self):
        """
        Start all registered servers.
        """
        for name, client in self._clients.items():
            try:
                await self._exit_stack.enter_async_context(client)
            except Exception as e:
                # TODO: Log error, maybe skip this server or fail hard?
                print(f"Failed to start MCP server {name}: {e}")
                # For now, let's re-raise to be safe, or continue?
                # Re-raising is safer for consistency.
                raise e
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._exit_stack.aclose()


    async def get_client(self, name: str) -> MCPClient:
        return self._clients[name]
        
    async def list_global_tools(self) -> List[Dict[str, Any]]:
        """
        Aggregate tools from all connected servers.
        """
        all_tools = []
        for name, client in self._clients.items():
            try:
                tools = await client.list_tools()
                # Decorate with server name to avoid collisions? or just merge
                for t in tools:
                    # t is likely a Tool object (pydantic), convert to dict if needed or keep obj
                    # mcp Tool matches schema
                    all_tools.append(t)
            except Exception as e:
                # Log error
                pass
        return all_tools

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        # We need to know which server owns the tool.
        # This requires a mapping built during `list_global_tools`.
        # For now, simplistic iteration search.
        for client in self._clients.values():
            try:
                # This logic is inefficient; ideally we cache tool->server mapping
                tools = await client.list_tools() 
                for tool in tools:
                    if tool.name == name:
                        return await client.call_tool(name, arguments)
            except:
                continue
        raise ValueError(f"Tool {name} not found on any server")
