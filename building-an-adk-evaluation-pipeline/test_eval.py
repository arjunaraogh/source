"""Run the policy agent's evaluation set as a pytest test.

Complete the marked section, then run from the files/ directory:

    uv run pytest test_eval.py -s
"""

import asyncio
import os
import pathlib
import threading

import pytest
from dotenv import load_dotenv

# Ensure `uv run pytest ...` picks up local .env settings for API-backed evals.
load_dotenv(dotenv_path=pathlib.Path(__file__).parent / ".env")

from google.adk.evaluation.agent_evaluator import AgentEvaluator

# The evaluation set lives next to this file. AgentEvaluator looks for
# test_config.json in the same folder for the pass/fail criteria.
EVALSET = pathlib.Path(__file__).parent / "policy_agent.evalset.json"
EVAL_TIMEOUT_SECONDS = int(os.getenv("ADK_EVAL_TIMEOUT_SECONDS", "90"))
HEARTBEAT_SECONDS = int(os.getenv("ADK_EVAL_HEARTBEAT_SECONDS", "10"))


def _is_quota_error(exc: Exception) -> bool:
    """Return True when the exception indicates Gemini quota/rate-limit exhaustion."""
    text = str(exc).lower()
    signals = (
        "resource_exhausted",
        "quota exceeded",
        "rate limit",
        "429",
        "retry in",
    )
    return any(signal in text for signal in signals)


def _start_heartbeat(interval_seconds: int) -> tuple[threading.Event, threading.Thread]:
    """Start background progress output while waiting on remote model calls."""

    stop_event = threading.Event()

    def _run() -> None:
        elapsed_seconds = 0
        while not stop_event.wait(interval_seconds):
            elapsed_seconds += interval_seconds
            print(
                f"Still running ADK evaluation... {elapsed_seconds}s elapsed",
                flush=True,
            )

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return stop_event, thread

async def test_policy_agent_evaluation():
    """Evaluates policy_agent against its evaluation set."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "voc-your-key-here":
        reason = "Set GEMINI_API_KEY in .env before running this evaluation test."
        print(f"Skipping: {reason}", flush=True)
        pytest.skip(reason)

    heartbeat_stop: threading.Event | None = None
    heartbeat_thread: threading.Thread | None = None
    try:
        print(
            f"Starting ADK evaluation (timeout: {EVAL_TIMEOUT_SECONDS}s)...",
            flush=True,
        )
        heartbeat_stop, heartbeat_thread = _start_heartbeat(HEARTBEAT_SECONDS)

        await asyncio.wait_for(
            AgentEvaluator.evaluate(
                agent_module="policy_agent",
                eval_dataset_file_path_or_dir=str(EVALSET),
            ),
            timeout=EVAL_TIMEOUT_SECONDS,
        )

        print("ADK evaluation finished.", flush=True)
    except TimeoutError:
        reason = (
            "Evaluation timed out while waiting for model responses. Retry later or "
            "increase ADK_EVAL_TIMEOUT_SECONDS."
        )
        print(f"Skipping: {reason}", flush=True)
        pytest.skip(reason)
    except Exception as exc:
        if _is_quota_error(exc):
            reason = (
                "Gemini API quota/rate limit was exceeded. Retry later or use a "
                "billing-enabled key."
            )
            print(f"Skipping: {reason}", flush=True)
            pytest.skip(reason)
        raise
    finally:
        if heartbeat_stop is not None:
            heartbeat_stop.set()
        if heartbeat_thread is not None:
            heartbeat_thread.join(timeout=1.0)