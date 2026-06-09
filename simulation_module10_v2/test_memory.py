import asyncio
from google.adk import App
from agent import root_agent

async def main():
    # Initialize the App with the root agent
    app = App(root_agent=root_agent)
    
    print("--- Starting Session ---")
    
    # First turn: Introduce user
    print("User: Hi, I'm Mario.")
    response1 = await app.run("Hi, I'm Mario.")
    print(f"Agent: {response1.text}")
    
    # Verify if store_name was called and state updated
    # In ADK 2.0, we can check the state from the context if needed, 
    # but here we rely on the next turn to verify persistence.
    
    # Second turn: Ask for name
    print("\nUser: What is my name?")
    response2 = await app.run("What is my name?")
    print(f"Agent: {response2.text}")
    
    if "Mario" in response2.text:
        print("\nSUCCESS: Agent remembered the name across turns.")
    else:
        print("\nFAILURE: Agent did not remember the name.")

if __name__ == "__main__":
    asyncio.run(main())
