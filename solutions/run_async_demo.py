"""Core Lab Step 4 solution - Asynchronous execution and streaming."""

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

    # YOUR CODE HERE - Step 4
    # [SOLUTION]
    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=message
    ):
        is_final = event.is_final_response()
        print(f"event from '{event.author}' | final response: {is_final}")
        if is_final and event.content and event.content.parts:
            print(f"  response: {event.content.parts[0].text}")
    # [/SOLUTION]


if __name__ == "__main__":
    asyncio.run(main())
