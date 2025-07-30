"""
This module provides monitoring and observability capabilities for LLM (Large Language Model)
clients.
It includes functionality for cost tracking, MLflow integration, and client wrapping for various
LLM providers like OpenAI, Azure OpenAI, and Anthropic.
"""

import os
import logging
from typing import Optional, Any, List, Dict
import asyncio
import inspect
import time
import functools
import threading
import uuid
from datetime import datetime, timezone

import mlflow

from autonomize.core.credential import ModelhubCredential
from autonomize_observer.utils import setup_logger
from .cost_tracking import CostTracker
from autonomize_observer.core.mlflow_client import MLflowClient

# NEW IMPORTS
from .async_monitor import (
    initialize_async,
    _monitor as async_monitor,
)

# Import Kafka components with fallback
try:
    from autonomize_observer.kafka import (
        KafkaTraceProducer,
        LLMCallEvent,
        KAFKA_AVAILABLE,
    )
except ImportError:
    KAFKA_AVAILABLE = False
    KafkaTraceProducer = None
    LLMCallEvent = None

from autonomize_observer.tracing.client_wrappers import (
    wrap_openai_async_with_separate_runs as _wrap_openai_async_with_separate_runs,
    wrap_openai_sync_with_separate_runs as _wrap_openai_sync_with_separate_runs,
    wrap_anthropic_async_with_separate_runs as _wrap_anthropic_async_with_separate_runs,
    wrap_anthropic_sync_with_separate_runs as _wrap_anthropic_sync_with_separate_runs,
)

logger = setup_logger(__name__)

# Global instances
_mlflow_client: Optional[MLflowClient] = None
_cost_tracker: CostTracker
_initialized: bool = False  # NEW: Global initialization flag

# Add thread-local storage for run management
_local = threading.local()


class KafkaLLMMonitor:
    """
    Kafka-based LLM monitor for direct LLM call tracking.

    Sends LLM events to Kafka for centralized processing, replacing the
    local AsyncMonitor approach with a scalable distributed architecture.
    """

    def __init__(self, kafka_config: Optional[Dict[str, Any]] = None):
        """
        Initialize Kafka LLM monitor.

        Args:
            kafka_config: Optional Kafka configuration overrides
        """
        if not KAFKA_AVAILABLE:
            logger.warning(
                "Kafka not available. Install confluent-kafka for LLM monitoring: "
                "pip install confluent-kafka"
            )
            self._producer = None
            self._enabled = False
            return

        # Load Kafka configuration from environment
        kafka_config = kafka_config or {}
        default_config = {
            "bootstrap_servers": os.getenv(
                "AUTONOMIZE_KAFKA_BROKERS", "localhost:9092"
            ),
            "topic": os.getenv("AUTONOMIZE_KAFKA_TOPIC", "genesis-traces"),
            "client_id": os.getenv("AUTONOMIZE_KAFKA_CLIENT_ID", "genesis-llm-monitor"),
            "kafka_username": os.getenv("AUTONOMIZE_KAFKA_USERNAME"),
            "kafka_password": os.getenv("AUTONOMIZE_KAFKA_PASSWORD"),
            "security_protocol": os.getenv(
                "AUTONOMIZE_KAFKA_SECURITY_PROTOCOL", "PLAINTEXT"
            ),
            "sasl_mechanism": os.getenv("AUTONOMIZE_KAFKA_SASL_MECHANISM", "PLAIN"),
        }

        # Remove None values
        default_config = {k: v for k, v in default_config.items() if v is not None}

        # Merge with user config
        final_config = {**default_config, **kafka_config}

        try:
            self._producer = KafkaTraceProducer(**final_config)
            self._enabled = True
            logger.info("Kafka LLM monitor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka LLM monitor: {e}")
            self._producer = None
            self._enabled = False

    @property
    def enabled(self) -> bool:
        """Check if Kafka monitoring is enabled."""
        return self._enabled

    def track_llm_start(
        self,
        call_id: str,
        model: str,
        provider: str,
        messages: List[Dict],
        params: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Track LLM call start without blocking.

        Args:
            call_id: Unique identifier for this LLM call
            model: Model name (e.g., 'gpt-4o', 'claude-3-5-sonnet')
            provider: Provider name (e.g., 'openai', 'anthropic')
            messages: Input messages/prompts
            params: Request parameters (temperature, max_tokens, etc.)
            user_id: Optional user identifier
            session_id: Optional session identifier
            metadata: Optional additional metadata

        Returns:
            bool: True if event was sent successfully
        """
        if not self._enabled:
            return False

        try:
            return self._producer.send_llm_start(
                call_id=call_id,
                model=model,
                provider=provider,
                messages=messages,
                params=params,
                user_id=user_id,
                session_id=session_id,
                metadata=metadata,
            )
        except Exception as e:
            logger.error(f"Failed to track LLM start: {e}")
            return False

    def track_llm_end(
        self,
        call_id: str,
        model: str,
        provider: str,
        duration_ms: float,
        usage: Dict[str, int],
        response: Optional[str] = None,
        cost: Optional[float] = None,
        error: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Track LLM call completion without blocking.

        Args:
            call_id: Unique identifier for this LLM call
            model: Model name
            provider: Provider name
            duration_ms: Call duration in milliseconds
            usage: Token usage {prompt_tokens, completion_tokens, total_tokens}
            response: Response content (will be truncated)
            cost: Calculated cost for the call
            error: Error message if call failed
            user_id: Optional user identifier
            session_id: Optional session identifier
            metadata: Optional additional metadata

        Returns:
            bool: True if event was sent successfully
        """
        if not self._enabled:
            return False

        try:
            return self._producer.send_llm_end(
                call_id=call_id,
                model=model,
                provider=provider,
                duration_ms=duration_ms,
                usage=usage,
                response=response,
                cost=cost,
                error=error,
                user_id=user_id,
                session_id=session_id,
                metadata=metadata,
            )
        except Exception as e:
            logger.error(f"Failed to track LLM end: {e}")
            return False

    def track_llm_metric(
        self,
        call_id: str,
        metrics: Dict[str, float],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Track additional LLM metrics without blocking.

        Args:
            call_id: Unique identifier for this LLM call
            metrics: Dictionary of metric name -> value
            user_id: Optional user identifier
            session_id: Optional session identifier
            metadata: Optional additional metadata

        Returns:
            bool: True if event was sent successfully
        """
        if not self._enabled:
            return False

        try:
            return self._producer.send_llm_metric(
                call_id=call_id,
                metrics=metrics,
                user_id=user_id,
                session_id=session_id,
                metadata=metadata,
            )
        except Exception as e:
            logger.error(f"Failed to track LLM metric: {e}")
            return False

    def flush(self, timeout: float = 10.0) -> int:
        """
        Flush pending messages.

        Args:
            timeout: Maximum time to wait for messages to be delivered

        Returns:
            Number of messages still pending after timeout
        """
        if self._producer:
            return self._producer.flush(timeout)
        return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get monitor statistics."""
        if self._producer:
            return self._producer.get_stats()
        return {"enabled": False, "reason": "Kafka not available"}

    def close(self):
        """Close the monitor and cleanup resources."""
        if self._producer:
            self._producer.close()
            self._producer = None
        self._enabled = False
        logger.info("Kafka LLM monitor closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Global monitor instance
_kafka_llm_monitor: Optional[KafkaLLMMonitor] = None
_monitor_lock = threading.Lock()


def get_kafka_llm_monitor(
    kafka_config: Optional[Dict[str, Any]] = None,
) -> KafkaLLMMonitor:
    """
    Get or create the global Kafka LLM monitor instance.

    Args:
        kafka_config: Optional Kafka configuration overrides

    Returns:
        KafkaLLMMonitor instance
    """
    global _kafka_llm_monitor

    with _monitor_lock:
        if _kafka_llm_monitor is None:
            _kafka_llm_monitor = KafkaLLMMonitor(kafka_config)
        return _kafka_llm_monitor


def close_kafka_llm_monitor():
    """Close the global Kafka LLM monitor."""
    global _kafka_llm_monitor

    with _monitor_lock:
        if _kafka_llm_monitor:
            _kafka_llm_monitor.close()
            _kafka_llm_monitor = None


# Helper function for easy integration
def track_llm_call(
    model: str,
    provider: str,
    messages: List[Dict],
    usage: Dict[str, int],
    duration_ms: float,
    response: Optional[str] = None,
    cost: Optional[float] = None,
    error: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Track a complete LLM call with start and end events.

    Args:
        model: Model name
        provider: Provider name
        messages: Input messages
        usage: Token usage
        duration_ms: Call duration
        response: Response content
        cost: Calculated cost
        error: Error message if failed
        params: Request parameters
        user_id: User identifier
        session_id: Session identifier
        metadata: Additional metadata

    Returns:
        str: Call ID for this LLM call
    """
    call_id = str(uuid.uuid4())
    monitor = get_kafka_llm_monitor()

    # Send start event
    monitor.track_llm_start(
        call_id=call_id,
        model=model,
        provider=provider,
        messages=messages,
        params=params,
        user_id=user_id,
        session_id=session_id,
        metadata=metadata,
    )

    # Send end event
    monitor.track_llm_end(
        call_id=call_id,
        model=model,
        provider=provider,
        duration_ms=duration_ms,
        usage=usage,
        response=response,
        cost=cost,
        error=error,
        user_id=user_id,
        session_id=session_id,
        metadata=metadata,
    )

    return call_id


def initialize(
    cost_rates: Optional[dict] = None,
    experiment_name: Optional[str] = None,
    credential: Optional[ModelhubCredential] = None,
):
    """
    Initialize the MLflowClient, Observability, and CostTracker.
    Must be called once at startup.

    Args:
        cost_rates (dict, optional): Dictionary of cost rates for different models
        experiment_name (str, optional): Name of the MLflow experiment
        credential (ModelhubCredential, optional): Modelhub credentials
    """
    global _mlflow_client, _cost_tracker, _initialized

    # Check if already initialized
    if _initialized:
        logger.debug("Observability system already initialized, skipping.")
        return

    # Check if MLFLOW_TRACKING_URI is set in environment
    mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI")

    if mlflow_tracking_uri:
        # Use mlflow directly since tracking URI is already set
        logger.debug("Using MLflow directly with tracking URI: %s", mlflow_tracking_uri)
        _mlflow_client = None
    else:
        if not credential:
            # Create a ModelhubCredential instance using environment variables.
            credential = ModelhubCredential(
                modelhub_url=os.getenv("MODELHUB_URI"),
                client_id=os.getenv("MODELHUB_AUTH_CLIENT_ID"),
                client_secret=os.getenv("MODELHUB_AUTH_CLIENT_SECRET"),
            )

        _mlflow_client = MLflowClient(
            credential=credential,
        )

    experiment_name = experiment_name or os.getenv("AUTONOMIZE_EXPERIMENT_NAME")
    if experiment_name:
        if _mlflow_client:
            _mlflow_client.set_experiment(experiment_name=experiment_name)
        else:
            mlflow.set_experiment(experiment_name)
    _cost_tracker = CostTracker(cost_rates=cost_rates)

    # Mark as initialized
    _initialized = True
    logger.debug("Observability system initialized.")


def monitor(
    client,
    provider: Optional[str] = None,
    cost_rates: Optional[dict] = None,
    experiment_name: Optional[str] = None,
    credential: Optional[ModelhubCredential] = None,
    # NEW PARAMETER
    use_async: bool = True,  # Default to async non-blocking monitoring
):
    """
    Enable monitoring on an LLM client.
    Supports multiple providers: 'openai', 'azure_openai', 'anthropic', etc.
    If provider is not provided, it is inferred from the client's module.

    Args:
        client: The LLM client to monitor
        provider (str, optional): The provider name (openai, azure_openai, anthropic)
        cost_rates (dict, optional): Dictionary of cost rates for different models
        experiment_name (str, optional): Name of the MLflow experiment
        credential (ModelhubCredential, optional): Modelhub credentials
        use_async (bool, optional): Use async non-blocking monitoring (default: True)
    """
    # ALWAYS initialize first - this sets up MLflow client and cost tracker
    # But only if not already initialized
    initialize(
        cost_rates=cost_rates,
        experiment_name=experiment_name,
        credential=credential,
    )

    # Check if we should use async monitoring
    if use_async:
        return _monitor_async(client, provider, cost_rates, experiment_name, credential)

    # Original synchronous monitoring code (initialize already called above)
    if provider is None:
        # Try checking the class name first.
        client_name = client.__class__.__name__.lower()
        if "azure" in client_name:
            provider = "azure_openai"
        elif "openai" in client_name:
            provider = "openai"
        elif "anthropic" in client_name:
            provider = "anthropic"
        else:
            # Fallback to module-based detection.
            mod = client.__class__.__module__.lower()
            if "openai" in mod:
                provider = "openai"
            elif "azure" in mod:
                provider = "azure_openai"
            elif "anthropic" in mod:
                provider = "anthropic"
            else:
                provider = "unknown"

    logger.debug("Detected provider: %s", provider)

    if provider in ("openai", "azure_openai"):
        if _mlflow_client:
            _mlflow_client.mlflow.openai.autolog()
        else:
            mlflow.openai.autolog()
        wrap_openai(client)
    elif provider == "anthropic":
        if _mlflow_client:
            _mlflow_client.mlflow.anthropic.autolog()
        else:
            mlflow.anthropic.autolog()
        wrap_anthropic(client)
    else:
        logger.warning("Monitoring not implemented for provider %s", provider)


# NEW FUNCTION: Async monitoring
def _monitor_async(
    client,
    provider: Optional[str] = None,
    cost_rates: Optional[dict] = None,
    experiment_name: Optional[str] = None,
    credential: Optional[Any] = None,
):
    """
    Enable async non-blocking monitoring on an LLM client.
    Uses Kafka-based monitoring when AUTONOMIZE_TRACING_ENABLED=true,
    otherwise falls back to legacy AsyncMonitor.
    """
    # Check if Kafka-based monitoring is enabled
    use_kafka = os.getenv("AUTONOMIZE_TRACING_ENABLED", "false").lower() == "true"

    if use_kafka:
        logger.info("Using Kafka-based LLM monitoring")
        return _monitor_with_kafka(
            client, provider, cost_rates, experiment_name, credential
        )
    else:
        logger.info("Using legacy AsyncMonitor for LLM monitoring")
        return _monitor_with_async_monitor(
            client, provider, cost_rates, experiment_name, credential
        )


def _monitor_with_kafka(
    client,
    provider: Optional[str] = None,
    cost_rates: Optional[dict] = None,
    experiment_name: Optional[str] = None,
    credential: Optional[Any] = None,
):
    """
    Enable Kafka-based monitoring on an LLM client.
    """
    # Auto-detect provider
    if provider is None:
        client_module = client.__class__.__module__.lower()
        client_name = client.__class__.__name__.lower()

        if "openai" in client_module or "openai" in client_name:
            provider = "openai"
        elif "anthropic" in client_module or "anthropic" in client_name:
            provider = "anthropic"
        else:
            logger.warning(f"Unknown provider for client {client.__class__.__name__}")
            return client

    # Initialize Kafka LLM monitor
    kafka_monitor = get_kafka_llm_monitor()

    if not kafka_monitor.enabled:
        logger.warning(
            "Kafka LLM monitoring not available, falling back to AsyncMonitor"
        )
        return _monitor_with_async_monitor(
            client, provider, cost_rates, experiment_name, credential
        )

    # Wrap the client with Kafka-based monitoring
    if provider == "openai":
        _wrap_openai_with_kafka(client, kafka_monitor, _cost_tracker)
    elif provider == "anthropic":
        _wrap_anthropic_with_kafka(client, kafka_monitor, _cost_tracker)
    else:
        logger.warning(f"Kafka monitoring not implemented for provider {provider}")
        return client

    logger.debug(f"Kafka-based monitoring enabled for {provider} client")
    return client


def _monitor_with_async_monitor(
    client,
    provider: Optional[str] = None,
    cost_rates: Optional[dict] = None,
    experiment_name: Optional[str] = None,
    credential: Optional[Any] = None,
):
    """
    Enable legacy AsyncMonitor-based monitoring on an LLM client.
    """
    # Auto-detect provider
    if provider is None:
        client_module = client.__class__.__module__.lower()
        client_name = client.__class__.__name__.lower()

        if "openai" in client_module or "openai" in client_name:
            provider = "openai"
        elif "anthropic" in client_module or "anthropic" in client_name:
            provider = "anthropic"
        else:
            logger.warning(f"Unknown provider for client {client.__class__.__name__}")
            return client

    # DON'T enable autolog for async monitoring - our custom wrappers handle everything
    # This prevents duplicate runs from being created
    logger.debug(
        "Skipping MLflow autolog for async monitoring - custom wrappers handle all logging"
    )

    # Initialize async monitor if needed (but don't duplicate main initialization)
    if not async_monitor._initialized:
        # Run initialization in background
        loop = None
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No event loop, create one for initialization
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            # Schedule initialization
            asyncio.create_task(
                initialize_async(cost_rates=cost_rates, experiment_name=experiment_name)
            )
        else:
            # Run initialization
            loop.run_until_complete(
                initialize_async(cost_rates=cost_rates, experiment_name=experiment_name)
            )

    # Detect if client is async
    is_async_client = any(
        asyncio.iscoroutinefunction(getattr(client, method, None))
        for method in ["create", "acreate", "__call__"]
    )

    # Wrap based on provider and sync/async - but with separate runs
    if provider == "openai":
        if is_async_client or "async" in client.__class__.__name__.lower():
            _wrap_openai_async_with_separate_runs(client, _cost_tracker, _mlflow_client)
        else:
            _wrap_openai_sync_with_separate_runs(client, _cost_tracker, _mlflow_client)

    elif provider == "anthropic":
        if is_async_client or "async" in client.__class__.__name__.lower():
            _wrap_anthropic_async_with_separate_runs(
                client, _cost_tracker, _mlflow_client
            )
        else:
            _wrap_anthropic_sync_with_separate_runs(
                client, _cost_tracker, _mlflow_client
            )

    logger.debug(f"Non-blocking monitoring enabled for {provider} client")
    return client


def _wrap_openai_with_kafka(client, kafka_monitor, cost_tracker):
    """
    Wrap OpenAI client with Kafka-based monitoring.
    """
    if (
        hasattr(client, "chat")
        and hasattr(client.chat, "completions")
        and hasattr(client.chat.completions, "create")
    ):
        original_create = client.chat.completions.create

        # Robust async client detection
        is_async_client = _is_async_client(client)

        if is_async_client:
            # Async OpenAI client (AsyncOpenAI or AsyncAzureOpenAI)
            async def wrapped_async_create(*args, **kwargs):
                call_id = str(uuid.uuid4())
                model = kwargs.get("model", "gpt-3.5-turbo")
                messages = kwargs.get("messages", [])

                # Extract user context if available
                user_id = getattr(_local, "user_id", None)
                session_id = getattr(_local, "session_id", None)

                # Track start
                start_time = time.time()
                kafka_monitor.track_llm_start(
                    call_id=call_id,
                    model=model,
                    provider="openai",
                    messages=messages,
                    params={
                        k: v
                        for k, v in kwargs.items()
                        if k not in ["messages", "model"]
                    },
                    user_id=user_id,
                    session_id=session_id,
                )

                error = None
                try:
                    result = await original_create(*args, **kwargs)

                    # Calculate cost
                    usage = {
                        "prompt_tokens": result.usage.prompt_tokens,
                        "completion_tokens": result.usage.completion_tokens,
                        "total_tokens": result.usage.total_tokens,
                    }

                    cost = cost_tracker.track_cost(
                        model_name=model,
                        input_tokens=usage["prompt_tokens"],
                        output_tokens=usage["completion_tokens"],
                    )

                    response = (
                        result.choices[0].message.content if result.choices else None
                    )

                    # Track end
                    duration_ms = (time.time() - start_time) * 1000
                    kafka_monitor.track_llm_end(
                        call_id=call_id,
                        model=model,
                        provider="openai",
                        duration_ms=duration_ms,
                        usage=usage,
                        response=response,
                        cost=cost,
                        user_id=user_id,
                        session_id=session_id,
                    )

                    return result

                except Exception as e:
                    error = str(e)
                    duration_ms = (time.time() - start_time) * 1000
                    kafka_monitor.track_llm_end(
                        call_id=call_id,
                        model=model,
                        provider="openai",
                        duration_ms=duration_ms,
                        usage={
                            "prompt_tokens": 0,
                            "completion_tokens": 0,
                            "total_tokens": 0,
                        },
                        error=error,
                        user_id=user_id,
                        session_id=session_id,
                    )
                    raise

            client.chat.completions.create = wrapped_async_create

        else:
            # Sync OpenAI client
            def wrapped_create(*args, **kwargs):
                call_id = str(uuid.uuid4())
                model = kwargs.get("model", "gpt-3.5-turbo")
                messages = kwargs.get("messages", [])

                # Extract user context if available
                user_id = getattr(_local, "user_id", None)
                session_id = getattr(_local, "session_id", None)

                # Track start
                start_time = time.time()
                kafka_monitor.track_llm_start(
                    call_id=call_id,
                    model=model,
                    provider="openai",
                    messages=messages,
                    params={
                        k: v
                        for k, v in kwargs.items()
                        if k not in ["messages", "model"]
                    },
                    user_id=user_id,
                    session_id=session_id,
                )

                error = None
                try:
                    result = original_create(*args, **kwargs)

                    # Calculate cost
                    usage = {
                        "prompt_tokens": result.usage.prompt_tokens,
                        "completion_tokens": result.usage.completion_tokens,
                        "total_tokens": result.usage.total_tokens,
                    }

                    cost = cost_tracker.track_cost(
                        model_name=model,
                        input_tokens=usage["prompt_tokens"],
                        output_tokens=usage["completion_tokens"],
                    )

                    response = (
                        result.choices[0].message.content if result.choices else None
                    )

                    # Track end
                    duration_ms = (time.time() - start_time) * 1000
                    kafka_monitor.track_llm_end(
                        call_id=call_id,
                        model=model,
                        provider="openai",
                        duration_ms=duration_ms,
                        usage=usage,
                        response=response,
                        cost=cost,
                        user_id=user_id,
                        session_id=session_id,
                    )

                    return result

                except Exception as e:
                    error = str(e)
                    duration_ms = (time.time() - start_time) * 1000
                    kafka_monitor.track_llm_end(
                        call_id=call_id,
                        model=model,
                        provider="openai",
                        duration_ms=duration_ms,
                        usage={
                            "prompt_tokens": 0,
                            "completion_tokens": 0,
                            "total_tokens": 0,
                        },
                        error=error,
                        user_id=user_id,
                        session_id=session_id,
                    )
                    raise

            client.chat.completions.create = wrapped_create

    logger.debug("Kafka monitoring enabled for OpenAI client")


def _wrap_anthropic_with_kafka(client, kafka_monitor, cost_tracker):
    """
    Wrap Anthropic client with Kafka-based monitoring.
    """
    # Robust async client detection
    is_async_client = _is_async_client(client)

    # Wrap synchronous messages.create
    if hasattr(client, "messages") and hasattr(client.messages, "create"):
        original_create = client.messages.create

        def wrapped_create(*args, **kwargs):
            call_id = str(uuid.uuid4())
            model = kwargs.get("model", "claude-3-5-sonnet")
            messages = kwargs.get("messages", [])

            # Extract user context if available
            user_id = getattr(_local, "user_id", None)
            session_id = getattr(_local, "session_id", None)

            # Track start
            start_time = time.time()
            kafka_monitor.track_llm_start(
                call_id=call_id,
                model=model,
                provider="anthropic",
                messages=messages,
                params={
                    k: v for k, v in kwargs.items() if k not in ["messages", "model"]
                },
                user_id=user_id,
                session_id=session_id,
            )

            error = None
            try:
                result = original_create(*args, **kwargs)

                # Calculate cost
                usage = {
                    "prompt_tokens": result.usage.input_tokens,
                    "completion_tokens": result.usage.output_tokens,
                    "total_tokens": result.usage.input_tokens
                    + result.usage.output_tokens,
                }

                cost = cost_tracker.track_cost(
                    model_name=model,
                    input_tokens=usage["prompt_tokens"],
                    output_tokens=usage["completion_tokens"],
                )

                response = result.content[0].text if result.content else None

                # Track end
                duration_ms = (time.time() - start_time) * 1000
                kafka_monitor.track_llm_end(
                    call_id=call_id,
                    model=model,
                    provider="anthropic",
                    duration_ms=duration_ms,
                    usage=usage,
                    response=response,
                    cost=cost,
                    user_id=user_id,
                    session_id=session_id,
                )

                return result

            except Exception as e:
                error = str(e)
                duration_ms = (time.time() - start_time) * 1000
                kafka_monitor.track_llm_end(
                    call_id=call_id,
                    model=model,
                    provider="anthropic",
                    duration_ms=duration_ms,
                    usage={
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0,
                    },
                    error=error,
                    user_id=user_id,
                    session_id=session_id,
                )
                raise

        client.messages.create = wrapped_create

    # Wrap asynchronous messages.acreate if available
    if is_async_client:
        original_acreate = client.messages.acreate

        async def wrapped_acreate(*args, **kwargs):
            call_id = str(uuid.uuid4())
            model = kwargs.get("model", "claude-3-5-sonnet")
            messages = kwargs.get("messages", [])

            # Extract user context if available
            user_id = getattr(_local, "user_id", None)
            session_id = getattr(_local, "session_id", None)

            # Track start
            start_time = time.time()
            kafka_monitor.track_llm_start(
                call_id=call_id,
                model=model,
                provider="anthropic",
                messages=messages,
                params={
                    k: v for k, v in kwargs.items() if k not in ["messages", "model"]
                },
                user_id=user_id,
                session_id=session_id,
            )

            error = None
            try:
                result = await original_acreate(*args, **kwargs)

                # Calculate cost
                usage = {
                    "prompt_tokens": result.usage.input_tokens,
                    "completion_tokens": result.usage.output_tokens,
                    "total_tokens": result.usage.input_tokens
                    + result.usage.output_tokens,
                }

                cost = cost_tracker.track_cost(
                    model_name=model,
                    input_tokens=usage["prompt_tokens"],
                    output_tokens=usage["completion_tokens"],
                )

                response = result.content[0].text if result.content else None

                # Track end
                duration_ms = (time.time() - start_time) * 1000
                kafka_monitor.track_llm_end(
                    call_id=call_id,
                    model=model,
                    provider="anthropic",
                    duration_ms=duration_ms,
                    usage=usage,
                    response=response,
                    cost=cost,
                    user_id=user_id,
                    session_id=session_id,
                )

                return result

            except Exception as e:
                error = str(e)
                duration_ms = (time.time() - start_time) * 1000
                kafka_monitor.track_llm_end(
                    call_id=call_id,
                    model=model,
                    provider="anthropic",
                    duration_ms=duration_ms,
                    usage={
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0,
                    },
                    error=error,
                    user_id=user_id,
                    session_id=session_id,
                )
                raise

        client.messages.acreate = wrapped_acreate

    logger.debug("Kafka monitoring enabled for Anthropic client")


# NEW DECORATORS
def trace_async(name: Optional[str] = None):
    """Decorator for async functions with non-blocking tracing."""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = name or func.__name__

            # Track start without blocking
            asyncio.create_task(
                async_monitor.track_component_start(
                    name=func_name, component_type="function"
                )
            )

            error = None
            result = None

            try:
                result = await func(*args, **kwargs)
                return result

            except Exception as e:
                error = e
                raise

            finally:
                duration_ms = (time.time() - start_time) * 1000

                # Track end without blocking
                asyncio.create_task(
                    async_monitor.track_component_end(
                        name=func_name,
                        duration_ms=duration_ms,
                        error=str(error) if error else None,
                        outputs={"result": str(result)[:100]} if result else None,
                    )
                )

        return wrapper

    return decorator


def trace_sync(name: Optional[str] = None):
    """Decorator for sync functions with non-blocking tracing."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = name or func.__name__

            # Track start without blocking
            async_monitor.track_sync(
                {
                    "type": "component_start",
                    "name": func_name,
                    "component_type": "function",
                }
            )

            error = None
            result = None

            try:
                result = func(*args, **kwargs)
                return result

            except Exception as e:
                error = e
                raise

            finally:
                duration_ms = (time.time() - start_time) * 1000

                # Track end without blocking
                async_monitor.track_sync(
                    {
                        "type": "component_end",
                        "name": func_name,
                        "duration_ms": duration_ms,
                        "error": str(error) if error else None,
                        "outputs": {"result": str(result)[:100]} if result else None,
                    }
                )

        return wrapper

    return decorator


def wrap_openai(client):
    """
    Wraps an OpenAI client to enable monitoring and logging capabilities.

    This function intercepts the client's completion creation methods (both synchronous
    and asynchronous) to track costs, log parameters, and manage MLflow runs.

    Args:
        client: An instance of the OpenAI client to be wrapped.

    Returns:
        None. The function modifies the client instance in-place by wrapping its methods.
    """
    # Wrap synchronous completions.create
    if hasattr(client.chat, "completions") and hasattr(
        client.chat.completions, "create"
    ):
        original_create = client.chat.completions.create

        def wrapped_create(*args, **kwargs):
            active = mlflow.active_run()
            logger.debug("Active run: %s", active)
            started_run = False
            if not active:
                run = mlflow.start_run(run_name="llm_call_auto")
                started_run = True
            else:
                run = active
            try:
                result = original_create(*args, **kwargs)
                logger.debug("result: %s", result)
                prompt_tokens = result.usage.prompt_tokens
                completion_tokens = result.usage.completion_tokens
                _cost_tracker.track_cost(
                    model_name=kwargs.get("model", "gpt-3.5-turbo"),
                    input_tokens=prompt_tokens,
                    output_tokens=completion_tokens,
                    run_id=run.info.run_id,
                )
                if _mlflow_client:
                    _mlflow_client.log_param(
                        "model", kwargs.get("model", "gpt-3.5-turbo")
                    )
                else:
                    mlflow.log_param("model", kwargs.get("model", "gpt-3.5-turbo"))
                return result
            finally:
                if started_run:
                    mlflow.end_run()

        client.chat.completions.create = wrapped_create

    # Wrap asynchronous completions.create (create)
    if hasattr(client, "chat") and hasattr(client.chat, "completions"):
        # Check if the client is an AsyncOpenAI instance
        if (
            hasattr(client.chat.completions, "create")
            and callable(client.chat.completions.create)
            and client.__class__.__name__ == "AsyncOpenAI"
        ):
            original_async_create = client.chat.completions.create

            async def wrapped_async_create(*args, **kwargs):
                active = mlflow.active_run()
                logger.debug("Active async run: %s", active)
                started_run = False
                if not active:
                    run = mlflow.start_run(run_name="async_llm_call_auto")
                    started_run = True
                else:
                    run = active

                try:
                    result = original_async_create(*args, **kwargs)
                    prompt_tokens = result.usage.prompt_tokens
                    completion_tokens = result.usage.completion_tokens
                    _cost_tracker.track_cost(
                        model_name=kwargs.get("model", "gpt-3.5-turbo"),
                        input_tokens=prompt_tokens,
                        output_tokens=completion_tokens,
                        run_id=run.info.run_id,
                    )
                    if _mlflow_client:
                        _mlflow_client.log_param(
                            "model", kwargs.get("model", "gpt-3.5-turbo")
                        )
                    else:
                        mlflow.log_param("model", kwargs.get("model", "gpt-3.5-turbo"))
                    return result
                finally:
                    if started_run:
                        mlflow.end_run()

            client.chat.completions.create = wrapped_async_create

    logger.debug("Monitoring enabled for OpenAI/AzureOpenAI client.")


def wrap_anthropic(client):
    """
    Wraps an Anthropic client to enable monitoring and logging capabilities.

    This function intercepts the client's message creation methods (both synchronous
    and asynchronous) to track costs, log parameters, and manage MLflow runs.

    Args:
        client: An instance of the Anthropic client to be wrapped.

    Returns:
        None. The function modifies the client instance in-place by wrapping its methods.
    """
    # Wrap synchronous messages.create.
    if hasattr(client, "messages") and hasattr(client.messages, "create"):
        original_create = client.messages.create

        def wrapped_create(*args, **kwargs):
            active = mlflow.active_run()
            started_run = False
            if not active:
                run = mlflow.start_run(run_name="llm_call_auto")
                started_run = True
            else:
                run = active
            try:
                result = original_create(*args, **kwargs)
                prompt_tokens = result.usage.input_tokens
                completion_tokens = result.usage.output_tokens
                _cost_tracker.track_cost(
                    model_name=kwargs.get("model", "anthropic-default"),
                    input_tokens=prompt_tokens,
                    output_tokens=completion_tokens,
                    run_id=run.info.run_id,
                )
                if _mlflow_client:
                    _mlflow_client.log_param(
                        "model", kwargs.get("model", "anthropic-default")
                    )
                else:
                    mlflow.log_param("model", kwargs.get("model", "anthropic-default"))
                return result
            finally:
                if started_run:
                    mlflow.end_run()

        client.messages.create = wrapped_create

    # Wrap asynchronous messages.acreate if available.
    if hasattr(client, "messages") and hasattr(client.messages, "acreate"):
        original_acreate = client.messages.acreate

        async def wrapped_acreate(*args, **kwargs):
            active = mlflow.active_run()
            started_run = False
            if not active:
                run = mlflow.start_run(run_name="llm_call_auto")
                started_run = True
            else:
                run = active
            try:
                result = await original_acreate(*args, **kwargs)
                prompt_tokens = result.usage.input_tokens
                completion_tokens = result.usage.output_tokens
                _cost_tracker.track_cost(
                    model_name=kwargs.get("model", "anthropic-default"),
                    input_tokens=prompt_tokens,
                    output_tokens=completion_tokens,
                    run_id=run.info.run_id,
                )
                if _mlflow_client:
                    _mlflow_client.log_param(
                        "model", kwargs.get("model", "anthropic-default")
                    )
                else:
                    mlflow.log_param("model", kwargs.get("model", "anthropic-default"))
                return result
            finally:
                if started_run:
                    mlflow.end_run()

        client.messages.acreate = wrapped_acreate

    logger.debug("Monitoring enabled for Anthropics client.")


def agent(name=None):
    """
    Decorator for agent functions.
    Automatically wraps the function execution in an MLflow run.
    """

    def decorator(fn):
        def wrapper(*args, **kwargs):
            active = mlflow.active_run()
            started_run = False
            if not active:
                mlflow.start_run(run_name=name or fn.__name__)
                started_run = True
            else:
                run = active
            try:
                return fn(*args, **kwargs)
            finally:
                if started_run:
                    mlflow.end_run()

        return wrapper

    return decorator


def tool(name=None):
    """
    Decorator for tool functions.
    """

    def decorator(fn):
        def wrapper(*args, **kwargs):
            active = mlflow.active_run()
            started_run = False
            if not active:
                run = mlflow.start_run(run_name=name or fn.__name__)
                started_run = True
            else:
                run = active
            try:
                return fn(*args, **kwargs)
            finally:
                if started_run:
                    mlflow.end_run()

        return wrapper

    return decorator


class Identify:
    """
    A simple context manager for setting user context (if needed).
    """

    def __init__(self, user_props=None):
        self.user_props = user_props

    def __enter__(self):
        # Set user context here if desired.
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clear user context.
        pass


def identify(user_props=None):
    """
    Creates and returns an Identify context manager for setting user context.

    Args:
        user_props (dict, optional): Dictionary containing user properties to be set
            during the context. Defaults to None.

    Returns:
        Identify: A context manager instance that handles user context.
    """
    return Identify(user_props)


def _is_async_client(client):
    """
    Robust detection of async LLM clients across different providers.

    Combines multiple detection methods:
    1. Check class name for known async patterns
    2. Check for async methods (with fallbacks for OpenAI's pattern)
    3. Module-based detection as backup
    """
    client_class_name = client.__class__.__name__
    client_module = client.__class__.__module__.lower()

    # Method 1: Known async class name patterns
    async_class_patterns = {
        # OpenAI patterns
        "AsyncOpenAI",
        "AsyncAzureOpenAI",  # Note: NOT AzureAsyncOpenAI
        # Anthropic patterns
        "AsyncAnthropic",
        # Other potential patterns
        "AsyncClient",
    }

    if client_class_name in async_class_patterns:
        return True

    # Method 2: Check if "async" is in the class name (case insensitive)
    if "async" in client_class_name.lower():
        return True

    # Method 3: Check for async methods (with OpenAI compatibility)
    # Note: OpenAI's async clients return coroutines from regular methods,
    # so we need to check multiple method patterns
    async_method_names = ["create", "acreate", "__call__", "stream", "astream"]

    for method_name in async_method_names:
        method = getattr(client, method_name, None)
        if method and asyncio.iscoroutinefunction(method):
            return True

    # Method 4: For OpenAI specifically, check if methods return coroutines
    # when called (this is how OpenAI async clients work)
    if "openai" in client_module or "openai" in client_class_name.lower():
        # Try to detect OpenAI async pattern by checking nested methods
        if hasattr(client, "chat") and hasattr(client.chat, "completions"):
            create_method = getattr(client.chat.completions, "create", None)
            if create_method:
                # For OpenAI, async clients have class names that include "Async"
                # but methods that return coroutines, not actual async methods
                if "async" in client_class_name.lower():
                    return True

    # Method 5: Check module patterns as fallback
    async_module_patterns = ["async", "aio"]
    if any(pattern in client_module for pattern in async_module_patterns):
        return True

    return False
