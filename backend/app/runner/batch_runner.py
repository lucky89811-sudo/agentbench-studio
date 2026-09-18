import asyncio
import statistics
import time
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.task import Task
from app.models.agent_config import AgentConfig
from app.models.run import Run
from app.models.batch import RunBatch
from app.models.evaluation import Evaluation
from app.runner.base import BaseRunner
from app.runner.mock_runner import MockRunner
from app.runner.openai_runner import OpenAIRunner
from app.runner.providers import AnthropicRunner, GeminiRunner, GenericOpenAIRunner
from app.evaluators.pipeline import evaluation_pipeline

def get_runner_for_config(agent_config: AgentConfig) -> BaseRunner:
    provider = (agent_config.provider or "mock").lower()
    if provider == "openai":
        return OpenAIRunner()
    elif provider == "anthropic":
        return AnthropicRunner()
    elif provider == "gemini":
        return GeminiRunner()
    elif provider == "generic":
        return GenericOpenAIRunner()
    else:
        return MockRunner()

class BatchRunner:
    async def run_single_iteration(
        self,
        batch_id: str,
        task_id: str,
        agent_config_id: str,
        run_index: int,
        semaphore: asyncio.Semaphore,
        max_retries: int = 2
    ):
        async with semaphore:
            db: Session = SessionLocal()
            try:
                # Check if this run index was already completed (resumability/idempotency)
                existing_run = db.query(Run).filter(
                    Run.batch_id == batch_id,
                    Run.run_index == run_index
                ).first()

                if existing_run and existing_run.status == "completed":
                    return existing_run

                task = db.query(Task).filter(Task.id == task_id).first()
                config = db.query(AgentConfig).filter(AgentConfig.id == agent_config_id).first()
                runner = get_runner_for_config(config)

                # Initialize or update Run record in DB as 'running'
                if not existing_run:
                    run_record = Run(
                        id=str(uuid.uuid4()),
                        batch_id=batch_id,
                        task_id=task_id,
                        agent_config_id=agent_config_id,
                        run_index=run_index,
                        status="running",
                        created_at=datetime.now(timezone.utc)
                    )
                    db.add(run_record)
                else:
                    run_record = existing_run
                    run_record.status = "running"

                db.commit()
                db.refresh(run_record)

                # Execute with transient retry logic
                exec_result = None
                for attempt in range(max_retries + 1):
                    try:
                        exec_result = await runner.execute(task, config)
                        if exec_result.status == "completed":
                            break
                        # If failed due to API rate-limit/network (transient), backoff and retry
                        if attempt < max_retries and "rate" in str(exec_result.error_trace).lower():
                            await asyncio.sleep(2 ** attempt)
                    except Exception as exc:
                        if attempt == max_retries:
                            exec_result = None
                            run_record.error_trace = f"Execution Exception: {type(exc).__name__}: {str(exc)}"
                            run_record.status = "failed"
                        else:
                            await asyncio.sleep(1.0 * (attempt + 1))

                if exec_result and exec_result.status == "completed":
                    run_record.status = "completed"
                    run_record.full_transcript = exec_result.transcript
                    run_record.final_output = exec_result.final_output
                    run_record.latency_ms = exec_result.latency_ms
                    run_record.time_to_first_token_ms = exec_result.time_to_first_token_ms
                    run_record.token_usage = exec_result.token_usage
                    run_record.cost_usd = exec_result.cost_usd
                    run_record.completed_at = datetime.now(timezone.utc)
                    db.commit()
                    db.refresh(run_record)

                    # Trigger evaluation pipeline immediately
                    await evaluation_pipeline.evaluate_run(db, run_record, task, config)
                else:
                    run_record.status = "failed"
                    run_record.completed_at = datetime.now(timezone.utc)
                    db.commit()

                return run_record
            finally:
                db.close()

    async def execute_batch(self, batch_id: str):
        """Orchestrates all iterations in the batch with concurrency control and computes summary metrics."""
        db: Session = SessionLocal()
        try:
            batch = db.query(RunBatch).filter(RunBatch.id == batch_id).first()
            if not batch:
                return

            batch.status = "running"
            db.commit()

            semaphore = asyncio.Semaphore(batch.concurrency_limit or 3)
            tasks = [
                self.run_single_iteration(
                    batch_id=batch.id,
                    task_id=batch.task_id,
                    agent_config_id=batch.agent_config_id,
                    run_index=idx,
                    semaphore=semaphore
                )
                for idx in range(1, batch.n_runs + 1)
            ]

            await asyncio.gather(*tasks, return_exceptions=True)

            # Re-query all runs in the batch to calculate metrics
            runs = db.query(Run).filter(Run.batch_id == batch.id).all()
            completed_runs = [r for r in runs if r.status == "completed"]
            failed_runs = [r for r in runs if r.status == "failed"]

            batch.completed_runs_count = len(completed_runs)
            batch.failed_runs_count = len(failed_runs)

            # Aggregate evaluations
            evaluations = []
            for r in completed_runs:
                ev = db.query(Evaluation).filter(Evaluation.run_id == r.id).first()
                if ev:
                    evaluations.append(ev)

            total_runs = len(runs) or 1
            passing_runs = [ev for ev in evaluations if ev.overall_passed]
            completion_passes = [ev for ev in evaluations if ev.completion_rate]

            completion_rate = (len(completion_passes) / len(evaluations) * 100.0) if evaluations else 0.0
            overall_pass_rate = (len(passing_runs) / total_runs * 100.0) if total_runs else 0.0

            avg_tool_accuracy = statistics.mean([ev.tool_call_accuracy for ev in evaluations]) if evaluations else 100.0
            avg_citation_precision = statistics.mean([ev.citation_precision for ev in evaluations]) if evaluations else 100.0
            avg_hallucination_rate = statistics.mean([ev.hallucination_rate for ev in evaluations]) if evaluations else 0.0
            avg_score = statistics.mean([ev.overall_score for ev in evaluations]) if evaluations else 0.0

            scores = [ev.overall_score for ev in evaluations]
            score_variance = statistics.pvariance(scores) if len(scores) > 1 else 0.0

            latencies = [r.latency_ms for r in completed_runs]
            avg_latency = statistics.mean(latencies) if latencies else 0.0
            latency_variance = statistics.pvariance(latencies) if len(latencies) > 1 else 0.0

            costs = [r.cost_usd for r in completed_runs]
            total_batch_cost = sum(costs)
            avg_cost = statistics.mean(costs) if costs else 0.0

            # Headline efficiency metric: Total batch cost / number of passing runs
            cost_per_successful_task = round(total_batch_cost / max(1, len(passing_runs)), 6)

            batch.summary_metrics = {
                "overall_pass_rate": round(overall_pass_rate, 1),
                "completion_rate": round(completion_rate, 1),
                "tool_call_accuracy": round(avg_tool_accuracy, 1),
                "citation_precision": round(avg_citation_precision, 1),
                "hallucination_rate": round(avg_hallucination_rate, 1),
                "avg_score": round(avg_score, 1),
                "score_variance": round(score_variance, 2),
                "score_std_dev": round(score_variance ** 0.5, 2),
                "avg_latency_ms": round(avg_latency, 1),
                "latency_variance": round(latency_variance, 2),
                "latency_std_dev": round(latency_variance ** 0.5, 1),
                "avg_cost_usd": round(avg_cost, 6),
                "total_cost_usd": round(total_batch_cost, 6),
                "cost_per_successful_task": cost_per_successful_task,
                "passing_runs_count": len(passing_runs),
                "total_runs_count": total_runs
            }

            batch.status = "completed"
            batch.completed_at = datetime.now(timezone.utc)
            db.commit()
        finally:
            db.close()

batch_runner = BatchRunner()
