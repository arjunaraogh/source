"""Challenge 1 solution - the coordinator using specialists as tools."""

import os

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types
from google.adk.tools.agent_tool import AgentTool

from specialists import make_billing_agent, make_tech_agent

MODEL = Gemini(
    model=os.getenv("ADK_MODEL", "gemini-3.5-flash"),
    retry_options=types.HttpRetryOptions(
        attempts=6,
        initial_delay=2.0,
        max_delay=60.0,
        exp_base=2.0,
        jitter=1.0,
        http_status_codes=[408, 429, 500, 502, 503, 504],
    ),
)

# YOUR CODE HERE - Challenge 1
# [SOLUTION]
root_agent = LlmAgent(
    name="support_coordinator",
    model=MODEL,
    description="Answers customer questions using specialist tools.",
    instruction=(
        "You are a customer-support coordinator. For billing, payment, "
        "and account questions, call the billing_agent tool. For technical "
        "and service-status questions, call the tech_agent tool. Then "
        "answer the user yourself using the tool's result - you remain the "
        "single voice to the customer."
    ),
    tools=[
        AgentTool(agent=make_billing_agent()),
        AgentTool(agent=make_tech_agent()),
    ],
)
# [/SOLUTION]
