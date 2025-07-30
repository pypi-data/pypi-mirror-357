"""MarkMate Unified LLM Provider Interface.

Provides a unified interface for multiple LLM providers using LiteLLM.
Supports Claude (Anthropic), OpenAI, and Gemini with consistent API.
"""

from __future__ import annotations

import logging
import os
import time
from datetime import datetime
from typing import Any, Optional

try:
    import litellm
    from litellm import completion
    from litellm.cost_calculator import completion_cost

    _litellm_available = True
except ImportError:
    _litellm_available = False
    # Define dummy functions for type checking
    litellm = None  # type: ignore[assignment]
    completion = None  # type: ignore[assignment] 
    completion_cost = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


class LLMProvider:
    """Unified LLM provider using LiteLLM for consistent API across providers."""

    # Supported provider configurations
    PROVIDER_CONFIGS: dict[str, dict[str, str]] = {
        "anthropic": {
            "claude-3-5-sonnet": "claude-3-5-sonnet-20241022",
            "claude-3-sonnet": "claude-3-sonnet-20240229",
            "claude-3-haiku": "claude-3-haiku-20240307",
        },
        "openai": {
            "gpt-4o": "gpt-4o",
            "gpt-4o-mini": "gpt-4o-mini",
            "gpt-4": "gpt-4",
            "gpt-3.5-turbo": "gpt-3.5-turbo",
        },
        "gemini": {
            "gemini-pro": "gemini/gemini-pro",
            "gemini-1.5-pro": "gemini/gemini-1.5-pro-latest",
            "gemini-2.0-flash": "gemini/gemini-2.0-flash",
        },
    }

    def __init__(self) -> None:
        """Initialize the unified LLM provider."""
        if not _litellm_available:
            raise ImportError(
                "LiteLLM is required but not available. Install with: pip install litellm"
            )

        # Configure LiteLLM
        if litellm is not None:
            litellm.set_verbose = False  # Set to True for debugging

        # Token usage tracking
        self.token_usage: dict[str, dict[str, float]] = {
            "anthropic": {"input_tokens": 0, "output_tokens": 0, "cost": 0.0},
            "openai": {"input_tokens": 0, "output_tokens": 0, "cost": 0.0},
            "gemini": {"input_tokens": 0, "output_tokens": 0, "cost": 0.0},
        }

        # Rate limiting tracking
        self.last_request_time: dict[str, float] = {}

        # Validate API keys
        _ = self._validate_api_keys()

    def _validate_api_keys(self) -> dict[str, bool]:
        """Validate which providers have API keys available.
        
        Returns:
            Dictionary mapping provider names to availability status.
        """
        providers_available = {
            "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "gemini": bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")),
        }

        logger.info(
            f"Available providers: {[k for k, v in providers_available.items() if v]}"
        )
        return providers_available

    def get_model_name(self, provider: str, model_short_name: str) -> str:
        """Get the full model name for LiteLLM from provider and short name.
        
        Args:
            provider: Provider name (anthropic, openai, gemini).
            model_short_name: Short model name.
            
        Returns:
            Full model name for LiteLLM.
            
        Raises:
            ValueError: If provider or model is not supported.
        """
        if provider not in self.PROVIDER_CONFIGS:
            raise ValueError(f"Unsupported provider: {provider}")

        if model_short_name not in self.PROVIDER_CONFIGS[provider]:
            raise ValueError(
                f"Unsupported model {model_short_name} for provider {provider}"
            )

        return self.PROVIDER_CONFIGS[provider][model_short_name]

    def _respect_rate_limit(self, provider: str, rate_limit: Optional[int] = None) -> None:
        """Ensure rate limits are respected for the provider.
        
        Args:
            provider: Provider name.
            rate_limit: Requests per minute limit.
        """
        if not rate_limit:
            return

        # Calculate minimum time between requests
        min_interval = 60.0 / rate_limit  # seconds between requests

        current_time = time.time()
        last_time = self.last_request_time.get(provider, 0)

        time_since_last = current_time - last_time
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            logger.debug(f"Rate limiting {provider}: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)

        self.last_request_time[provider] = time.time()

    def grade_submission(
        self,
        provider: str,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2000,
        rate_limit: Optional[int] = None,
        timeout: int = 60,
    ) -> dict[str, Any]:
        """Grade a submission using the specified provider and model.

        Args:
            provider: Provider name (anthropic, openai, gemini).
            model: Model short name (e.g., 'claude-3-5-sonnet', 'gpt-4o', 'gemini-pro').
            prompt: The grading prompt.
            system_prompt: Optional system prompt (for providers that support it).
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in response.
            rate_limit: Requests per minute limit.
            timeout: Request timeout in seconds.

        Returns:
            Dictionary containing response, token usage, and metadata.
        """
        # Respect rate limits
        self._respect_rate_limit(provider, rate_limit)

        # Get full model name for LiteLLM
        full_model_name = self.get_model_name(provider, model)

        # Prepare messages
        messages: list[dict[str, str]] = []
        if system_prompt and provider in ["openai", "anthropic"]:
            messages.append({"role": "system", "content": system_prompt})

        # For providers without system prompt support, prepend to user message
        if system_prompt and provider == "gemini":
            prompt = f"{system_prompt}\n\n{prompt}"

        messages.append({"role": "user", "content": prompt})

        try:
            start_time = time.time()

            # Make the API call using LiteLLM
            if completion is None:
                raise RuntimeError("LiteLLM completion function not available")
                
            response = completion(
                model=full_model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout,
            )

            end_time = time.time()

            # Extract response content
            response_content = response.choices[0].message.content

            # Track token usage and cost
            usage_info = {
                "input_tokens": response.usage.prompt_tokens
                if hasattr(response.usage, "prompt_tokens")
                else response.usage.input_tokens,
                "output_tokens": response.usage.completion_tokens
                if hasattr(response.usage, "completion_tokens")
                else response.usage.output_tokens,
                "total_tokens": response.usage.total_tokens,
                "response_time": end_time - start_time,
            }

            # Calculate cost using LiteLLM
            try:
                if completion_cost is not None:
                    cost = completion_cost(completion_response=response)
                    usage_info["cost"] = cost
                else:
                    usage_info["cost"] = 0.0
            except Exception as e:
                logger.warning(f"Could not calculate cost for {provider}: {e}")
                usage_info["cost"] = 0.0

            # Update global usage tracking
            self.token_usage[provider]["input_tokens"] += usage_info["input_tokens"]
            self.token_usage[provider]["output_tokens"] += usage_info["output_tokens"]
            self.token_usage[provider]["cost"] += usage_info["cost"]

            return {
                "content": response_content,
                "usage": usage_info,
                "provider": provider,
                "model": model,
                "full_model_name": full_model_name,
                "timestamp": datetime.now().isoformat(),
                "success": True,
            }

        except Exception as e:
            logger.error(f"Error calling {provider} {model}: {e}")
            return {
                "content": "",
                "error": str(e),
                "provider": provider,
                "model": model,
                "full_model_name": full_model_name,
                "timestamp": datetime.now().isoformat(),
                "success": False,
            }

    def get_available_providers(self) -> list[str]:
        """Get list of providers with valid API keys.
        
        Returns:
            List of provider names that have valid API keys.
        """
        available = self._validate_api_keys()
        return [
            provider for provider, is_available in available.items() if is_available
        ]

    def get_provider_models(self, provider: str) -> list[str]:
        """Get available models for a provider.
        
        Args:
            provider: Provider name.
            
        Returns:
            List of available model names for the provider.
        """
        if provider not in self.PROVIDER_CONFIGS:
            return []
        return list(self.PROVIDER_CONFIGS[provider].keys())

    def estimate_cost(
        self, provider: str, model: str, input_tokens: int, output_tokens: int
    ) -> float:
        """Estimate cost for a request (approximate).
        
        Args:
            provider: Provider name.
            model: Model name.
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.
            
        Returns:
            Estimated cost in USD.
        """
        _ = self.get_model_name(provider, model)

        try:
            # Use LiteLLM's cost calculation (requires actual response object)
            # This is an approximation - actual cost calculated after response

            # Rough cost estimates (per 1K tokens)
            cost_estimates = {
                "anthropic": {
                    "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
                    "claude-3-sonnet": {"input": 0.003, "output": 0.015},
                    "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
                },
                "openai": {
                    "gpt-4o": {"input": 0.005, "output": 0.015},
                    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
                    "gpt-4": {"input": 0.03, "output": 0.06},
                    "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
                },
                "gemini": {
                    "gemini-pro": {"input": 0.0005, "output": 0.0015},
                    "gemini-1.5-pro": {"input": 0.007, "output": 0.021},
                    "gemini-2.0-flash": {"input": 0.000375, "output": 0.0015},
                },
            }

            if provider in cost_estimates and model in cost_estimates[provider]:
                rates = cost_estimates[provider][model]
                input_cost = (input_tokens / 1000) * rates["input"]
                output_cost = (output_tokens / 1000) * rates["output"]
                return input_cost + output_cost

            return 0.0

        except Exception as e:
            logger.warning(f"Could not estimate cost for {provider} {model}: {e}")
            return 0.0

    def get_total_usage(self) -> dict[str, Any]:
        """Get total token usage and cost across all providers.
        
        Returns:
            Dictionary containing total usage statistics.
        """
        total_input = sum(usage["input_tokens"] for usage in self.token_usage.values())
        total_output = sum(
            usage["output_tokens"] for usage in self.token_usage.values()
        )
        total_cost = sum(usage["cost"] for usage in self.token_usage.values())

        return {
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_input + total_output,
            "total_cost": round(total_cost, 4),
            "by_provider": self.token_usage,
        }

    def reset_usage_tracking(self) -> None:
        """Reset token usage tracking."""
        for provider in self.token_usage:
            self.token_usage[provider] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "cost": 0.0,
            }
