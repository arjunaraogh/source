"""The specialist agents used across the lab.

This file is provided complete. It exposes two *factory functions* rather
than two agent objects. Each call returns a fresh agent - that matters
because an agent may have only one parent, and several coordinators in
this lab each need their own copy of a specialist.
"""

import os

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types

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

# Mock data for the specialist tools.
ACCOUNTS = {
    "A-1001": "$42.50 due on the 15th",
    "A-1002": "paid in full",
}
SERVICES = {
    "email": "operational",
    "vpn": "degraded - engineers investigating",
    "portal": "operational",
}


def get_account_balance(account_id: str) -> dict:
    """Looks up the billing balance for a customer account.

    Args:
        account_id: The account identifier, such as "A-1001".
    """
    balance = ACCOUNTS.get(account_id.strip().upper())
    if balance is None:
        return {
            "status": "error",
            "error_message": f"No account found with id '{account_id}'.",
        }
    return {"status": "success", "account_id": account_id, "balance": balance}


def get_service_status(service_name: str) -> dict:
    """Looks up the operational status of a service.

    Args:
        service_name: The service name, such as "email" or "vpn".
    """
    status = SERVICES.get(service_name.strip().lower())
    if status is None:
        return {
            "status": "error",
            "error_message": f"No service found named '{service_name}'.",
        }
    return {"status": "success", "service": service_name, "service_status": status}


def make_billing_agent() -> LlmAgent:
    """Returns a fresh billing-specialist agent."""
    return LlmAgent(
        name="billing_agent",
        model=MODEL,
        description="Handles billing, payment, and account-balance questions.",
        instruction=(
            "You are a billing specialist. Answer billing and account "
            "questions only. Use get_account_balance to look up a balance. "
            "Be brief and friendly."
        ),
        tools=[get_account_balance],
    )


def make_tech_agent() -> LlmAgent:
    """Returns a fresh technical-support-specialist agent."""
    return LlmAgent(
        name="tech_agent",
        model=MODEL,
        description="Handles technical and service-status questions.",
        instruction=(
            "You are a technical-support specialist. Answer technical "
            "questions only. Use get_service_status to check a service. "
            "Be brief and friendly."
        ),
        tools=[get_service_status],
    )
