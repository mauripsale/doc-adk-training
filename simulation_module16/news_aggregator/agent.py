from google.adk import Agent, Workflow
from google.adk.workflow import JoinNode

# 1. Define Specialist Nodes
tech_researcher = Agent(
    name="tech_researcher",
    model="gemini-1.5-flash",
    instruction="Find 3 exciting headlines about AI and Robotics. Be concise.",
    output_key="tech_news"
)

market_researcher = Agent(
    name="market_researcher",
    model="gemini-1.5-flash",
    instruction="Find 3 key headlines about Stock Market trends. Be concise.",
    output_key="market_news"
)

summarizer = Agent(
    name="summarizer",
    model="gemini-1.5-flash",
    instruction="""
    You are a news editor. Create a brief newsletter using the data provided:
    TECH: {tech_news}
    MARKET: {market_news}
    
    Synthesize the information into a single, cohesive daily briefing.
    """
)

# 2. Define the Synchronization Point
syncer = JoinNode(name="news_sync")

# 3. Assemble the Workflow
# Parallel Fan-out + Sequential Fan-in
root_agent = Workflow(
    name="NewsSystem",
    edges=[
        # Both start at the same time and connect to the same JoinNode
        ("START", tech_researcher, syncer),
        ("START", market_researcher, syncer),
        
        # Once both are done, the syncer triggers the summarizer
        (syncer, summarizer)
    ]
)
