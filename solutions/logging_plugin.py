"""Core Lab solution - a process-wide logging plugin."""

from google.adk.plugins.base_plugin import BasePlugin


class LoggingPlugin(BasePlugin):
    """Logs every model call and tool call across the whole run."""

    def __init__(self) -> None:
        super().__init__(name="logging_plugin")
        self.model_calls = 0
        self.tool_calls = 0

    async def before_model_callback(self, *, callback_context, llm_request):
        """Runs before every model call, for every agent in the run."""
        # YOUR CODE HERE - Step 3
        # [SOLUTION]
        self.model_calls += 1
        print(
            f"[log] model call #{self.model_calls} "
            f"by agent {callback_context.agent_name}"
        )
        return None
        # [/SOLUTION]

    async def before_tool_callback(self, *, tool, tool_args, tool_context):
        """Runs before every tool call, for every agent in the run."""
        # YOUR CODE HERE - Step 4
        # [SOLUTION]
        self.tool_calls += 1
        print(f"[log] tool call: {tool.name}({tool_args})")
        return None
        # [/SOLUTION]
