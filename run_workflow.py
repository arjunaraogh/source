"""Run the research-and-report workflow and trace each node.

This file is provided complete - you do not need to edit it.

It runs the workflow in research_workflow.py against a sample topic and
prints a step-by-step trace: every node that runs, in order, with a
snippet of what it produced. Watch the trace to see the parallel
research branches and the revise loop.

Run it from the files/ directory:

    uv run run_workflow.py
"""

import asyncio

from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.genai import errors as genai_errors
from google.genai import types

from research_workflow import workflow

load_dotenv()

APP_NAME = "research_workflow"
USER_ID = "student"
TOPIC = "the history and future of electric vehicles"


def _snippet(value, limit: int = 160) -> str:
    """Return a short one-line snippet of a node's output."""
    text = " ".join(str(value).split())
    return text if len(text) <= limit else text[:limit] + "..."


async def main() -> None:
    runner = InMemoryRunner(node=workflow, app_name=APP_NAME)
    session = await runner.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID
    )
    message = types.Content(role="user", parts=[types.Part(text=TOPIC)])

    print(f"Topic: {TOPIC}\n")
    print("--- workflow trace ---")
    try:
        async for event in runner.run_async(
            user_id=USER_ID, session_id=session.id, new_message=message
        ):
            info = getattr(event, "node_info", None)
            output = getattr(event, "output", None)
            if info and output is not None:
                print(f"[node] {info.path}")
                print(f"       {_snippet(output)}\n")
    except genai_errors.APIError as exc:
        code = getattr(exc, "code", None)
        if code == 429:
            print("[the Gemini API quota was exceeded - use a billing-enabled key]")
        else:
            print("[the model is temporarily unavailable - run the script again]")
        return

    session = await runner.session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session.id
    )
    print("--- final report ---")
    print(session.state.get("draft", "(no draft produced)"))


if __name__ == "__main__":
    asyncio.run(main())
