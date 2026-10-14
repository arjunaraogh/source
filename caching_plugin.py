"""Challenge 1 - a response-caching plugin.

When the same request reaches the model twice, the second call is waste.
This plugin remembers each model response and serves it from a cache the
next time an identical request appears - skipping the model call.

Complete the two hooks marked "# YOUR CODE HERE", then run with caching
enabled (set EXTRA_PLUGIN=caching in .env):

    uv run run_agent.py
"""

from google.adk.plugins.base_plugin import BasePlugin


def _request_key(llm_request) -> str:
    """Builds a cache key from the most recent user message."""
    for content in reversed(llm_request.contents or []):
        if content.role == "user" and content.parts:
            return " ".join(p.text for p in content.parts if p.text)
    return ""


class CachingPlugin(BasePlugin):
    """Caches model responses so identical requests skip the model."""

    def __init__(self) -> None:
        super().__init__(name="caching_plugin")
        self.cache: dict = {}

    async def before_model_callback(self, *, callback_context, llm_request):
        """Serve a cached response if this request has been seen before."""
        # YOUR CODE HERE - Challenge 1
        # 1. Build the key with _request_key(llm_request).
        # 2. Stash it for the after-model hook:
        #       callback_context.state["temp:cache_key"] = key
        # 3. If the key is in self.cache, print a "cache hit" line and
        #    return the cached LlmResponse - this SKIPS the model call.
        # 4. Otherwise print a "cache miss" line and return None.
        return None

    async def after_model_callback(self, *, callback_context, llm_response):
        """Store this fresh model response in the cache."""
        # YOUR CODE HERE - Challenge 1
        # 1. Read the key back: callback_context.state.get("temp:cache_key").
        # 2. If there is a key and llm_response has content with parts,
        #    store llm_response in self.cache under that key.
        # 3. Return None - this hook only observes; it changes nothing.
        return None
