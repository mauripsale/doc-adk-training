import asyncio
from agent import root_agent

async def simulate_conversation():
    # 1. Ask about price (should be handled by sales_agent)
    print("--- Turn 1: Price Query ---")
    response1 = await root_agent.run("How much does the Pro model cost?")
    print(f"Response: {response1.text}")
    print(f"Active Agent: {root_agent._workflow_context.active_agent.name if hasattr(root_agent, '_workflow_context') else 'N/A'}")

    # 2. Ask about technical specs (should trigger hand-off to tech_agent)
    print("\n--- Turn 2: Technical Query ---")
    response2 = await root_agent.run("Does it support 5G?")
    print(f"Response: {response2.text}")
    # In ADK 2.0, the root_agent's state should reflect the current collaborator
    
if __name__ == "__main__":
    # Mocking the environment for testing
    # We need to ensure API keys are available if we actually run it, 
    # but for simulation we can check the structural integrity and logic.
    pass
