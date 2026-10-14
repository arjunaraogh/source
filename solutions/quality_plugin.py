"""Challenge 2 solution - a quality-gate plugin."""

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
        # [SOLUTION]
        if not llm_response.content or not llm_response.content.parts:
            return None
        parts = llm_response.content.parts
        if any(p.function_call for p in parts):
            # A tool-call step, not a final answer - leave it alone.
            return None
        text = parts[0].text
        if not text or len(text.strip()) < MIN_USEFUL_LENGTH:
            self.interventions += 1
            print(
                f"[quality] intervention #{self.interventions} - "
                f"replaced a low-quality response"
            )
            return LlmResponse(
                content=types.Content(
                    role="model", parts=[types.Part(text=FALLBACK)]
                )
            )
        return None
        # [/SOLUTION]
