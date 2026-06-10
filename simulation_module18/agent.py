from __future__ import annotations
from pydantic import BaseModel
from google.adk import Agent, Workflow, Context, Event
from google.adk.workflow import node
from typing import AsyncGenerator, Literal

# ===== Specialist Agent Nodes =====

ai_support = Agent(
    name="ai_support_bot",
    model="gemini-3.5-flash",
    instruction="You are a helpful customer support AI. Answer technical questions clearly."
)

human_escalation = Agent(
    name="human_escalation_team",
    model="gemini-3.5-flash",
    instruction="You are a human rep. Frustrated customer. apologize and promise a call."
)

# ===== 1. Define Sentiment Schema =====

class SentimentClassification(BaseModel):
    sentiment: Literal["angry", "neutral", "happy"]

classifier = Agent(
    name="classifier",
    model="gemini-3.5-flash",
    instruction="Classify the sentiment of the user's latest message.",
    output_schema=SentimentClassification
)

# ===== 2. Build the Dynamic Workflow =====

@node(rerun_on_resume=True)
async def support_router_workflow(ctx: Context, node_input: str):
    # Step 2a: Run the classifier node.
    classification: SentimentClassification = await ctx.run_node(classifier, node_input)
    
    # Step 2b: Routing Logic.
    if classification.sentiment == "angry":
        chosen_agent = human_escalation
    else:
        chosen_agent = ai_support
    
    # Step 2c: Execute the chosen agent and return the result.
    return await ctx.run_node(chosen_agent, node_input)

# ===== 3. Register the System =====

root_agent = Workflow(
    name="SupportSystem",
    edges=[("START", support_router_workflow)]
)
