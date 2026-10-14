"""Challenge 2 - a quality-gate plugin.

When the model returns a low-quality answer - empty, or too short to be
useful - this plugin intervenes in the after-model hook and replaces it
with a safe fallback message.

This is the detect-and-intervene half of a "reflect-and-retry" pattern;
a production version would re-issue the request. Here, replacing the
weak answer is enough to see the intervention work.

Complete the hook marked "# YOUR CODE HERE", then run with the quality
gate enabled (set EXTRA_PLUGIN=quality in .env):

    uv run run_agent.py
"""

from google.adk.models.llm_response import LlmResponse
from google.adk.plugins.base_plugin import BasePlugin
from google.genai import types

MIN_USEFUL_LENGTH = 15
FALLBACK = (
    "I'm not able to give a complete answer to that. Could you rephrase "
    "your question, or give me an order id to look up?"
)


class QualityGatePlugin(BasePlugin):
    """Replaces low-quality model responses with a safe fallback."""

    def __init__(self) -> None:
        super().__init__(name="quality_gate_plugin")
        self.interventions = 0

    async def after_model_callback(self, *, callback_context, llm_response):
        """Inspect the model's answer and replace it if it is low quality."""
        # YOUR CODE HERE - Challenge 2
        # 1. If llm_response has no content or parts, return None.
        # 2. If any part has a .function_call, this is a tool-call step,
        #    not a final answer - return None and leave it alone.
        # 3. Read the answer text from the first part (it may be None).
        # 4. If the text is missing or shorter than MIN_USEFUL_LENGTH,
        #    increment self.interventions, print an intervention line, and
        #    return a new LlmResponse whose content is a model-role
        #    types.Content carrying the FALLBACK message.
        # 5. Otherwise return None.
        return None
