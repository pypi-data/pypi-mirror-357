"""
Metrics collection for LLM monitoring.
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional

from metricllm.utils.metric_logging import get_logger


class MetricsCollector:
    """Collects various metrics for LLM interactions."""

    def __init__(self):
        self.logger = get_logger(__name__)

        # Token pricing per 1K tokens (approximate as of 2024)
        # Token pricing per 1K tokens (approximate as of 2024)
        self.pricing = {
            "openai": {
                "gpt-4": {"input": 0.03, "output": 0.06},
                "gpt-4-turbo": {"input": 0.01, "output": 0.03},
                "gpt-4o": {"input": 0.005, "output": 0.015},
                "gpt-4.1-mini": {"input": 0.0004, "output": 0.0016},
                "gpt-4.1-nano": {"input": 0.0001, "output": 0.0004},
                "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
                "gpt-3.5-turbo-instruct": {"input": 0.0015, "output": 0.002},
            },
            "anthropic": {
                "claude-3-opus": {"input": 0.015, "output": 0.075},
                "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
                "claude-3-sonnet": {"input": 0.003, "output": 0.015},
                "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
                "claude-3-5-haiku": {"input": 0.001, "output": 0.005},
            },
            "google": {
                "gemini-2.5-pro": {"input": 1.25, "output": 10.00},
                "gemini-2.5-flash": {"input": 0.30, "output": 2.50},
                "gemini-2.5-flash-lite": {"input": 0.10, "output": 0.40},
                "gemini-2.5-flash-native-audio": {"input": 3.00, "output": 12.00},
                "gemini-2.5-preview-tts": {"input": 0.50, "output": 10.00},
                "gemini-2.5-pro-preview-tts": {"input": 1.00, "output": 20.00},
                "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
                "gemini-2.0-flash-lite": {"input": 0.075, "output": 0.30},
                "gemini-1.5-flash": {"input": 0.15, "output": 0.60},
                "gemini-1.5-pro": {"input": 2.50, "output": 10.00},
                "imagen-3": {"input": 0.039, "output": 0.039},
                "veo-2": {"input": 0.35, "output": 0.35},
                "gemini-2.0-flash-live": {"input": 0.35, "output": 1.50},
                "gemini-embedding": {"input": 0.30, "output": 0.30},
                "gemini-2.5-flash-preview-native-audio-dialog": {"input": 3.00, "output": 12.00},
                "gemini-2.5-flash-exp-native-audio-thinking-dialog": {"input": 3.00, "output": 12.00},
                "gemini-2.0-flash-preview-image-generation": {"input": 0.10, "output": 0.40},
            },
            "amazon": {
                "claude-3-opus-bedrock": {"input": 0.015, "output": 0.075},
                "claude-3-sonnet-bedrock": {"input": 0.003, "output": 0.015},
                "claude-3-haiku-bedrock": {"input": 0.00025, "output": 0.00125},
                "titan-text-express": {"input": 0.0008, "output": 0.0016},
                "titan-text-lite": {"input": 0.0003, "output": 0.0004},
                "cohere-command": {"input": 0.0015, "output": 0.002},
                "ai21-j2-ultra": {"input": 0.0125, "output": 0.0125},
                "meta-llama2-70b": {"input": 0.00195, "output": 0.00256},
            },
            "xai": {
                "grok-beta": {"input": 0.005, "output": 0.015},
                "grok-vision-beta": {"input": 0.005, "output": 0.015},
                "grok-2-1212": {"input": 0.002, "output": 0.01},
                "grok-2-vision-1212": {"input": 0.002, "output": 0.01},
            },
            "meta": {
                "llama-2-7b": {"input": 0.0002, "output": 0.0002},
                "llama-2-13b": {"input": 0.0003, "output": 0.0004},
                "llama-2-70b": {"input": 0.0009, "output": 0.0009},
                "llama-3-8b": {"input": 0.00015, "output": 0.00015},
                "llama-3-70b": {"input": 0.0008, "output": 0.0008},
                "llama-3.1-8b": {"input": 0.00015, "output": 0.00015},
                "llama-3.1-70b": {"input": 0.0008, "output": 0.0008},
                "llama-3.1-405b": {"input": 0.005, "output": 0.005},
            },
            "ollama": {
                "llama2": {"input": 0.0, "output": 0.0},
                "llama3": {"input": 0.0, "output": 0.0},
                "mistral": {"input": 0.0, "output": 0.0},
                "codellama": {"input": 0.0, "output": 0.0},
                "phi": {"input": 0.0, "output": 0.0},
                "vicuna": {"input": 0.0, "output": 0.0},
            },
            "huggingface": {
                "llama-2-7b-chat": {"input": 0.0002, "output": 0.0002},
                "llama-2-13b-chat": {"input": 0.0003, "output": 0.0004},
                "llama-2-70b-chat": {"input": 0.0009, "output": 0.0009},
                "mistral-7b": {"input": 0.0002, "output": 0.0002},
                "mixtral-8x7b": {"input": 0.0007, "output": 0.0007},
            }
        }

    def collect(self,
                provider: str,
                model: str,
                prompt: str,
                response: str,
                execution_time: float,
                track_tokens: bool = True,
                track_cost: bool = True,
                usage_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Collect comprehensive metrics for an LLM interaction.

        Args:
            provider: LLM provider name (will be auto-detected if possible)
            model: Model name (will be auto-detected if possible)
            prompt: Input prompt
            response: Model response
            execution_time: Time taken for the call
            track_tokens: Whether to track token usage
            track_cost: Whether to estimate costs
            usage_data: Actual usage data from the API response

        Returns:
            Dictionary containing collected metrics
        """
        # --- Auto-detect provider/model if possible -- Future ---
        detected_provider = provider
        detected_model = model

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "provider": detected_provider,
            "model": detected_model,
            "execution_time_seconds": round(execution_time, 4),
            "execution_time_ms": round(execution_time * 1000, 2)
        }

        self.logger.info(f"Metrics : {metrics}")

        # Basic text metrics
        metrics.update(self._calculate_text_metrics(prompt, response))
        self.logger.info(f"Prompt : {prompt}")
        self.logger.info(f"Response : {response}")
        self.logger.info(f"Track Token Metrics : {track_tokens}")

        # Token metrics
        if track_tokens:
            token_metrics = self._calculate_token_metrics(prompt, response, usage_data)
            metrics.update(token_metrics)

            self.logger.info(f"Token Metrics : {token_metrics}")
            self.logger.info(f"Metrics : {metrics}")

        # Cost estimation
        if track_cost and track_tokens:
            cost_metrics = self._estimate_costs(
                detected_provider, detected_model,
                metrics.get("prompt_tokens_estimated", 0),
                metrics.get("completion_tokens_estimated", 0)
            )
            metrics.update(cost_metrics)

            self.logger.info(f"Cost Metrics : {cost_metrics}")
        # Performance metrics
        metrics.update(self._calculate_performance_metrics(execution_time, metrics))

        return metrics

    def _calculate_text_metrics(self, prompt: str, response: str) -> Dict[str, Any]:
        """Calculate basic text-based metrics."""
        return {
            "prompt_length": len(prompt),
            "response_length": len(response),
            "prompt_words": len(prompt.split()),
            "response_words": len(response.split()),
            "prompt_lines": len(prompt.split('\n')),
            "response_lines": len(response.split('\n'))
        }

    def _calculate_token_metrics(self, prompt: str, response: str, usage_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Calculate token-based metrics."""
        if usage_data:
            # Use actual usage data if available
            return {
                "prompt_tokens": usage_data.get("prompt_tokens", 0),
                "completion_tokens": usage_data.get("completion_tokens", 0),
                "total_tokens": usage_data.get("total_tokens", 0)
            }
        else:
            # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
            prompt_tokens = max(1, len(prompt) // 4)
            completion_tokens = max(1, len(response) // 4)

            return {
                "prompt_tokens_estimated": prompt_tokens,
                "completion_tokens_estimated": completion_tokens,
                "total_tokens_estimated": prompt_tokens + completion_tokens
            }

    def _estimate_costs(self, provider: str, model: str, prompt_tokens: int, completion_tokens: int) -> Dict[str, Any]:
        """Estimate costs based on token usage."""
        cost_data = {
            "estimated_cost_usd": 0.0,
            "cost_breakdown": {
                "input_cost": 0.0,
                "output_cost": 0.0
            },
            "pricing_source": "estimated"
        }

        if provider and (provider_key := provider.lower()) in self.pricing:
            provider_pricing = self.pricing[provider_key]
            model_cost = provider_pricing.get(model)

            if model_cost:
                # Compute costs per 1K tokens
                input_price = model_cost.get("input", 0.0)
                output_price = model_cost.get("output", 0.0)

                input_cost = round((prompt_tokens / 1000.0) * input_price, 6)
                output_cost = round((completion_tokens / 1000.0) * output_price, 6)
                total_cost = round(input_cost + output_cost, 6)

                self.logger.info(f"Cost breakdown for model '{model}':")
                self.logger.info(f"  Input Cost :{prompt_tokens} {input_cost} @ {input_price}/1K tokens")
                self.logger.info(f"  Output Cost: {completion_tokens} {output_cost} @ {output_price}/1K tokens")
                self.logger.info(f"  Total Cost : {total_cost}")

                cost_data.update({
                    "estimated_cost_usd": total_cost,
                    "cost_breakdown": {
                        "input_cost": input_cost,
                        "output_cost": output_cost
                    },
                    "pricing_model": model,
                    "pricing_per_1k_tokens": {
                        "input": input_price,
                        "output": output_price
                    }
                })

        return cost_data

    def _calculate_performance_metrics(self, execution_time: float, metrics: Dict) -> Dict[str, Any]:
        """Calculate performance-related metrics."""
        performance_metrics = {}

        # Tokens per second
        total_tokens = metrics.get("total_tokens", metrics.get("total_tokens_estimated", 0))
        if total_tokens > 0 and execution_time > 0:
            performance_metrics["tokens_per_second"] = round(total_tokens / execution_time, 2)

        # Response generation speed (characters per second)
        response_length = metrics.get("response_length", 0)
        if response_length > 0 and execution_time > 0:
            performance_metrics["chars_per_second"] = round(response_length / execution_time, 2)

        # Categorize response time
        if execution_time < 1:
            performance_metrics["response_time_category"] = "fast"
        elif execution_time < 5:
            performance_metrics["response_time_category"] = "medium"
        else:
            performance_metrics["response_time_category"] = "slow"

        return performance_metrics
