from __future__ import annotations
from pydantic import BaseModel
from google.adk import Agent, Workflow
from typing import Literal

# 1. Define the Classification Schema
class MarketRoute(BaseModel):
    currency: Literal["USD", "EUR", "GBP"]

# 2. Create the Classifier Node
classifier = Agent(
    name="classifier",
    model="gemini-3.5-flash",
    instruction="Extract the currency (USD, EUR, or GBP) from the user's request. Return ONLY the JSON.",
    output_schema=MarketRoute
)

# 3. Create Specialist Agents (Nodes)
usd_analyst = Agent(
    name="usd_analyst",
    model="gemini-3.5-flash",
    instruction="Provide a brief, bullish outlook for the US Dollar."
)

eur_analyst = Agent(
    name="eur_analyst",
    model="gemini-3.5-flash",
    instruction="Provide a brief, cautious outlook for the Euro."
)

gbp_analyst = Agent(
    name="gbp_analyst",
    model="gemini-3.5-flash",
    instruction="Provide a brief, neutral outlook for the British Pound."
)

# 4. Build the Deterministic Workflow
root_agent = Workflow(
    name="MarketSystem",
    edges=[
        ("START", classifier),
        (classifier, {
            "USD": usd_analyst,
            "EUR": eur_analyst,
            "GBP": gbp_analyst
        })
    ]
)
