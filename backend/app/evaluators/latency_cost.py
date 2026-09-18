from typing import Any
from app.evaluators.base import BaseEvaluator
from app.models.task import Task
from app.models.agent_config import AgentConfig
from app.models.run import Run
from app.schemas.evaluation import EvaluatorResult

DEFAULT_PRICING = {
    # USD per 1M tokens: (input, output)
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "claude-sonnet-4-6": (3.00, 15.00),
    "claude-haiku-3-5": (0.80, 4.00),
    "gemini-1.5-pro": (1.25, 5.00),
    "gemini-1.5-flash": (0.075, 0.30),
    "mock-agent": (0.00, 0.00),
    "mock-fast": (0.00, 0.00),
    "mock-creative": (0.00, 0.00),
    "default": (2.00, 8.00)
}

def calculate_cost(model_name: str, input_tokens: int, output_tokens: int, custom_pricing: dict[str, tuple[float, float]] = None) -> float:
    pricing = custom_pricing or DEFAULT_PRICING
    rates = pricing.get(model_name.lower()) or pricing.get("default", (2.00, 8.00))
    input_rate, output_rate = rates
    cost = (input_tokens * (input_rate / 1_000_000.0)) + (output_tokens * (output_rate / 1_000_000.0))
    return round(cost, 6)

class LatencyCostTracker(BaseEvaluator):
    @property
    def name(self) -> str:
        return "latency_cost"

    async def evaluate(self, task: Task, agent_config: AgentConfig, run: Run) -> EvaluatorResult:
        transcript = run.full_transcript or []
        budget = task.budget_constraints or {}
        max_latency_ms = budget.get("max_latency_ms", 15000.0)
        max_cost_usd = budget.get("max_cost_usd", 0.10)

        # Per-step latency breakdown
        step_latencies = []
        for step in transcript:
            step_latencies.append({
                "step_index": step.get("step_index", 0),
                "role": step.get("role"),
                "latency_ms": step.get("step_latency_ms", 0.0)
            })

        total_latency = run.latency_ms or sum(s["latency_ms"] for s in step_latencies)
        ttft = run.time_to_first_token_ms or (step_latencies[0]["latency_ms"] * 0.4 if step_latencies else 0.0)

        token_usage = run.token_usage or {}
        in_tokens = token_usage.get("input_tokens", 0)
        out_tokens = token_usage.get("output_tokens", 0)
        tot_tokens = token_usage.get("total_tokens", in_tokens + out_tokens)

        cost = run.cost_usd
        if cost == 0.0 and tot_tokens > 0:
            cost = calculate_cost(agent_config.model, in_tokens, out_tokens)

        # Evaluate against budget constraints
        latency_ok = total_latency <= max_latency_ms if max_latency_ms else True
        cost_ok = cost <= max_cost_usd if max_cost_usd else True
        passed = latency_ok and cost_ok

        # Score efficiency 0 - 100
        latency_ratio = min(1.0, total_latency / max_latency_ms) if max_latency_ms else 0.5
        cost_ratio = min(1.0, cost / max_cost_usd) if max_cost_usd and cost > 0 else 0.5
        efficiency_score = round(max(0.0, 100.0 - (latency_ratio * 40.0 + cost_ratio * 40.0)), 1)

        evidence = (
            f"Latency: {round(total_latency, 1)}ms (budget: {max_latency_ms}ms, TTFT: {round(ttft, 1)}ms). "
            f"Cost: ${round(cost, 5)} for {tot_tokens} tokens (budget: ${max_cost_usd})."
        )

        return EvaluatorResult(
            metric="latency_cost",
            score=efficiency_score,
            passed=passed,
            evidence=evidence,
            details={
                "total_latency_ms": round(total_latency, 1),
                "time_to_first_token_ms": round(ttft, 1),
                "step_latencies": step_latencies,
                "input_tokens": in_tokens,
                "output_tokens": out_tokens,
                "total_tokens": tot_tokens,
                "cost_usd": cost,
                "max_latency_ms": max_latency_ms,
                "max_cost_usd": max_cost_usd,
                "within_budget": passed
            }
        )
