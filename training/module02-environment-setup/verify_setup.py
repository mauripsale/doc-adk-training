import asyncio
from google.adk.agents import LlmAgent

async def main():
    try:
        print("✅ Google ADK is installed correctly.")
        print("Attempting to connect to the LLM service...")

        # LlmAgent requires a name, model, and instruction.
        agent = LlmAgent(name="verify_agent", model="gemini-3.5-flash", instruction="You are a helpful assistant.")

        response = await agent.invoke("hello")

        if response:
            print("✅ Authentication successful: Connected to the LLM service.")
            print(f"LLM response: {response}")
        else:
            print("❌ Authentication failed: Could not connect to the LLM service.")

    except ImportError:
        print("❌ Installation error: The 'google-adk' package could not be found.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
