import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.agent_config import AgentConfig
from app.models.run import Run
from app.models.evaluation import Evaluation
from app.evaluators.task_completion import TaskCompletionEvaluator
from app.evaluators.tool_accuracy import ToolAccuracyEvaluator
from app.evaluators.citation import CitationEvaluator
from app.evaluators.hallucination import HallucinationDetector
from app.evaluators.latency_cost import LatencyCostTracker

class EvaluationPipeline:
    def __init__(self):
        self.evaluators = [
            TaskCompletionEvaluator(),
            ToolAccuracyEvaluator(),
            CitationEvaluator(),
            HallucinationDetector(),
            LatencyCostTracker(),
        ]

    async def evaluate_run(self, db: Session, run: Run, task: Optional[Task] = None, agent_config: Optional[AgentConfig] = None) -> Evaluation:
        if not task:
            task = db.query(Task).filter(Task.id == run.task_id).first()
        if not agent_config:
            agent_config = db.query(AgentConfig).filter(AgentConfig.id == run.agent_config_id).first()

        results = {}
        raw_results = []

        for evaluator in self.evaluators:
            res = await evaluator.evaluate(task, agent_config, run)
            results[evaluator.name] = res
            raw_results.append(res.model_dump())

        # Extract metric results
        comp_res = results.get("task_completion")
        tool_res = results.get("tool_accuracy")
        cit_res = results.get("citation_correctness")
        hall_res = results.get("hallucination_detector")
        lat_res = results.get("latency_cost")

        completion_rate = comp_res.passed if comp_res else False
        completion_score = comp_res.score if comp_res else 0.0

        tool_accuracy = tool_res.score if tool_res else 100.0
        tool_details = tool_res.details if tool_res else {}
        tool_error_count = tool_details.get("tool_error_count", 0)
        unnecessary_tool_calls = tool_details.get("unnecessary_tool_calls", 0)
        ignored_tool_errors = tool_details.get("ignored_tool_errors", 0)

        citation_precision = cit_res.score if cit_res else 100.0
        citation_details = cit_res.details if cit_res else {}
        uncited_claims_count = citation_details.get("uncited_claims_count", 0)
        broken_link_count = citation_details.get("broken_link_count", 0)

        hallucination_details = hall_res.details if hall_res else {}
        hallucination_rate = hallucination_details.get("hallucination_rate", 0.0)
        phantom_tool_use_count = hallucination_details.get("phantom_tool_use_count", 0)

        # Overall composite score calculation
        # Weights: Completion 40%, Tool Accuracy 25%, Hallucination freedom 20%, Citation 15%
        hallucination_freedom = max(0.0, 100.0 - hallucination_rate)
        overall_score = round(
            (completion_score * 0.40) +
            (tool_accuracy * 0.25) +
            (hallucination_freedom * 0.20) +
            (citation_precision * 0.15),
            1
        )

        overall_passed = (
            completion_rate and
            phantom_tool_use_count == 0 and
            broken_link_count == 0 and
            ignored_tool_errors == 0 and
            overall_score >= 70.0
        )

        # Check existing evaluation
        eval_record = db.query(Evaluation).filter(Evaluation.run_id == run.id).first()
        if not eval_record:
            eval_record = Evaluation(
                id=str(uuid.uuid4()),
                run_id=run.id,
                overall_passed=overall_passed,
                overall_score=overall_score,
                completion_rate=completion_rate,
                completion_score=completion_score,
                completion_details=comp_res.details if comp_res else {},
                tool_call_accuracy=tool_accuracy,
                tool_error_count=tool_error_count,
                unnecessary_tool_calls=unnecessary_tool_calls,
                ignored_tool_errors=ignored_tool_errors,
                tool_details=tool_details,
                citation_precision=citation_precision,
                uncited_claims_count=uncited_claims_count,
                broken_link_count=broken_link_count,
                citation_details=citation_details,
                hallucination_rate=hallucination_rate,
                phantom_tool_use_count=phantom_tool_use_count,
                hallucination_details=hallucination_details,
                latency_details=lat_res.details if lat_res else {},
                cost_details=lat_res.details if lat_res else {},
                raw_evaluator_results=raw_results,
                created_at=datetime.now(timezone.utc)
            )
            db.add(eval_record)
        else:
            eval_record.overall_passed = overall_passed
            eval_record.overall_score = overall_score
            eval_record.completion_rate = completion_rate
            eval_record.completion_score = completion_score
            eval_record.completion_details = comp_res.details if comp_res else {}
            eval_record.tool_call_accuracy = tool_accuracy
            eval_record.tool_error_count = tool_error_count
            eval_record.unnecessary_tool_calls = unnecessary_tool_calls
            eval_record.ignored_tool_errors = ignored_tool_errors
            eval_record.tool_details = tool_details
            eval_record.citation_precision = citation_precision
            eval_record.uncited_claims_count = uncited_claims_count
            eval_record.broken_link_count = broken_link_count
            eval_record.citation_details = citation_details
            eval_record.hallucination_rate = hallucination_rate
            eval_record.phantom_tool_use_count = phantom_tool_use_count
            eval_record.hallucination_details = hallucination_details
            eval_record.latency_details = lat_res.details if lat_res else {}
            eval_record.cost_details = lat_res.details if lat_res else {}
            eval_record.raw_evaluator_results = raw_results

        db.commit()
        db.refresh(eval_record)
        return eval_record

evaluation_pipeline = EvaluationPipeline()
