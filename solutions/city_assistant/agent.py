"""Core Lab solution - City Assistant agent."""

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

    # YOUR CODE HERE - Step 2
    # [SOLUTION]
    if city_key not in known_times:
        return {
            "status": "error",
            "error_message": f"No time information is available for '{city}'.",
        }
    return {
        "status": "success",
        "city": city,
        "time": known_times[city_key],
    }
    # [/SOLUTION]


root_agent = LlmAgent(
    name="city_assistant",
    model=os.getenv("ADK_MODEL", "gemini-3.5-flash"),
    description="Answers questions about the current time in a city.",
    # YOUR CODE HERE - Step 3
    # [SOLUTION]
    instruction=(
        "You are a friendly city assistant. When the user asks about the "
        "current time in a city, call the get_current_time tool with that "
        "city and report the result in a natural sentence. If the tool "
        "returns an error, apologize and tell the user which city was not "
        "found."
    ),
    tools=[get_current_time],
    # [/SOLUTION]
)
