from google.adk.agents import Agent
from google.adk.workflow import Workflow
from google.adk.apps import App
from google.adk.tools import FunctionTool
from tools.finance import execute_investment

# --- 1. Define the Supervisor Node ---
supervisor = Agent(
    name="supervisor",
    model="gemini-3.5-flash",
    instruction="You are a senior supervisor. Review the large investment request and provide a final verdict."
)

# --- 2. Wrap the Tool for Safety ---
secure_investment_tool = FunctionTool(
    execute_investment,
    require_confirmation=True
)

# --- 3. Define the Main Agent ---
finance_agent = Agent(
    name="finance_agent",
    model="gemini-3.5-flash",
    instruction="Help users with their investments. Use 'execute_investment' for trades.",
    tools=[secure_investment_tool],
    sub_agents=[supervisor] # Required for discovery during transfer
)

# --- 4. Build the Workflow Graph ---
root_agent = Workflow(
    name="SecureSystem",
    edges=[("START", finance_agent)]
)

# --- 5. Export for CLI ---
app = App(name="SecureFinanceApp", root_agent=root_agent)
