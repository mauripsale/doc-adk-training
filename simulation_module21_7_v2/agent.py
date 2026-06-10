from google.adk import Agent

# 1. Define the Tech Agent
tech_agent = Agent(
    name="tech_agent",
    model="gemini-3.5-flash",
    description="Expert in hardware specs and troubleshooting.",
    instruction="""
    You are a technical support expert. You answer questions about hardware specs and troubleshooting.
    If the user asks about pricing, buying, or discounts, hand off to the sales_agent.
    """
)

# 2. Define the Sales Agent
sales_agent = Agent(
    name="sales_agent",
    model="gemini-3.5-flash",
    description="Expert in pricing, bundles, and purchase orders.",
    instruction="""
    You are a sales representative. You help users with pricing and buying products.
    If the user asks about hardware specifications, compatibility, or technical issues, hand off to the tech_agent.
    """,
    # TODO: Add the collaborators list to enable hand-offs
    collaborators=[tech_agent] 
)

# 3. Enable bi-directional hand-offs
# TODO: Since sales_agent was just defined, you can now link tech_agent to it.
tech_agent.collaborators = [sales_agent]

# 4. Define the Root Agent
root_agent = sales_agent
