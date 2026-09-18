import re
from typing import Any
from app.evaluators.base import BaseEvaluator
from app.models.task import Task
from app.models.agent_config import AgentConfig
from app.models.run import Run
from app.schemas.evaluation import EvaluatorResult

# Regular expression mappings for claimed tool activities
TOOL_CLAIM_PATTERNS = [
    {
        "tool_type": "web_search",
        "tool_names": {"web_search", "search", "google_search", "bing_search"},
        "patterns": [
            r"(?:i\s+(?:have\s+)?searched\s+(?:the\s+web|online|google|bing|the\s+internet)?\s*(?:for|about)?)",
            r"(?:according\s+to\s+(?:my\s+)?(?:web\s+)?search(?:\s+results)?)",
            r"(?:based\s+on\s+(?:my\s+)?(?:web\s+)?search(?:\s+results)?)",
            r"(?:i\s+(?:looked\s+up|queried\s+the\s+web\s+for))",
            r"(?:my\s+search\s+(?:revealed|returned|shows))",
        ]
    },
    {
        "tool_type": "fetch_url",
        "tool_names": {"fetch_url", "fetch_webpage", "browse", "read_url_content"},
        "patterns": [
            r"(?:i\s+(?:have\s+)?(?:fetched|visited|opened|browsed|accessed)\s+(?:the\s+(?:page|url|website|article)|https?://))",
            r"(?:i\s+checked\s+the\s+(?:website|url|link|page))",
            r"(?:upon\s+reading\s+the\s+(?:webpage|url|article))",
        ]
    },
    {
        "tool_type": "calculator",
        "tool_names": {"calculator", "calc", "math_eval", "compute"},
        "patterns": [
            r"(?:i\s+(?:have\s+)?(?:used\s+(?:the\s+)?calculator|calculated\s+using\s+(?:the\s+)?calculator))",
            r"(?:using\s+the\s+calculator\s+tool)",
            r"(?:i\s+computed\s+with\s+(?:the\s+)?calculator)",
            r"(?:the\s+calculator\s+returned)",
        ]
    },
    {
        "tool_type": "code_interpreter",
        "tool_names": {"code_interpreter", "python", "run_command", "bash"},
        "patterns": [
            r"(?:i\s+(?:have\s+)?(?:executed|ran)\s+(?:the\s+)?(?:python\s+code|script|command))",
            r"(?:running\s+the\s+code\s+gave)",
            r"(?:the\s+code\s+output\s+showed)",
        ]
    },
]

class HallucinationDetector(BaseEvaluator):
    @property
    def name(self) -> str:
        return "hallucination_detector"

    async def evaluate(self, task: Task, agent_config: AgentConfig, run: Run) -> EvaluatorResult:
        transcript = run.full_transcript or []
        output = run.final_output or ""

        # 1. Extract all actual tool calls from transcript
        actual_tools_called = set()
        tool_results_content = []

        for step in transcript:
            # Check tool_calls in step
            calls = step.get("tool_calls", []) or []
            for call in calls:
                tool_name = call.get("name") or call.get("function", {}).get("name", "")
                if tool_name:
                    actual_tools_called.add(tool_name.lower())

            # Check tool_results in step
            results = step.get("tool_results", []) or []
            for res in results:
                tool_name = res.get("name") or res.get("tool_name", "")
                if tool_name:
                    actual_tools_called.add(tool_name.lower())
                tool_results_content.append(str(res.get("content") or res.get("output") or ""))

        # 2. Extract text spoken by assistant (both intermediate messages and final output)
        assistant_texts = []
        for step in transcript:
            if step.get("role") == "assistant" and step.get("content"):
                assistant_texts.append(step["content"])
        if output and output not in assistant_texts:
            assistant_texts.append(output)

        combined_assistant_text = "\n".join(assistant_texts)

        # 3. Deterministic Phantom Tool Use Detection
        phantom_claims = []
        for claim_def in TOOL_CLAIM_PATTERNS:
            expected_names = claim_def["tool_names"]
            called_any = bool(actual_tools_called.intersection(expected_names))

            for pattern in claim_def["patterns"]:
                matches = re.finditer(pattern, combined_assistant_text, re.IGNORECASE)
                for match in matches:
                    if not called_any:
                        # Extract the surrounding sentence for evidence
                        start = max(0, match.start() - 40)
                        end = min(len(combined_assistant_text), match.end() + 60)
                        snippet = combined_assistant_text[start:end].replace("\n", " ").strip()
                        
                        phantom_claims.append({
                            "claimed_tool_type": claim_def["tool_type"],
                            "evidence_snippet": f"...{snippet}...",
                            "matched_phrase": match.group(0),
                            "actual_tools_called": list(actual_tools_called)
                        })

        phantom_count = len(phantom_claims)

        # 4. Fact-Grounding Check
        # Extract numerical specs, prices, or definite factual claims
        # and test if they have grounding in tool results or task prompt
        claimed_specs = re.findall(r"\$\d+(?:\.\d+)?|\b\d+(?:\.\d+)?\s*(?:gb|tb|ghz|mah|hours|inches|lbs|kg)\b", combined_assistant_text, re.IGNORECASE)
        total_factual_tokens = max(1, len(claimed_specs) + phantom_count)
        
        ungrounded_specs = []
        all_grounded_text = (" ".join(tool_results_content) + " " + (task.prompt_template or "") + " " + str(task.expected_output_schema or "")).lower()

        for spec in claimed_specs:
            clean_spec = spec.strip().lower()
            # Also extract just the number part
            num_part = re.search(r"\d+(?:\.\d+)?", clean_spec)
            num_str = num_part.group(0) if num_part else clean_spec
            
            if clean_spec not in all_grounded_text and num_str not in all_grounded_text and len(tool_results_content) > 0:
                ungrounded_specs.append(spec)

        # Compute hallucination rate
        total_claims_evaluated = max(1, len(claimed_specs) + phantom_count)
        hallucinated_items = phantom_count + len(ungrounded_specs)
        hallucination_rate = min(100.0, round((hallucinated_items / total_claims_evaluated) * 100.0, 1))

        passed = phantom_count == 0 and hallucination_rate <= 25.0
        score = max(0.0, round(100.0 - hallucination_rate, 1))

        evidence_parts = []
        if phantom_count > 0:
            evidence_parts.append(f"Detected {phantom_count} phantom tool invocation(s): agent claimed actions without calling the tool.")
        if ungrounded_specs:
            evidence_parts.append(f"{len(ungrounded_specs)} ungrounded fact/spec claims found.")
        if not evidence_parts:
            evidence_parts.append("No phantom tool calls detected and claims were grounded in observed tool outputs.")

        return EvaluatorResult(
            metric="hallucination_detector",
            score=score,
            passed=passed,
            evidence=" ".join(evidence_parts),
            details={
                "phantom_tool_use_count": phantom_count,
                "phantom_claims": phantom_claims,
                "hallucination_rate": hallucination_rate,
                "ungrounded_specs": ungrounded_specs,
                "total_claims_evaluated": total_claims_evaluated,
                "actual_tools_called": list(actual_tools_called)
            }
        )
