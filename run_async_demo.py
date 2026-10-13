"""Core Lab Step 4 - Asynchronous execution and streaming.

Run the city assistant agent asynchronously and walk the events it
produces. Complete the section marked "# YOUR CODE HERE", then run this
file from the lab's files/ directory:

    uv run run_async_demo.py
"""

import asyncio

from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.genai import types

from city_assistant.agent import root_agent

load_dotenv()

APP_NAME = "city_assistant_demo"
USER_ID = "student"
SESSION_ID = "async-session"


async def main() -> None:
    runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)
    await runner.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )

    message = types.Content(
        role="user",
        parts=[types.Part(text="What time is it in Tokyo?")],
    )

    # Step 4
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=message,
    ):
        print(f"Author: {event.author}")
        print(f"Is Final Response: {event.is_final_response()}")

        if event.is_final_response():
            print(f"Response: {event.content.parts[0].text}")


if __name__ == "__main__":
    asyncio.run(main())
