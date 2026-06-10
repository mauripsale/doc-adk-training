import asyncio
from unittest.mock import AsyncMock, MagicMock
from agent import support_router_workflow, SentimentClassification, human_escalation, ai_support
from google.adk import Event

async def mock_generator(events):
    for e in events:
        yield e

async def test_routing():
    # Mock Context
    ctx = MagicMock()
    ctx.run_node = AsyncMock()

    # Test case 1: Angry customer
    node_input = "I HATE THIS SERVICE!"
    
    # We need to simulate run_node behavior. 
    # In reality, run_node calls the node's run method and collects the final output.
    # For our test, we just want to verify the logic inside support_router_workflow.run
    
    # However, support_router_workflow is a FunctionNode, and calling .run() 
    # will execute the wrapped function.
    
    # Let's try to run the underlying function directly if possible, 
    # but the decorator might have made it hard to reach.
    # In ADK, the original function is usually available via .func
    
    func = support_router_workflow.func
    
    ctx.run_node.side_effect = [
        SentimentClassification(sentiment="angry"), # First call: classifier
        "Mocked Human Response"                      # Second call: human_escalation
    ]
    
    result = await func(ctx, node_input)
    
    print(f"Input: {node_input}")
    print(f"Result: {result}")
    
    # Assertions
    assert ctx.run_node.call_count == 2
    ctx.run_node.assert_any_call(human_escalation, node_input)
    print("Test Case 1 (Angry) Passed!")

    # Reset mock for case 2
    ctx.run_node.reset_mock()
    
    # Test case 2: Neutral customer
    node_input = "How do I reset my password?"
    ctx.run_node.side_effect = [
        SentimentClassification(sentiment="neutral"), # First call: classifier
        "Mocked AI Response"                         # Second call: ai_support
    ]
    
    result = await func(ctx, node_input)
    
    print(f"Input: {node_input}")
    print(f"Result: {result}")
    
    # Assertions
    assert ctx.run_node.call_count == 2
    ctx.run_node.assert_any_call(ai_support, node_input)
    print("Test Case 2 (Neutral) Passed!")

if __name__ == "__main__":
    asyncio.run(test_routing())
