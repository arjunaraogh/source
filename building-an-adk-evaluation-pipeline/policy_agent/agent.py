"""The agent under evaluation - a store-policy assistant.

This file is provided complete. In this lab the agent is the *system
under test*: you build an evaluation pipeline around it, you do not
modify it.
"""

import os

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types

POLICIES = {
    "returns": "You have 30 days from delivery to return an item for a full refund.",
    "shipping": "Standard shipping takes 5 business days; expedited takes 2.",
    "warranty": "Every product carries a 1-year limited warranty against defects.",
}


def get_policy(topic: str) -> dict:
    """Looks up the official store policy for a topic.

    Args:
        topic: The policy topic - one of "returns", "shipping", or "warranty".
    """
    key = topic.strip().lower()
    if key not in POLICIES:
        return {
            "status": "error",
            "error_message": f"No policy found for topic '{topic}'.",
        }
    return {"status": "success", "topic": key, "policy": POLICIES[key]}


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

root_agent = LlmAgent(
    name="policy_agent",
    model=MODEL,
    description="Answers customer questions about store policies.",
    instruction=(
        "You answer customer questions about store policies. Always call "
        "the get_policy tool to retrieve the official policy text, then "
        "answer based only on what it returns. Keep answers to one sentence."
    ),
    tools=[get_policy],
)
