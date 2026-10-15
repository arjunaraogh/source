"""Core Lab solution - expose the tech agent as a remote A2A server.

Run from the lab's files/ directory (not from solutions/):

    uv run python solutions/a2a_server.py

or, after completing the starter file:

    uv run a2a_server.py
"""

from dotenv import load_dotenv
from google.adk.a2a.utils.agent_to_a2a import to_a2a

from specialists import make_tech_agent

load_dotenv()

A2A_HOST = "localhost"
A2A_PORT = 8001

# YOUR CODE HERE - Step 3
# [SOLUTION]
app = to_a2a(make_tech_agent(), host=A2A_HOST, port=A2A_PORT)
# [/SOLUTION]


if __name__ == "__main__":
    import uvicorn

    print(f"Tech agent A2A server on http://{A2A_HOST}:{A2A_PORT}")
    print(f"Agent card: http://{A2A_HOST}:{A2A_PORT}/.well-known/agent-card.json")
    uvicorn.run(app, host=A2A_HOST, port=A2A_PORT)
