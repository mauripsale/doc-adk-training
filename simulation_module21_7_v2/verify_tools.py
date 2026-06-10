from agent import sales_agent, tech_agent

def check_tools():
    print(f"Sales Agent Tools: {[t.name for t in sales_agent.tools]}")
    print(f"Tech Agent Tools: {[t.name for t in tech_agent.tools]}")
    
    has_tech_tool = any("hand_off_to_tech_agent" in t.name for t in sales_agent.tools)
    has_sales_tool = any("hand_off_to_sales_agent" in t.name for t in tech_agent.tools)
    
    print(f"Sales has hand_off_to_tech_agent: {has_tech_tool}")
    print(f"Tech has hand_off_to_sales_agent: {has_sales_tool}")
    
    assert has_tech_tool, "Sales agent missing hand_off tool for tech_agent"
    assert has_sales_tool, "Tech agent missing hand_off tool for sales_agent"
    print("Hand-off tools correctly injected!")

if __name__ == "__main__":
    check_tools()
