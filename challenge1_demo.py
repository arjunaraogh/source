"""Challenge - Run the city assistant with session state.

This script starts a session with an initial state value for the key
"user:name" and runs the agent once. After you change the agent's
instruction to a state-templated string (the Challenge), the agent will
greet the user by the name set here.

This file is provided complete - you do not need to edit it. Run it from
the lab's files/ directory:

    uv run challenge1_demo.py
"""

import asyncio

from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.genai import types

from city_assistant.agent import root_agent

load_dotenv()

APP_NAME = "city_assistant_demo"
USER_ID = "student"
SESSION_ID = "challenge1-session"


async def main() -> None:
    runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)

    # The session starts with a value in state. The agent's
    # state-templated instruction reads {user:name?} from here.
    await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state={"user:name": "Ada Lovelace"},
    )

    message = types.Content(
        role="user",
        parts=[types.Part(text="Hello! What time is it in London?")],
    )

    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=message
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
