import os
import sys
from agent import root_agent, classifier, usd_analyst, eur_analyst, gbp_analyst
from google.adk import Workflow

def test_workflow_structure():
    print("Validating Workflow Structure...")
    assert root_agent.name == "MarketSystem"
    
    # Check edges
    # The edges are stored internally. In ADK 2.x, they might be in a specific format.
    # We can at least check if it was initialized without error.
    print("Workflow initialized successfully.")
    
    # Verify participants
    # In some versions of ADK, Workflow might have participants or nodes
    # Let's check what's available in root_agent
    print(f"Edges: {root_agent.edges}")
    
    # Verify START edge
    found_start = False
    for start, end in root_agent.edges:
        if start == "START":
            assert end == classifier
            found_start = True
    assert found_start, "START edge not found or incorrect"
    
    # Verify router edge
    found_router = False
    for start, end in root_agent.edges:
        if start == classifier:
            assert isinstance(end, dict)
            assert end["USD"] == usd_analyst
            assert end["EUR"] == eur_analyst
            assert end["GBP"] == gbp_analyst
            found_router = True
    assert found_router, "Router edge not found or incorrect"

    print("Workflow structure is CORRECT.")

if __name__ == "__main__":
    try:
        test_workflow_structure()
    except Exception as e:
        print(f"Validation FAILED: {e}")
        sys.exit(1)
