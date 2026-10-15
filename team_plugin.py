"""Challenge 2 - a process-wide plugin that logs every agent in the team.

This plugin is provided complete. Its before_agent_callback hook fires
for every agent the runner activates - the coordinator and each
sub-agent, the local one and the remote-A2A one alike.
"""

from google.adk.plugins.base_plugin import BasePlugin


class TeamPlugin(BasePlugin):
    """Logs every agent activated during a run."""

    def __init__(self) -> None:
        super().__init__(name="team_plugin")
        self.agents_seen: list[str] = []

    async def before_agent_callback(self, *, agent, callback_context):
        """Runs before every agent in the hierarchy is activated."""
        self.agents_seen.append(agent.name)
        print(f"[team] agent activated: {agent.name}")
        return None
