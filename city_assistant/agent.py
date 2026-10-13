"""Core Lab - City Assistant agent.

This agent answers questions about the current time in a city. Complete
the two sections marked "# YOUR CODE HERE", then run the agent from the
lab's files/ directory with:

    uv run adk run city_assistant
"""

import os

from google.adk.agents import LlmAgent


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city: The name of the city to look up.
    """
    # A small lookup table stands in for a real time service.
    known_times = {
        "paris": "10:30 PM",
        "tokyo": "5:30 AM",
        "new york": "4:30 PM",
        "london": "9:30 PM",
    }
    city_key = city.strip().lower()

    # Step 2
    if city_key not in known_times:
        return {
            "status": "error",
            "error_message": f"Unknown city: {city}"
        }

    return {
        "status": "success",
        "city": city,
        "time": known_times[city_key]
    }


root_agent = LlmAgent(
    name="city_assistant",
    model=os.getenv("ADK_MODEL", "gemini-3.5-flash"),
    description="Answers questions about the current time in a city.",
    # Step 3
    instruction=(
        "When a user asks for the current time in a city, use the "
        "get_current_time tool to retrieve the information. "
        "If the tool returns an error, explain that the city is not available. "
        "Otherwise, provide the city and its current time."
    ),
    tools=[get_current_time],
)