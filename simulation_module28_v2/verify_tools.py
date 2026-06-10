import asyncio
import os
from agent import root_agent

async def verify_agent():
    print("Initializing agent and fetching MCP tools...")
    # The MCP connection is established when the toolset is first used or initialized
    # For ADK 2.0, we can check the tools available to the root_agent
    
    # Trigger tool discovery if necessary
    # In some ADK versions, tools might be lazily loaded.
    
    print(f"Agent Name: {root_agent.name}")
    print("Available Tools:")
    for tool in root_agent.tools:
        # Check if it's an MCPToolset
        from google.adk.tools.mcp_tool import MCPToolset
        if isinstance(tool, MCPToolset):
            # MCPToolset might need an active session to show sub-tools
            # But let's see what it reports
            print(f" - Toolset: {type(tool).__name__}")
            # We can't easily list sub-tools without a run context in some versions
            # but we can try to inspect internal state if needed.
    
    print("\nVerification script finished.")

if __name__ == "__main__":
    asyncio.run(verify_agent())
