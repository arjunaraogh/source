"""Challenge 1 - branch the workflow on the type of request.

A router function node inspects the request and routes it to either a
quick-summary path or a full-report path. The router is a function node,
so the decision is deterministic and costs no model call.

Complete classify_request where marked, then run:

    uv run challenge1_routing.py
"""

import asyncio
import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.agents.context import Context
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.workflow import START, Workflow, node
from google.genai import errors as genai_errors
from google.genai import types

load_dotenv()
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

summarizer = LlmAgent(
    name="summarizer",
    model=MODEL,
    instruction="Write a two-sentence summary of the topic in the request.",
)
reporter = LlmAgent(
    name="reporter",
    model=MODEL,
    instruction="Write a detailed, multi-paragraph report on the topic "
    "in the request.",
)


async def classify_request(node_input, ctx: Context):
    """Router: send summary requests one way, report requests the other."""
    # YOUR CODE HERE - Challenge 1
    # 1. Read the request text - node_input.parts[0].text - lowercased.
    # 2. If it mentions "summary" or "summarize", set ctx.route = "summary".
    # 3. Otherwise set ctx.route = "report".
    # The routing map below sends the run to the matching node.
    return "classify_request not implemented"


router_node = node(classify_request, name="router")
summary_node = node(summarizer, name="summarizer")
report_node = node(reporter, name="reporter")

workflow = Workflow(
    name="request_router",
    edges=[
        (START, router_node),
        (router_node, {"summary": summary_node, "report": report_node}),
    ],
)

REQUESTS = [
    "Give me a quick summary of quantum computing.",
    "I need a detailed report on quantum computing.",
]


async def main() -> None:
    runner = InMemoryRunner(node=workflow, app_name="request_router")
    for request in REQUESTS:
        session = await runner.session_service.create_session(
            app_name="request_router", user_id="student"
        )
        message = types.Content(role="user", parts=[types.Part(text=request)])
        print(f"\nRequest: {request}")
        try:
            async for event in runner.run_async(
                user_id="student", session_id=session.id, new_message=message
            ):
                info = getattr(event, "node_info", None)
                output = getattr(event, "output", None)
                if info and output is not None:
                    print(f"  [node] {info.path}")
        except genai_errors.APIError as exc:
            code = getattr(exc, "code", None)
            if code == 429:
                print("  [the Gemini API quota was exceeded - use a billing-enabled key]")
            else:
                print("  [the model is temporarily unavailable - run again]")


if __name__ == "__main__":
    asyncio.run(main())
