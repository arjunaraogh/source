"""Challenge 2 - run the team under a process-wide plugin.

The plugin's hooks should fire across the whole team: the coordinator,
the local billing agent, and the remote tech agent.

This uses the remote_support_team coordinator, so a2a_server.py must be
running in another terminal first.

Complete the section marked "# YOUR CODE HERE", then run:

    uv run run_with_plugin.py
"""

import asyncio

from dotenv import load_dotenv
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import errors as genai_errors
from google.genai import types

from remote_support_team.agent import root_agent
from team_plugin import TeamPlugin

load_dotenv()

APP_NAME = "support"
USER_ID = "student"
QUESTIONS = [
    "What is the balance on account A-1001?",
    "Is the VPN service working right now?",
]


async def run_turn(runner, session_id, text):
    """Run one turn and print the coordinator's final answer."""
    message = types.Content(role="user", parts=[types.Part(text=text)])
    try:
        async for event in runner.run_async(
            user_id=USER_ID, session_id=session_id, new_message=message
        ):
            if event.is_final_response() and event.content and event.content.parts:
                print(f"Answer: {event.content.parts[0].text}")
    except genai_errors.APIError as exc:
        code = getattr(exc, "code", None)
        if code == 429:
            print("[the Gemini API quota was exceeded - use a billing-enabled key]")
        else:
            print("[the model is temporarily unavailable - run the script again]")


async def main() -> None:
    plugin = TeamPlugin()
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID
    )

    # YOUR CODE HERE - Challenge 2
    # Register the plugin by building an App with it, then handing that
    # App to the Runner:
    #     app = App(name=APP_NAME, root_agent=root_agent, plugins=[plugin])
    #     runner = Runner(app=app, session_service=session_service)
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    for question in QUESTIONS:
        print(f"\nUser: {question}")
        await run_turn(runner, session.id, question)

    print(f"\nAgents the plugin saw: {plugin.agents_seen}")


if __name__ == "__main__":
    asyncio.run(main())
