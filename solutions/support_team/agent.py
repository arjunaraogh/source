"""Core Lab solution - a support coordinator with two specialist sub-agents."""

import os

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types

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

# YOUR CODE HERE - Step 1
# [SOLUTION]
root_agent = LlmAgent(
    name="support_coordinator",
    model=MODEL,
    description="Routes customer questions to the right specialist.",
    instruction=(
        "You are a customer-support coordinator. Hand billing, payment, "
        "and account questions to billing_agent. Hand technical and "
        "service-status questions to tech_agent. Do not answer specialist "
        "questions yourself - always delegate."
    ),
    sub_agents=[make_billing_agent(), make_tech_agent()],
)
# [/SOLUTION]
