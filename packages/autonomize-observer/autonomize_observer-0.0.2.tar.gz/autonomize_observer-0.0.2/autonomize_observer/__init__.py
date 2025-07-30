"""Autonomize ML Observability package."""

from .version import __version__

# Import core monitoring functions
from .monitoring import (
    initialize,
    monitor,
    identify,
    wrap_openai,
    wrap_anthropic,
    trace_async,
    trace_sync,
    agent,
    tool,
    Identify,
    CostTracker,
    KafkaLLMMonitor,
    get_kafka_llm_monitor,
    close_kafka_llm_monitor,
    track_llm_call,
)

# Import legacy monitoring tools
from .monitoring.async_monitor import AsyncMonitor

# Import tracing tools
from .tracing.base_tracer import BaseTracer

# Import AgentTracer if available
try:
    from .tracing.agent_tracer import AgentTracer
except ImportError:
    AgentTracer = None

# Import client wrapper functions
from .tracing.client_wrappers import (
    wrap_openai_async_with_separate_runs,
    wrap_openai_sync_with_separate_runs,
    wrap_anthropic_async_with_separate_runs,
    wrap_anthropic_sync_with_separate_runs,
)

# Import MLflow client
from .core.mlflow_client import MLflowClient

__all__ = [
    "__version__",
    # Core monitoring functions (most commonly used)
    "initialize",
    "monitor",
    "identify",
    "wrap_openai",
    "wrap_anthropic",
    # Decorators
    "trace_async",
    "trace_sync",
    "agent",
    "tool",
    # Classes
    "Identify",
    "CostTracker",
    "KafkaLLMMonitor",
    "AsyncMonitor",
    "BaseTracer",
    "AgentTracer",
    "MLflowClient",
    # Kafka monitoring
    "get_kafka_llm_monitor",
    "close_kafka_llm_monitor",
    "track_llm_call",
    # Client wrappers
    "wrap_openai_async_with_separate_runs",
    "wrap_openai_sync_with_separate_runs",
    "wrap_anthropic_async_with_separate_runs",
    "wrap_anthropic_sync_with_separate_runs",
]
