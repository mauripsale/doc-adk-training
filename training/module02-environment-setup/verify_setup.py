import asyncio
import sys
import importlib.metadata
from google.adk.agents import LlmAgent

async def main():
    try:
        # 1. Check ADK Version
        version = importlib.metadata.version("google-adk")
        print(f"📦 Google ADK version: {version}")
        
        major_version = int(version.split('.')[0])
        if major_version < 2:
            print(f"❌ Error: This course requires ADK version 2.0 or higher. You have {version}.")
            print("Please run: uv pip install -U 'google-adk>=2.1.0'")
            sys.exit(1)
        
        print("✅ ADK 2.0+ is installed correctly.")

        # 2. Check Python Version
        if sys.version_info < (3, 10):
            print(f"❌ Error: Python 3.10+ is required. You are using {sys.version.split()[0]}.")
            sys.exit(1)
        print("✅ Python 3.10+ requirement met.")

        # 3. Basic Functionality Check
        print("Attempting to connect to the LLM service...")
        agent = LlmAgent(
            name="verify_agent", 
            model="gemini-3.5-flash", 
            instruction="You are a helpful assistant. Reply with 'OK' if you can hear me."
        )

        # Basic invoke still works for simple verification
        response = await agent.invoke("Verify connection")

        if response:
            print("✅ Authentication successful: Connected to the LLM service.")
            print(f"LLM verification response: {response}")
        else:
            print("❌ Authentication failed: Could not connect to the LLM service.")

    except importlib.metadata.PackageNotFoundError:
        print("❌ Installation error: The 'google-adk' package could not be found.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
