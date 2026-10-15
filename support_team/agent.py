"""Core Lab - a support coordinator with two specialist sub-agents.

The coordinator delegates each question to the right specialist:
billing questions to billing_agent, technical questions to tech_agent.

Complete the section marked "# YOUR CODE HERE", then run:

    uv run adk run support_team

Ask a billing question and a technical question, and watch the
coordinator hand each one to a different sub-agent.
"""

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
root_agent = LlmAgent(
    name="support_coordinator",
    model=MODEL,
    sub_agents=[make_billing_agent(), make_tech_agent()],
    instruction=(
        "You are a support coordinator. Route each customer request to the "
        "right specialist:\n"
        "- Hand billing and account questions to billing_agent.\n"
        "- Hand technical and service questions to tech_agent.\n"
        "Do not answer specialist questions yourself; always transfer to the "
        "appropriate sub-agent."
    ),
)
