"""Challenge 2 solution - recover from a failing node with a retry config."""

import asyncio

from google.adk.agents.context import Context
from google.adk.runners import InMemoryRunner
from google.adk.workflow import RetryConfig, START, Workflow, node
from google.genai import types

# Tracks attempts so the node fails once, then succeeds (an induced failure).
_attempts = {"count": 0}


async def flaky_fetch(node_input, ctx: Context):
    """A node that fails on its first attempt, then succeeds."""
    _attempts["count"] += 1
    if _attempts["count"] < 2:
        raise RuntimeError(f"induced failure on attempt {_attempts['count']}")
    return f"fetch succeeded on attempt {_attempts['count']}"


async def report(node_input, ctx: Context):
    """Terminal node - reports what the fetch produced."""
    return f"workflow finished: {node_input}"


# YOUR CODE HERE - Challenge 2
# [SOLUTION]
fetch_node = node(
    flaky_fetch, name="fetch", retry_config=RetryConfig(max_attempts=3)
)
# [/SOLUTION]


report_node = node(report, name="report")

workflow = Workflow(
    name="retry_workflow",
    edges=[
        (START, fetch_node),
        (fetch_node, report_node),
    ],
)


async def main() -> None:
    runner = InMemoryRunner(node=workflow, app_name="retry_workflow")
    session = await runner.session_service.create_session(
        app_name="retry_workflow", user_id="student"
    )
    message = types.Content(role="user", parts=[types.Part(text="go")])
    print("Running the workflow (the fetch node fails on its first attempt)...\n")
    try:
        async for event in runner.run_async(
            user_id="student", session_id=session.id, new_message=message
        ):
            info = getattr(event, "node_info", None)
            output = getattr(event, "output", None)
            if info and output is not None:
                print(f"[node] {info.path}: {output}")
        print("\nThe workflow completed - the retry recovered the failed node.")
    except Exception as exc:  # noqa: BLE001 - demo: show the unrecovered failure
        print(f"\nThe workflow failed: {exc!r}")
        print("Add a RetryConfig to the fetch node so it recovers.")


if __name__ == "__main__":
    asyncio.run(main())
