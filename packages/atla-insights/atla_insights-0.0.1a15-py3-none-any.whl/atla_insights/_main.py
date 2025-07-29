"""Core functionality for the atla_insights package."""

import importlib
import json
import logging
import os
from contextlib import contextmanager
from typing import (
    ContextManager,
    Literal,
    Optional,
    Sequence,
    Union,
)

import logfire
import opentelemetry.trace
from opentelemetry import trace
from opentelemetry.instrumentation.instrumentor import (  # type: ignore[attr-defined]
    BaseInstrumentor,
)
from opentelemetry.sdk.environment_variables import OTEL_ATTRIBUTE_COUNT_LIMIT
from opentelemetry.sdk.trace import SpanProcessor, TracerProvider

from ._constants import (
    DEFAULT_OTEL_ATTRIBUTE_COUNT_LIMIT,
    METADATA_MARK,
    SUCCESS_MARK,
    SUPPORTED_LLM_PROVIDER,
)
from ._span_processors import (
    AtlaRootSpanProcessor,
    _metadata,
    _root_span,
    get_atla_span_processor,
)
from ._utils import validate_metadata

logger = logging.getLogger("atla_insights")


# Override the OTEL default attribute count limit (128), if not user-specified. This is
# because we use separate attributes to store e.g. message history, available tools, etc.
# see: https://opentelemetry-python.readthedocs.io/en/latest/sdk/environment_variables.html#opentelemetry.sdk.environment_variables.OTEL_ATTRIBUTE_COUNT_LIMIT
if os.environ.get(OTEL_ATTRIBUTE_COUNT_LIMIT) is None:
    os.environ[OTEL_ATTRIBUTE_COUNT_LIMIT] = str(DEFAULT_OTEL_ATTRIBUTE_COUNT_LIMIT)


class AtlaInsights:
    """Atla insights."""

    def __init__(self) -> None:
        """Initialize Atla insights."""
        self._active_instrumentors: dict[str, Sequence[BaseInstrumentor]] = {}
        self.configured = False

    def configure(
        self,
        token: str,
        metadata: Optional[dict[str, str]] = None,
        additional_span_processors: Optional[Sequence[SpanProcessor]] = None,
        verbose: bool = True,
    ) -> None:
        """Configure Atla insights.

        :param token (str): The write access token.
        :param metadata (Optional[dict[str, str]]): A dictionary of metadata to be added
            to the trace.
        :param additional_span_processors (Optional[Sequence[SpanProcessor]]): Additional
            span processors. Defaults to `None`.
        :param verbose (bool): Whether to print verbose output to console.
            Defaults to `True`.
        """
        self._maybe_reset_tracer_provider()

        validate_metadata(metadata)
        _metadata.set(metadata)

        additional_span_processors = additional_span_processors or []
        span_processors = [
            get_atla_span_processor(token),
            AtlaRootSpanProcessor(),
            *additional_span_processors,
        ]

        self.logfire_instance = logfire.configure(
            additional_span_processors=span_processors,
            console=None if verbose else False,
            environment=os.getenv("_ATLA_ENV", "prod"),
            send_to_logfire=False,
            scrubbing=False,
        )
        self.configured = True

        logger.info("Atla insights configured correctly ✅")

    def _maybe_reset_tracer_provider(self) -> None:
        """Reset the existing OpenTelemetry tracer provider, if one exists.

        Removes any existing tracer provider to allow the Atla tracer provider to get
        initialized correctly. OpenTelemetry tracer providers cannot be re-initialized, so
        we need to reload the module.
        """
        if isinstance(trace.get_tracer_provider(), TracerProvider):
            importlib.reload(opentelemetry.trace)

    def _mark_root_span(self, value: Literal[0, 1]) -> None:
        """Mark the root span in the current trace with a value."""
        if not self.configured:
            raise ValueError(
                "Cannot mark trace before running the atla `configure` method."
            )
        root_span = _root_span.get()
        if root_span is None:
            raise ValueError(
                "Atla marking can only be done within an instrumented function."
            )
        root_span.set_attribute(SUCCESS_MARK, value)

    def mark_success(self) -> None:
        """Mark the root span in the current trace as successful."""
        self._mark_root_span(1)
        logger.info("Marked trace as success ✅")

    def mark_failure(self) -> None:
        """Mark the root span in the current trace as failed."""
        self._mark_root_span(0)
        logger.info("Marked trace as failure ❌")

    def get_metadata(self) -> Optional[dict[str, str]]:
        """Get the metadata for the current trace."""
        return _metadata.get()

    def set_metadata(self, metadata: dict[str, str]) -> None:
        """Set the metadata for the current trace."""
        validate_metadata(metadata)

        _metadata.set(metadata)
        if root_span := _root_span.get():
            # If the root span already exists, we can assign the metadata to it.
            # If not, it will be assigned the `_metadata` context var on creation.
            root_span.set_attribute(METADATA_MARK, json.dumps(metadata))

    def _instrument_provider(
        self, provider: str, instrumentors: Sequence[BaseInstrumentor]
    ) -> ContextManager[None]:
        if provider in self._active_instrumentors:
            logger.warning(f"Attempting to instrument already instrumented {provider}")
            self._uninstrument_provider(provider)

        for instrumentor in instrumentors:
            instrumentor.instrument()

        self._active_instrumentors[provider] = instrumentors

        @contextmanager
        def instrumented_context():
            try:
                yield
            finally:
                self._uninstrument_provider(provider)

        return instrumented_context()

    def _uninstrument_provider(self, provider: str) -> None:
        if provider not in self._active_instrumentors.keys():
            logger.warning(
                f"Attempting to uninstrument {provider} which was not instrumented."
            )
            return

        instrumentors = self._active_instrumentors.pop(provider)
        for instrumentor in instrumentors:
            instrumentor.uninstrument()

    def instrument_anthropic(self) -> ContextManager[None]:
        """Instrument Anthropic."""
        try:
            from openinference.instrumentation.anthropic import AnthropicInstrumentor
        except ImportError as e:
            raise ImportError(
                "Anthropic instrumentation needs to be installed. "
                "Please install it via `pip install atla-insights[anthropic]`."
            ) from e

        return self._instrument_provider(
            provider="anthropic",
            instrumentors=[AnthropicInstrumentor()],
        )

    def uninstrument_anthropic(self) -> None:
        """Uninstrument Anthropic."""
        return self._uninstrument_provider("anthropic")

    def instrument_google_genai(self) -> ContextManager[None]:
        """Instrument Google GenAI."""
        from ._google_genai import AtlaGoogleGenAIInstrumentor

        return self._instrument_provider(
            provider="google-genai",
            instrumentors=[AtlaGoogleGenAIInstrumentor()],
        )

    def uninstrument_google_genai(self) -> None:
        """Uninstrument Anthropic."""
        return self._uninstrument_provider("google-genai")

    def instrument_openai(self) -> ContextManager[None]:
        """Instrument OpenAI."""
        try:
            from openinference.instrumentation.openai import OpenAIInstrumentor
        except ImportError as e:
            raise ImportError(
                "OpenAI instrumentation needs to be installed. "
                "Please install it via `pip install atla-insights[openai]`."
            ) from e

        return self._instrument_provider(
            provider="openai",
            instrumentors=[OpenAIInstrumentor()],
        )

    def uninstrument_openai(self) -> None:
        """Uninstrument OpenAI."""
        return self._uninstrument_provider("openai")

    def instrument_langchain(self) -> ContextManager[None]:
        """Instrument the Langchain framework."""
        try:
            from openinference.instrumentation.langchain import LangChainInstrumentor
        except ImportError as e:
            raise ImportError(
                "Langchain instrumentation needs to be installed. "
                "Please install it via `pip install atla-insights[langchain]`."
            ) from e

        return self._instrument_provider(
            provider="langchain",
            instrumentors=[LangChainInstrumentor()],
        )

    def uninstrument_langchain(self) -> None:
        """Uninstrument LangChain."""
        return self._uninstrument_provider("langchain")

    def instrument_litellm(self) -> ContextManager[None]:
        """Instrument litellm."""
        from ._litellm import AtlaLiteLLMIntrumentor

        return self._instrument_provider(
            provider="litellm",
            instrumentors=[AtlaLiteLLMIntrumentor()],
        )

    def uninstrument_litellm(self) -> None:
        """Uninstrument LiteLLM."""
        return self._uninstrument_provider("litellm")

    def _get_instrumentors_for_provider(
        self,
        llm_provider: Union[Sequence[SUPPORTED_LLM_PROVIDER], SUPPORTED_LLM_PROVIDER],
    ) -> list[BaseInstrumentor]:
        if isinstance(llm_provider, str):
            llm_provider = [llm_provider]

        instrumentors = []
        for provider in llm_provider:
            match provider:
                case "anthropic":
                    from openinference.instrumentation.anthropic import (
                        AnthropicInstrumentor,
                    )

                    instrumentors.append(AnthropicInstrumentor())
                case "google-genai":
                    from ._google_genai import AtlaGoogleGenAIInstrumentor

                    instrumentors.append(AtlaGoogleGenAIInstrumentor())
                case "litellm":
                    from ._litellm import AtlaLiteLLMIntrumentor

                    instrumentors.append(AtlaLiteLLMIntrumentor())
                case "openai":
                    from openinference.instrumentation.openai import OpenAIInstrumentor

                    instrumentors.append(OpenAIInstrumentor())
                case _:
                    raise ValueError(f"Invalid LLM provider: {provider}")
        return instrumentors

    def instrument_agno(
        self,
        llm_provider: Union[Sequence[SUPPORTED_LLM_PROVIDER], SUPPORTED_LLM_PROVIDER],
    ) -> ContextManager[None]:
        """Instrument the Agno framework.

        :param llm_provider (Union[Sequence[SUPPORTED_LLM_PROVIDER],
            SUPPORTED_LLM_PROVIDER]): The LLM provider(s) to instrument.
        """
        from ._agno import AtlaAgnoInstrumentor

        return self._instrument_provider(
            provider="agno",
            instrumentors=[
                *self._get_instrumentors_for_provider(llm_provider),
                AtlaAgnoInstrumentor(),
            ],
        )

    def uninstrument_agno(self) -> None:
        """Uninstrument Agno."""
        return self._uninstrument_provider("agno")

    def instrument_crewai(self) -> ContextManager[None]:
        """Instrument CrewAI."""
        from ._crewai import AtlaCrewAIInstrumentor
        from ._litellm import AtlaLiteLLMIntrumentor

        tracer = self.logfire_instance._get_tracer(is_span_tracer=True)
        return self._instrument_provider(
            provider="crewai",
            instrumentors=[
                AtlaLiteLLMIntrumentor(),
                AtlaCrewAIInstrumentor(tracer=tracer),
            ],
        )

    def uninstrument_crewai(self) -> None:
        """Uninstrument CrewAI."""
        return self._uninstrument_provider("crewai")

    def instrument_openai_agents(
        self,
        llm_provider: Union[
            Sequence[SUPPORTED_LLM_PROVIDER], SUPPORTED_LLM_PROVIDER
        ] = "openai",
    ) -> ContextManager[None]:
        """Instrument OpenAI agents.

        :param llm_provider (Union[Sequence[SUPPORTED_LLM_PROVIDER],
            SUPPORTED_LLM_PROVIDER]): The LLM provider(s) to instrument.
            Defaults to "openai".
        """
        from ._openai_agents import AtlaOpenAIAgentsInstrumentor

        return self._instrument_provider(
            provider="openai-agents",
            instrumentors=[
                *self._get_instrumentors_for_provider(llm_provider),
                AtlaOpenAIAgentsInstrumentor(),
            ],
        )

    def uninstrument_openai_agents(self) -> None:
        """Uninstrument OpenAI Agents."""
        return self._uninstrument_provider("openai-agents")

    def instrument_mcp(self) -> ContextManager[None]:
        """Instrument MCP."""
        try:
            from openinference.instrumentation.mcp import MCPInstrumentor
        except ImportError as e:
            raise ImportError(
                "MCP instrumentation needs to be installed. "
                "Please install it via `pip install atla-insights[mcp]`."
            ) from e

        return self._instrument_provider(
            provider="mcp",
            instrumentors=[MCPInstrumentor()],
        )

    def uninstrument_mcp(self) -> None:
        """Uninstrument MCP."""
        return self._uninstrument_provider("mcp")

    def instrument_smolagents(
        self,
        llm_provider: Union[Sequence[SUPPORTED_LLM_PROVIDER], SUPPORTED_LLM_PROVIDER],
    ) -> ContextManager[None]:
        """Instrument the HuggingFace Smolagents framework.

        :param llm_provider (Union[Sequence[SUPPORTED_LLM_PROVIDER],
            SUPPORTED_LLM_PROVIDER]): The LLM provider(s) to instrument.
        """
        try:
            from openinference.instrumentation.smolagents import SmolagentsInstrumentor
        except ImportError as e:
            raise ImportError(
                "Smolagents instrumentation needs to be installed. "
                "Please install it via `pip install atla-insights[smolagents]`."
            ) from e

        return self._instrument_provider(
            provider="smolagents",
            instrumentors=[
                *self._get_instrumentors_for_provider(llm_provider),
                SmolagentsInstrumentor(),
            ],
        )

    def uninstrument_smolagents(self) -> None:
        """Uninstrument smolagents."""
        return self._uninstrument_provider("smolagents")


_ATLA = AtlaInsights()

configure = _ATLA.configure

get_metadata = _ATLA.get_metadata
set_metadata = _ATLA.set_metadata

mark_success = _ATLA.mark_success
mark_failure = _ATLA.mark_failure

instrument_agno = _ATLA.instrument_agno
uninstrument_agno = _ATLA.uninstrument_agno

instrument_anthropic = _ATLA.instrument_anthropic
uninstrument_anthropic = _ATLA.uninstrument_anthropic

instrument_crewai = _ATLA.instrument_crewai
uninstrument_crewai = _ATLA.uninstrument_crewai

instrument_google_genai = _ATLA.instrument_google_genai
uninstrument_google_genai = _ATLA.uninstrument_google_genai

instrument_langchain = _ATLA.instrument_langchain
uninstrument_langchain = _ATLA.uninstrument_langchain

instrument_litellm = _ATLA.instrument_litellm
uninstrument_litellm = _ATLA.uninstrument_litellm

instrument_mcp = _ATLA.instrument_mcp
uninstrument_mcp = _ATLA.uninstrument_mcp

instrument_openai = _ATLA.instrument_openai
uninstrument_openai = _ATLA.uninstrument_openai

instrument_openai_agents = _ATLA.instrument_openai_agents
uninstrument_openai_agents = _ATLA.uninstrument_openai_agents

instrument_smolagents = _ATLA.instrument_smolagents
uninstrument_smolagents = _ATLA.uninstrument_smolagents
