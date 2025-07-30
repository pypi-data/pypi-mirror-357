"""Tracing module for autonomize observer."""

from .base_tracer import BaseTracer
from .client_wrappers import (
    wrap_openai_async_with_separate_runs,
    wrap_openai_sync_with_separate_runs,
    wrap_anthropic_async_with_separate_runs,
    wrap_anthropic_sync_with_separate_runs,
)

# Import AgentTracer if Kafka dependencies are available
try:
    from .agent_tracer import AgentTracer
except ImportError:
    AgentTracer = None

__all__ = [
    "BaseTracer",
    "AgentTracer",
    "wrap_openai_async_with_separate_runs",
    "wrap_openai_sync_with_separate_runs",
    "wrap_anthropic_async_with_separate_runs",
    "wrap_anthropic_sync_with_separate_runs",
]
