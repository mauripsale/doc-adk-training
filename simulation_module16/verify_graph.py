from news_aggregator.agent import root_agent
from google.adk.workflow import Workflow

def get_node_name(node):
    if isinstance(node, str):
        return node
    if hasattr(node, "name"):
        return node.name
    return str(node)

def test_graph_structure():
    assert isinstance(root_agent, Workflow)
    print("Graph name:", root_agent.name)
    print("Edges:")
    for edge in root_agent.edges:
        print(f"  {[get_node_name(n) for n in edge]}")

    # Check for START nodes
    start_edges = [e for e in root_agent.edges if get_node_name(e[0]) == "START"]
    assert len(start_edges) == 2, f"Expected 2 parallel start edges, found {len(start_edges)}"
    
    # Check for JoinNode synchronization
    syncer_edges = [e for e in root_agent.edges if len(e) == 3 and get_node_name(e[2]) == "news_sync"]
    assert len(syncer_edges) == 2, f"Expected 2 edges converging at news_sync, found {len(syncer_edges)}"
    
    # Check for sequential step after JoinNode
    post_syncer_edges = [e for e in root_agent.edges if get_node_name(e[0]) == "news_sync"]
    assert len(post_syncer_edges) == 1, f"Expected 1 edge after news_sync, found {len(post_syncer_edges)}"
    assert get_node_name(post_syncer_edges[0][1]) == "summarizer"

    print("Graph structure validation PASSED.")

if __name__ == "__main__":
    test_graph_structure()
