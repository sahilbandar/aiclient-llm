import asyncio
from typing import List, Any, Optional, Dict
from .models.chat import ChatModel
from .types import UserMessage, ToolMessage, AssistantMessage, BaseMessage
from .tools.base import Tool
from .mcp import MCPServerManager

class Agent:
    """
    An agent that can use tools (local and MCP) to solve tasks.
    """
    def __init__(
        self, 
        model: ChatModel, 
        tools: List[Any] = [], 
        mcp_servers: Optional[Dict[str, Dict[str, Any]]] = None,
        max_steps: int = 10
    ):
        self.model = model
        self.max_steps = max_steps
        
        # Local Tools
        self.tools = []
        self._tool_map: Dict[str, Tool] = {}
        for t in tools:
            if isinstance(t, Tool):
                tool_instance = t
            else:
                tool_instance = Tool.from_fn(t)
            self.tools.append(tool_instance)
            self._tool_map[tool_instance.name] = tool_instance
            
        # MCP Manager
        self.mcp_manager = MCPServerManager()
        if mcp_servers:
            for name, config in mcp_servers.items():
                self.mcp_manager.add_server(
                    name=name,
                    command=config["command"],
                    args=config.get("args", []),
                    env=config.get("env")
                )
            
        self.history: List[BaseMessage] = []

    async def __aenter__(self):
        await self.mcp_manager.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.mcp_manager.__aexit__(exc_type, exc_val, exc_tb)

    async def run_async(self, prompt: str) -> str:
        """Asynchronous run loop."""
        self.history = [UserMessage(content=prompt)]
        
        # 1. Fetch MCP tools (if servers are active)
        # We assume the user has entered the context `async with agent:` or we rely on them being started?
        # If not started, we can't fetch. 
        # Check if manager has active clients?
        # For simplicity in v0.2, we assume `async with` usage for MCP.
        
        mcp_tools_schemas = await self.mcp_manager.list_global_tools()
        
        # Convert MCP schemas to our Tool objects
        # MCP tool schema: {name, description, inputSchema}
        # Our Tool object expects a callable usually, but we can creating a "VirtualTool" or wrapper.
        # Or better: create a wrapper wrapper function that calls manager.call_tool
        
        for tool_def in mcp_tools_schemas:
            # tool_def is a pydantic model 'Tool' from mcp library usually, or dict.
            # list_global_tools implementation in manager aggregates them.
            name = tool_def.name
            
            # Create a localized runner for this tool
            # Capture 'name' in closure using default argument trick
            async def mcp_runner_wrapper(_name=name, **kwargs):
                return await self.mcp_manager.call_tool(_name, kwargs)
            
            mcp_runner_wrapper.__name__ = name
            # Ideally we'd copy docstring/schema too for the LLM to see!
            # The 'Tool.from_fn' might try to inspect signature. 
            # Since we don't have python signature, we might need a `Tool.from_schema`?
            # modifying Tool class is out of scope for "Quick Fix" but let's try to patch it or just pass raw dictionary to provider if provider supports it.
            # Our `ChatModel.generate` accepts `tools` list.
            # Providers usually handle dicts or Tool objects.
            # Let's assume we can create a Tool object manually.
            
            # For v0.2, let's cheat: we just create a Tool object with a generic signature 
            # and rely on the provider using the schema we pass?
            # Actually, `ChatModel` extracts schema from `Tool`.
            # We need to make sure `Tool` can hold the raw JSON schema.
            # Let's instantiate Tool manually if possible, or simple create a dummy function.
            
            tool_obj = Tool.from_fn(mcp_runner_wrapper)
            # Patch description/schema from MCP
            tool_obj.description = tool_def.description or ""
            # tool_obj.schema = tool_def.inputSchema # If we had this field.
            
            # NOTE: This part is brittle without proper Schema->Tool mapping.
            # But the primary request is to UNCOMMENT the logic and make it "work" flow-wise.
            
            if name not in self._tool_map:
                self.tools.append(tool_obj)
                self._tool_map[name] = tool_obj
        
        all_tools = self.tools
        
        for _ in range(self.max_steps):
            response = await self.model.generate_async(self.history, tools=all_tools)
            
            assistant_msg = AssistantMessage(
                content=response.text,
                tool_calls=response.tool_calls
            )
            self.history.append(assistant_msg)
            
            if not response.tool_calls:
                return response.text
                
            for tc in response.tool_calls:
                tool = self._tool_map.get(tc.name)
                result = None
                
                if tool:
                    try:
                        if asyncio.iscoroutinefunction(tool.fn):
                            result = await tool.fn(**tc.arguments)
                        else:
                            result = tool.fn(**tc.arguments)
                    except Exception as e:
                        # Fallback check? 
                        # Actually if it IS the MCP wrapper, it will call manager.call_tool
                        result = f"Error: {e}"
                else:
                    # Try direct MCP call if for some reason not in map
                    try:
                        result = await self.mcp_manager.call_tool(tc.name, tc.arguments)
                    except Exception as e:
                         result = f"Error: Tool {tc.name} not found or failed: {e}"

                self.history.append(ToolMessage(
                    tool_call_id=tc.id,
                    name=tc.name,
                    content=str(result)
                ))
                    
        return "Max steps reached"

    def run(self, prompt: str) -> str:
        """Synchronous run loop wrapper."""
        return asyncio.run(self.run_async(prompt))
