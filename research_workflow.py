"""Core Lab - a research-and-report workflow graph.

The workflow:

    START -> planner -> (background_researcher, news_researcher)
          -> research_join -> writer -> review_router
          -> "revise" back to writer, or "done" to finalize

That single graph uses every pattern from the module: a sequential
chain, a parallel fan-out with a join, a routed cycle (the revise
loop), and conditional routing.

Complete the two sections marked "# YOUR CODE HERE", then run:

    uv run run_workflow.py
"""

from google.adk.agents.context import Context
from google.adk.workflow import JoinNode, START, Workflow, node

from research_agents import (
    background_researcher,
    news_researcher,
    planner,
    writer,
)

# The revise loop runs the writer this many times before finalizing.
MAX_REVISIONS = 2


async def finalize(node_input, ctx: Context) -> dict:
    """Terminal node: returns the finished report from session state."""
    return {"report": ctx.state.get("draft", "")}

async def review_router(node_input, ctx: Context):
    """Decides whether the draft needs another revision pass.

    This is a function node - a deterministic step with no model call.
    """
    revision_round = ctx.state.get("revision_round", 0) + 1
    ctx.state["revision_round"] = revision_round

    if revision_round >= MAX_REVISIONS:
        ctx.route = "done"
    else:
        ctx.route = "revise"

    return f"Revision round {revision_round} of {MAX_REVISIONS}: route={ctx.route}"


# --- Nodes (provided) -------------------------------------------------
# Each node object must be created once and reused in the edges list.
planner_node = node(planner, name="planner")
background_node = node(background_researcher, name="background_researcher")
news_node = node(news_researcher, name="news_researcher")
research_join = JoinNode(name="research_join")
writer_node = node(writer, name="writer")
review_node = node(review_router, name="review_router")
finalize_node = node(finalize, name="finalize")


# --- Edges ------------------------------------------------------------

edges: list = [
    (START, planner_node),
    (planner_node, (background_node, news_node)),  # fan-out
    ((background_node, news_node), research_join),  # fan-in
    (research_join, writer_node),
    (writer_node, review_node),
    (review_node, {"revise": writer_node, "done": finalize_node}),
]

workflow = Workflow(name="research_workflow", edges=edges)


