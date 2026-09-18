import json
from typing import Any
import jsonschema
from app.evaluators.base import BaseEvaluator
from app.models.task import Task
from app.models.agent_config import AgentConfig
from app.models.run import Run
from app.schemas.evaluation import EvaluatorResult

class ToolAccuracyEvaluator(BaseEvaluator):
    @property
    def name(self) -> str:
        return "tool_accuracy"

    async def evaluate(self, task: Task, agent_config: AgentConfig, run: Run) -> EvaluatorResult:
        transcript = run.full_transcript or []
        required_tools = [t.lower() for t in (task.required_tools or [])]
        allowed_tool_defs = agent_config.tool_definitions or []
        allowed_tools_map = {}
        for td in allowed_tool_defs:
            if isinstance(td, dict):
                t_name = td.get("name") or td.get("function", {}).get("name")
                if t_name:
                    allowed_tools_map[t_name.lower()] = td

        calls_recorded = []
        tools_called_set = set()
        schema_invalid_calls = []
        disallowed_calls = []
        tool_errors = []
        ignored_errors = []

        # Walk through transcript steps
        for step_idx, step in enumerate(transcript):
            tool_calls = step.get("tool_calls", []) or []
            tool_results = step.get("tool_results", []) or []

            for call in tool_calls:
                name = (call.get("name") or call.get("function", {}).get("name", "")).lower()
                args = call.get("arguments") or call.get("function", {}).get("arguments", {})
                call_id = call.get("id", f"call_{len(calls_recorded)}")

                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except Exception:
                        schema_invalid_calls.append({"step": step_idx, "tool": name, "reason": "Arguments string was invalid JSON"})
                        args = {}

                tools_called_set.add(name)
                calls_recorded.append({"step": step_idx, "id": call_id, "name": name, "arguments": args})

                # Check disallowed tools
                if allowed_tools_map and name not in allowed_tools_map:
                    disallowed_calls.append({"step": step_idx, "tool": name, "reason": "Tool not in allowed tool definitions"})

                # Check argument schema if available in config
                if name in allowed_tools_map:
                    def_obj = allowed_tools_map[name]
                    param_schema = def_obj.get("parameters") or def_obj.get("function", {}).get("parameters")
                    if param_schema and isinstance(param_schema, dict) and isinstance(args, dict):
                        try:
                            jsonschema.validate(args, param_schema)
                        except jsonschema.ValidationError as ve:
                            schema_invalid_calls.append({"step": step_idx, "tool": name, "error": str(ve.message)})

            # Check tool results for errors
            for res in tool_results:
                is_error = res.get("is_error", False) or "error" in str(res.get("content", "")).lower() or "exception" in str(res.get("content", "")).lower()
                if is_error:
                    tool_name = (res.get("name") or res.get("tool_name", "")).lower()
                    tool_errors.append({
                        "step": step_idx,
                        "tool": tool_name,
                        "error_message": str(res.get("content") or res.get("output", ""))[:200]
                    })
                    
                    # Look ahead to see if the agent retried or handled the error
                    retried = False
                    for next_step in transcript[step_idx + 1:]:
                        next_calls = next_step.get("tool_calls", []) or []
                        for nc in next_calls:
                            nc_name = (nc.get("name") or nc.get("function", {}).get("name", "")).lower()
                            if nc_name == tool_name:
                                retried = True
                                break
                        if retried:
                            break
                    
                    if not retried and len(transcript) > step_idx + 1:
                        ignored_errors.append({
                            "step": step_idx,
                            "tool": tool_name,
                            "note": "Agent encountered tool error but did not retry or adapt in subsequent steps."
                        })

        # Required tools check
        missing_required = [t for t in required_tools if t not in tools_called_set]

        total_calls = len(calls_recorded)
        total_defects = len(schema_invalid_calls) + len(disallowed_calls) + len(ignored_errors) + (len(missing_required) * 2)

        if total_calls == 0 and len(required_tools) > 0:
            accuracy_score = 0.0
            passed = False
        elif total_calls == 0 and len(required_tools) == 0:
            accuracy_score = 100.0
            passed = True
        else:
            defect_penalty = (total_defects / max(1, total_calls)) * 50.0
            accuracy_score = max(0.0, round(100.0 - defect_penalty, 1))
            passed = accuracy_score >= 80.0 and len(missing_required) == 0 and len(ignored_errors) == 0

        evidence_list = []
        if missing_required:
            evidence_list.append(f"Missing required tools: {', '.join(missing_required)}.")
        if disallowed_calls:
            evidence_list.append(f"Called {len(disallowed_calls)} disallowed tool(s).")
        if schema_invalid_calls:
            evidence_list.append(f"{len(schema_invalid_calls)} call(s) failed argument schema validation.")
        if ignored_errors:
            evidence_list.append(f"Ignored {len(ignored_errors)} tool error(s) without retry.")
        if not evidence_list:
            evidence_list.append(f"All {total_calls} tool call(s) were valid, required tools invoked, and errors handled properly.")

        return EvaluatorResult(
            metric="tool_accuracy",
            score=accuracy_score,
            passed=passed,
            evidence=" ".join(evidence_list),
            details={
                "total_tool_calls": total_calls,
                "tool_call_accuracy": accuracy_score,
                "tool_error_count": len(tool_errors),
                "unnecessary_tool_calls": len(disallowed_calls),
                "ignored_tool_errors": len(ignored_errors),
                "schema_invalid_calls": schema_invalid_calls,
                "missing_required_tools": missing_required,
                "called_tools": list(tools_called_set),
            }
        )
