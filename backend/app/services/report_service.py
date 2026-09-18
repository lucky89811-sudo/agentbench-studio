import statistics
from typing import Any
from sqlalchemy.orm import Session
from app.models.batch import RunBatch
from app.models.task import Task
from app.models.agent_config import AgentConfig
from app.models.run import Run
from app.models.evaluation import Evaluation

def compute_percentiles(values: list[float]) -> dict[str, float]:
    if not values:
        return {"min": 0.0, "p25": 0.0, "p50": 0.0, "p75": 0.0, "max": 0.0, "mean": 0.0, "std_dev": 0.0}
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    return {
        "min": round(sorted_vals[0], 2),
        "p25": round(sorted_vals[int(n * 0.25)], 2),
        "p50": round(sorted_vals[int(n * 0.50)], 2),
        "p75": round(sorted_vals[int(n * 0.75)], 2),
        "max": round(sorted_vals[-1], 2),
        "mean": round(statistics.mean(sorted_vals), 2),
        "std_dev": round(statistics.pstdev(sorted_vals), 2) if n > 1 else 0.0
    }

class ReportService:
    def generate_batch_report(self, db: Session, batch_id: str) -> dict[str, Any]:
        batch = db.query(RunBatch).filter(RunBatch.id == batch_id).first()
        if not batch:
            return {"error": "Batch not found"}

        task = db.query(Task).filter(Task.id == batch.task_id).first()
        config = db.query(AgentConfig).filter(AgentConfig.id == batch.agent_config_id).first()
        runs = db.query(Run).filter(Run.batch_id == batch.id).order_by(Run.run_index).all()

        run_evals = []
        for r in runs:
            ev = db.query(Evaluation).filter(Evaluation.run_id == r.id).first()
            run_evals.append((r, ev))

        scores = [ev.overall_score for _, ev in run_evals if ev]
        latencies = [r.latency_ms for r, _ in run_evals if r.status == "completed"]
        tokens = [r.token_usage.get("total_tokens", 0) for r, _ in run_evals if r.status == "completed"]
        costs = [r.cost_usd for r, _ in run_evals if r.status == "completed"]

        score_dist = compute_percentiles(scores)
        latency_dist = compute_percentiles(latencies)
        token_dist = compute_percentiles(tokens)
        cost_dist = compute_percentiles(costs)

        # Worst-run drilldown (sorted by overall_score ascending)
        sorted_by_score = sorted(
            [item for item in run_evals if item[1] is not None],
            key=lambda x: x[1].overall_score
        )

        worst_runs = []
        for r, ev in sorted_by_score[:3]:
            # Highlight defective steps in transcript
            annotated_transcript = []
            for step in (r.full_transcript or []):
                flags = []
                # Check phantom tool
                if ev.phantom_tool_use_count > 0 and step.get("role") == "assistant":
                    for p in ev.hallucination_details.get("phantom_claims", []):
                        if p.get("matched_phrase", "").lower() in str(step.get("content", "")).lower():
                            flags.append(f"Phantom Tool Claim: claimed '{p.get('claimed_tool_type')}' without invocation")
                # Check ignored error
                if step.get("role") == "tool" and any("error" in str(res.get("content", "")).lower() for res in step.get("tool_results", [])):
                    flags.append("Tool Error Occurred")

                step_copy = dict(step)
                step_copy["defect_flags"] = flags
                annotated_transcript.append(step_copy)

            worst_runs.append({
                "run_id": r.id,
                "run_index": r.run_index,
                "overall_score": ev.overall_score,
                "overall_passed": ev.overall_passed,
                "latency_ms": r.latency_ms,
                "cost_usd": r.cost_usd,
                "final_output": r.final_output,
                "failure_reasons": [
                    res["evidence"] for res in ev.raw_evaluator_results if not res.get("passed", True)
                ],
                "evaluator_scores": {
                    "completion_rate": ev.completion_rate,
                    "completion_score": ev.completion_score,
                    "tool_accuracy": ev.tool_call_accuracy,
                    "citation_precision": ev.citation_precision,
                    "hallucination_rate": ev.hallucination_rate,
                    "phantom_tool_count": ev.phantom_tool_use_count,
                    "broken_link_count": ev.broken_link_count,
                    "ignored_tool_errors": ev.ignored_tool_errors
                },
                "transcript": annotated_transcript
            })

        # Historical trend (other batches of same task + config)
        history_batches = db.query(RunBatch).filter(
            RunBatch.task_id == batch.task_id,
            RunBatch.agent_config_id == batch.agent_config_id,
            RunBatch.status == "completed"
        ).order_by(RunBatch.created_at.asc()).all()

        trend = []
        for hb in history_batches:
            sm = hb.summary_metrics or {}
            trend.append({
                "batch_id": hb.id,
                "created_at": hb.created_at.isoformat(),
                "pass_rate": sm.get("overall_pass_rate", 0.0),
                "avg_score": sm.get("avg_score", 0.0),
                "avg_latency_ms": sm.get("avg_latency_ms", 0.0),
                "cost_per_successful_task": sm.get("cost_per_successful_task", 0.0)
            })

        return {
            "batch_id": batch.id,
            "status": batch.status,
            "created_at": batch.created_at.isoformat(),
            "completed_at": batch.completed_at.isoformat() if batch.completed_at else None,
            "task": {
                "id": task.id if task else "",
                "name": task.name if task else "",
                "category": task.category if task else "",
                "prompt_template": task.prompt_template if task else ""
            },
            "agent_config": {
                "id": config.id if config else "",
                "name": config.name if config else "",
                "model": config.model if config else "",
                "provider": config.provider if config else "",
                "prompt_version": config.prompt_version if config else ""
            },
            "scorecard": batch.summary_metrics or {},
            "distributions": {
                "score": score_dist,
                "latency": latency_dist,
                "tokens": token_dist,
                "cost": cost_dist,
                "raw_run_scores": [
                    {"run_index": r.run_index, "score": ev.overall_score if ev else 0.0, "latency_ms": r.latency_ms, "cost_usd": r.cost_usd, "passed": ev.overall_passed if ev else False}
                    for r, ev in run_evals
                ]
            },
            "worst_runs": worst_runs,
            "historical_trend": trend
        }

report_service = ReportService()
