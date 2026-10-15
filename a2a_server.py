"""Core Lab - expose the tech agent as a remote A2A server.

This runs the tech specialist as its own networked service. The
coordinator in remote_support_team/ then reaches it over A2A.

Complete the section marked "# YOUR CODE HERE", then start the server
in its own terminal:

    uv run a2a_server.py

Leave it running, then use remote_support_team in a second terminal.
"""

from dotenv import load_dotenv
from google.adk.a2a.utils.agent_to_a2a import to_a2a

from specialists import make_tech_agent

load_dotenv()

A2A_HOST = "localhost"
A2A_PORT = 8001

# YOUR CODE HERE - Step 3
app = to_a2a(make_tech_agent(), host=A2A_HOST, port=A2A_PORT)


if __name__ == "__main__":
    import uvicorn

    print(f"Tech agent A2A server on http://{A2A_HOST}:{A2A_PORT}")
    print(f"Agent card: http://{A2A_HOST}:{A2A_PORT}/.well-known/agent-card.json")
    uvicorn.run(app, host=A2A_HOST, port=A2A_PORT)
