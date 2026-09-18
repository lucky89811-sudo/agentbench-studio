import math
from typing import Any
from sqlalchemy.orm import Session
from app.models.batch import RunBatch
from app.models.task import Task
from app.models.agent_config import AgentConfig
from app.models.comparison import Comparison

def normal_cdf(z: float) -> float:
    """Standard normal cumulative distribution function using math.erf."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))

def two_proportion_z_test(x1: int, n1: int, x2: int, n2: int) -> dict[str, Any]:
    """
    Computes two-proportion z-test for difference in success rates.
    x1, x2: number of successes (passing runs)
    n1, n2: sample sizes (total runs)
    """
    if n1 <= 0 or n2 <= 0:
        return {"z_score": 0.0, "p_value": 1.0, "is_significant": False, "ci_95": [0.0, 0.0]}

    p1 = x1 / n1
    p2 = x2 / n2
    diff = p1 - p2

    pooled_p = (x1 + x2) / (n1 + n2)

    if pooled_p == 0.0 or pooled_p == 1.0:
        return {
            "z_score": 0.0,
            "p_value": 1.0 if diff == 0 else 0.0,
            "is_significant": diff != 0,
            "ci_95": [round(diff, 4), round(diff, 4)],
            "difference": round(diff, 4)
        }

    se_pooled = math.sqrt(pooled_p * (1.0 - pooled_p) * (1.0 / n1 + 1.0 / n2))
    if se_pooled == 0.0:
        z_score = 0.0
        p_value = 1.0
    else:
        z_score = diff / se_pooled
        # Two-tailed p-value
        p_value = 2.0 * (1.0 - normal_cdf(abs(z_score)))

    # 95% Confidence Interval for difference
    se_diff = math.sqrt((p1 * (1.0 - p1) / n1) + (p2 * (1.0 - p2) / n2))
    margin = 1.96 * se_diff
    ci_lower = max(-1.0, diff - margin)
    ci_upper = min(1.0, diff + margin)

    return {
        "z_score": round(z_score, 4),
        "p_value": round(p_value, 4),
        "is_significant": p_value < 0.05,
        "ci_95": [round(ci_lower, 4), round(ci_upper, 4)],
        "difference": round(diff, 4),
        "rate_1": round(p1, 4),
        "rate_2": round(p2, 4)
    }

class ComparisonService:
    def build_comparison(self, db: Session, task_id: str, batch_ids: list[str], comparison_name: str = "") -> Comparison:
        batches = db.query(RunBatch).filter(RunBatch.id.in_(batch_ids)).all()
        task = db.query(Task).filter(Task.id == task_id).first()

        metrics_matrix = []
        for b in batches:
            cfg = db.query(AgentConfig).filter(AgentConfig.id == b.agent_config_id).first()
            sm = b.summary_metrics or {}
            metrics_matrix.append({
                "batch_id": b.id,
                "agent_config_id": b.agent_config_id,
                "agent_name": cfg.name if cfg else "Unknown",
                "model": cfg.model if cfg else "Unknown",
                "n_runs": b.n_runs,
                "overall_pass_rate": sm.get("overall_pass_rate", 0.0),
                "completion_rate": sm.get("completion_rate", 0.0),
                "tool_call_accuracy": sm.get("tool_call_accuracy", 0.0),
                "citation_precision": sm.get("citation_precision", 0.0),
                "hallucination_rate": sm.get("hallucination_rate", 0.0),
                "avg_score": sm.get("avg_score", 0.0),
                "avg_latency_ms": sm.get("avg_latency_ms", 0.0),
                "cost_per_successful_task": sm.get("cost_per_successful_task", 0.0),
                "passing_runs_count": sm.get("passing_runs_count", 0),
            })

        # Pairwise statistical test between first two batches (or all pairs)
        stats_result = {}
        if len(metrics_matrix) >= 2:
            m1 = metrics_matrix[0]
            m2 = metrics_matrix[1]
            x1 = m1["passing_runs_count"]
            n1 = m1["n_runs"]
            x2 = m2["passing_runs_count"]
            n2 = m2["n_runs"]
            stats_result = two_proportion_z_test(x1, n1, x2, n2)
            stats_result["comparison_pair"] = f"{m1['agent_name']} vs {m2['agent_name']}"

        name = comparison_name or f"Comparison: {task.name if task else 'Task'} ({len(batches)} configs)"
        comparison = Comparison(
            name=name,
            task_id=task_id,
            batch_ids=batch_ids,
            metrics_matrix={"configs": metrics_matrix},
            statistical_confidence=stats_result
        )
        db.add(comparison)
        db.commit()
        db.refresh(comparison)
        return comparison

comparison_service = ComparisonService()
