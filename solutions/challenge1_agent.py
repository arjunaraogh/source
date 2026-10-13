"""Challenge solution - City Assistant with a state-templated instruction.

This is the Core Lab agent.py with one change: the instruction is now a
state-templated string. The {user:name?} placeholder is filled from
session state at run time. The trailing "?" makes the placeholder
optional, so the instruction still works when no name is set.

To use this solution, replace the contents of city_assistant/agent.py
with this file, then run the provided script:

    uv run challenge1_demo.py
"""

import os

from google.adk.agents import LlmAgent


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city: The name of the city to look up.
    """
    known_times = {
        "paris": "10:30 PM",
        "tokyo": "5:30 AM",
        "new york": "4:30 PM",
        "london": "9:30 PM",
    }
    city_key = city.strip().lower()
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


root_agent = LlmAgent(
    name="city_assistant",
    model=os.getenv("ADK_MODEL", "gemini-3.5-flash"),
    description="Answers questions about the current time in a city.",
    instruction=(
        "You are a friendly city assistant helping {user:name?}. "
        "Greet the user by name when a name is available. When the user "
        "asks about the current time in a city, call the get_current_time "
        "tool and report the result in a natural sentence."
    ),
    tools=[get_current_time],
)
