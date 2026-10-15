"""Core Lab solution - a research-and-report workflow graph."""

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
    # YOUR CODE HERE - Step 1
    # [SOLUTION]
    rounds = ctx.state.get("revision_round", 0) + 1
    ctx.state["revision_round"] = rounds
    ctx.route = "done" if rounds >= MAX_REVISIONS else "revise"
    return f"revision check: round {rounds}, route '{ctx.route}'"
    # [/SOLUTION]


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
# YOUR CODE HERE - Step 2
# [SOLUTION]
edges = [
    (START, planner_node),
    (planner_node, (background_node, news_node)),
    ((background_node, news_node), research_join),
    (research_join, writer_node),
    (writer_node, review_node),
    (review_node, {"revise": writer_node, "done": finalize_node}),
]
# [/SOLUTION]


workflow = Workflow(name="research_workflow", edges=edges)
