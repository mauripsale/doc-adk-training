import os

# Mocking Agent and MCPToolset classes for simulation in a restricted environment
class MockAgent:
    def __init__(self, model, name, instruction, tools):
        self.model = model
        self.name = name
        self.instruction = instruction
        self.tools = tools

class MockMCPToolset:
    def __init__(self, connection_params, tool_filter=None):
        self.connection_params = connection_params
        self.tool_filter = tool_filter
        self.name = "mcp_toolset"
    
    def __call__(self, *args, **kwargs):
        # This would be called when the agent executes the tool
        pass

class MockStdioConnectionParams:
    def __init__(self, server_params):
        self.server_params = server_params

class MockStdioServerParameters:
    def __init__(self, command, args):
        self.command = command
        self.args = args

# Overriding the imports with mocks
Agent = MockAgent
MCPToolset = MockMCPToolset
StdioConnectionParams = MockStdioConnectionParams
StdioServerParameters = MockStdioServerParameters

# -- Configuration --
TARGET_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_files/")

# -- Agent Definition --
root_agent = Agent(
    model='gemini-3.5-flash',
    name='filesystem_agent',
    instruction='You are a helpful assistant that can interact with a user\'s local file system. You can list files and read their content.',
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='npx',
                    args=[
                        "-y", 
                        "@modelcontextprotocol/server-filesystem", 
                        os.path.abspath(TARGET_FOLDER_PATH)
                    ],
                ),
            ),
            tool_filter=['list_directory', 'read_file']
        )
    ]
)

if __name__ == "__main__":
    print(f"Agent '{root_agent.name}' initialized successfully.")
    print(f"Target folder: {TARGET_FOLDER_PATH}")
    print(f"Tool Filter: {root_agent.tools[0].tool_filter}")
    print(f"MCP Command: {root_agent.tools[0].connection_params.server_params.command}")
    print(f"MCP Args: {root_agent.tools[0].connection_params.server_params.args}")
