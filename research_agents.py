"""The LLM agents used by the research-and-report workflow.

This file is provided complete. Each agent is an ordinary LlmAgent. The
workflow in research_workflow.py wires them into a graph; the agents
themselves do not know they are part of a workflow.

Data flows between agents through session state:
  - planner            writes  output_key "plan"
  - background_researcher writes "background"
  - news_researcher       writes "recent"
  - writer             writes  output_key "draft"
Downstream agents read those values with {placeholder} templating.
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

planner = LlmAgent(
    name="planner",
    model=MODEL,
    description="Turns a topic into a short research plan.",
    instruction=(
        "The user gives you a topic to report on. Produce a short research "
        "plan: three or four specific questions worth answering about the "
        "topic. Output only the numbered questions, nothing else."
    ),
    output_key="plan",
)

background_researcher = LlmAgent(
    name="background_researcher",
    model=MODEL,
    description="Researches background and fundamentals.",
    instruction=(
        "You research background and fundamentals. Using the research plan "
        "below, write two or three paragraphs of background context on the "
        "topic.\n\nResearch plan:\n{plan}"
    ),
    output_key="background",
)

news_researcher = LlmAgent(
    name="news_researcher",
    model=MODEL,
    description="Researches recent and notable developments.",
    instruction=(
        "You research recent developments. Using the research plan below, "
        "write two or three paragraphs on recent or notable developments "
        "related to the topic.\n\nResearch plan:\n{plan}"
    ),
    output_key="recent",
)

writer = LlmAgent(
    name="writer",
    model=MODEL,
    description="Writes the report from the research.",
    instruction=(
        "Write a concise, well-organized report using the research below. "
        "Give it a title and four to six short paragraphs.\n\n"
        "Background:\n{background}\n\nRecent developments:\n{recent}\n\n"
        "If an earlier draft exists, improve it rather than starting over:\n"
        "{draft?}"
    ),
    output_key="draft",
)
