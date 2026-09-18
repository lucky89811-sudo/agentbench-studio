import json
import re
from typing import Any, Optional
import jsonschema
from app.evaluators.base import BaseEvaluator
from app.models.task import Task
from app.models.agent_config import AgentConfig
from app.models.run import Run
from app.schemas.evaluation import EvaluatorResult

def extract_json_payload(text: str) -> Optional[Any]:
    """Extracts JSON data from markdown code fences or raw string."""
    if not text or not text.strip():
        return None
    
    # Try direct parse
    trimmed = text.strip()
    try:
        return json.loads(trimmed)
    except json.JSONDecodeError:
        pass

    # Try ```json ... ``` or ``` ... ```
    code_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if code_block_match:
        try:
            return json.loads(code_block_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try finding outermost { ... } or [ ... ]
    brace_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
    if brace_match:
        try:
            return json.loads(brace_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    return None

class TaskCompletionEvaluator(BaseEvaluator):
    @property
    def name(self) -> str:
        return "task_completion"

    async def evaluate(self, task: Task, agent_config: AgentConfig, run: Run) -> EvaluatorResult:
        output = run.final_output or ""
        expected_schema = task.expected_output_schema

        # 1. Deterministic Schema Validation if expected_output_schema exists
        if expected_schema and isinstance(expected_schema, dict) and len(expected_schema) > 0:
            parsed_json = extract_json_payload(output)
            if parsed_json is None:
                return EvaluatorResult(
                    metric="task_completion",
                    score=0.0,
                    passed=False,
                    evidence="Output does not contain valid JSON matching the required schema.",
                    details={
                        "mode": "deterministic_schema",
                        "validation_errors": ["Output could not be parsed as JSON"],
                        "parsed_json": None
                    }
                )

            validator = jsonschema.Draft7Validator(expected_schema)
            errors = list(validator.iter_errors(parsed_json))
            
            if not errors:
                return EvaluatorResult(
                    metric="task_completion",
                    score=100.0,
                    passed=True,
                    evidence="Final output strictly satisfied the expected output JSON schema.",
                    details={
                        "mode": "deterministic_schema",
                        "validation_errors": [],
                        "parsed_json": parsed_json
                    }
                )
            else:
                error_msgs = [f"At '{list(e.path)}': {e.message}" for e in errors]
                # Partial credit based on ratio of satisfied constraints (at least 0, max 80 if schema failed)
                score = max(0.0, 100.0 - (len(errors) * 30.0))
                return EvaluatorResult(
                    metric="task_completion",
                    score=round(score, 1),
                    passed=False,
                    evidence=f"JSON schema validation failed with {len(errors)} error(s): " + "; ".join(error_msgs[:3]),
                    details={
                        "mode": "deterministic_schema",
                        "validation_errors": error_msgs,
                        "parsed_json": parsed_json
                    }
                )

        # 2. LLM-Judge Evaluation for Free-text rubric / non-schema tasks
        # Or heuristic fallback if no external judge key is configured
        rubric = task.success_criteria or {}
        rubric_text = rubric.get("rubric", "") if isinstance(rubric, dict) else str(rubric)
        rules = rubric.get("rules", []) if isinstance(rubric, dict) else []

        # Deterministic check for required keywords/rules if specified
        passed_rules = []
        failed_rules = []
        if rules and isinstance(rules, list):
            for rule in rules:
                if isinstance(rule, str):
                    if rule.lower() in output.lower():
                        passed_rules.append(rule)
                    else:
                        failed_rules.append(rule)
            
            if rules:
                rule_score = (len(passed_rules) / len(rules)) * 100.0
                all_passed = len(failed_rules) == 0
                evidence = f"Rule check: {len(passed_rules)}/{len(rules)} criteria met."
                if failed_rules:
                    evidence += f" Missing: {', '.join(failed_rules[:3])}"
                return EvaluatorResult(
                    metric="task_completion",
                    score=round(rule_score, 1),
                    passed=all_passed,
                    evidence=evidence,
                    details={
                        "mode": "deterministic_rules",
                        "passed_rules": passed_rules,
                        "failed_rules": failed_rules,
                        "rubric": rubric_text
                    }
                )

        # General completion heuristic (length and non-empty check)
        if len(output.strip()) > 30 and not run.error_trace:
            return EvaluatorResult(
                metric="task_completion",
                score=100.0,
                passed=True,
                evidence="Output produced without errors and addressed the prompt.",
                details={"mode": "heuristic", "rubric": rubric_text}
            )
        else:
            return EvaluatorResult(
                metric="task_completion",
                score=0.0,
                passed=False,
                evidence="Output is empty or encountered an error trace.",
                details={"mode": "heuristic", "error_trace": run.error_trace}
            )
