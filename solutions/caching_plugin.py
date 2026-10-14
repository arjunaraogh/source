"""Challenge 1 solution - a response-caching plugin."""

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
        # [SOLUTION]
        key = _request_key(llm_request)
        callback_context.state["temp:cache_key"] = key
        if key in self.cache:
            print(f"[cache] hit - skipping model call for: {key[:50]!r}")
            return self.cache[key]
        print(f"[cache] miss - calling model for: {key[:50]!r}")
        return None
        # [/SOLUTION]

    async def after_model_callback(self, *, callback_context, llm_response):
        """Store this fresh model response in the cache."""
        # YOUR CODE HERE - Challenge 1
        # [SOLUTION]
        key = callback_context.state.get("temp:cache_key")
        if key and llm_response.content and llm_response.content.parts:
            self.cache[key] = llm_response
        return None
        # [/SOLUTION]
