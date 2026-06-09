import asyncio
from google.adk.apps import App
from agent import root_agent

async def test_hitl():
    print("\n--- Testing HITL (Small Amount) ---")
    app = App(name="SecureFinanceTest", root_agent=root_agent)
    
    # 1. Ask for investment
    try:
        responses = await app.run("Invest $500 for me.")
        for resp in responses:
            print(f"Agent response: {resp}")
    except Exception as e:
        print(f"Error during run: {e}")

async def test_escalation():
    print("\n--- Testing Escalation (Large Amount) ---")
    app = App(name="SecureFinanceTest", root_agent=root_agent)
    
    # 1. Ask for large investment
    try:
        responses = await app.run("Invest $50,000 for me.")
        for resp in responses:
            print(f"Agent response: {resp}")
    except Exception as e:
        print(f"Error during run: {e}")

if __name__ == "__main__":
    asyncio.run(test_hitl())
    asyncio.run(test_escalation())
