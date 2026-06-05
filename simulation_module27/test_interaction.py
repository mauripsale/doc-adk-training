import os
import sys

# Add the agent directory to sys.path to import it
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_agent"))

import agent

def test_simulation():
    print("Starting simulation test for Module 27...")
    
    # Verify agent properties
    assert agent.root_agent.name == 'filesystem_agent'
    assert agent.root_agent.model == 'gemini-3.5-flash'
    
    # Simulate list_directory tool
    print("\nSimulating tool discovery and execution...")
    mcp_toolset = agent.root_agent.tools[0]
    
    # In a real scenario, MCPToolset would discover tools from the server.
    # Here we simulate the logic of the filesystem server.
    test_files_dir = agent.TARGET_FOLDER_PATH
    files = os.listdir(test_files_dir)
    print(f"Files found in {test_files_dir}: {files}")
    assert "hello.txt" in files
    
    # Simulate reading the file
    file_path = os.path.join(test_files_dir, "hello.txt")
    with open(file_path, 'r') as f:
        content = f.read()
    print(f"Content of hello.txt: {content.strip()}")
    assert "Hello from the MCP world!" in content
    
    print("\nSimulation successful!")

if __name__ == "__main__":
    test_simulation()
