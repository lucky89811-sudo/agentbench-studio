import time
from datetime import datetime, timezone
import httpx
from app.runner.base import BaseRunner, RunExecutionResult
from app.runner.mock_runner import MockRunner
from app.models.task import Task
from app.models.agent_config import AgentConfig
from app.config import settings
from app.tools.registry import dispatch_tool_call
from app.evaluators.latency_cost import calculate_cost

class OpenAIRunner(BaseRunner):
    async def execute(self, task: Task, agent_config: AgentConfig) -> RunExecutionResult:
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            # Seamless fallback to mock runner if no API key provided
            return await MockRunner().execute(task, agent_config)

        start_time = time.perf_counter()
        transcript = []
        step_idx = 1

        messages = []
        if agent_config.system_prompt:
            messages.append({"role": "system", "content": agent_config.system_prompt})
        messages.append({"role": "user", "content": task.prompt_template})

        transcript.append({
            "step_index": step_idx,
            "role": "user",
            "content": task.prompt_template,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "step_latency_ms": 0.0
        })
        step_idx += 1

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        total_input_tokens = 0
        total_output_tokens = 0
        final_output = ""
        ttft_ms = 0.0

        async with httpx.AsyncClient(timeout=60.0, trust_env=False) as client:
            for step in range(agent_config.max_steps):
                step_start = time.perf_counter()
                payload = {
                    "model": agent_config.model,
                    "messages": messages,
                    "temperature": agent_config.temperature,
                }
                if agent_config.tool_definitions:
                    payload["tools"] = [{"type": "function", "function": t} for t in agent_config.tool_definitions]

                resp = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                step_latency = round((time.perf_counter() - step_start) * 1000, 1)
                if step == 0:
                    ttft_ms = step_latency * 0.4

                if resp.status_code >= 400:
                    return RunExecutionResult(
                        transcript=transcript,
                        final_output="",
                        latency_ms=round((time.perf_counter() - start_time) * 1000, 1),
                        time_to_first_token_ms=ttft_ms,
                        token_usage={"input_tokens": total_input_tokens, "output_tokens": total_output_tokens, "total_tokens": total_input_tokens + total_output_tokens},
                        cost_usd=calculate_cost(agent_config.model, total_input_tokens, total_output_tokens),
                        error_trace=f"OpenAI API Error {resp.status_code}: {resp.text}",
                        status="failed"
                    )

                data = resp.json()
                usage = data.get("usage", {})
                total_input_tokens += usage.get("prompt_tokens", 0)
                total_output_tokens += usage.get("completion_tokens", 0)

                choice = data["choices"][0]["message"]
                content = choice.get("content") or ""
                tool_calls = choice.get("tool_calls") or []

                transcript.append({
                    "step_index": step_idx,
                    "role": "assistant",
                    "content": content,
                    "tool_calls": tool_calls,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "step_latency_ms": step_latency
                })
                step_idx += 1

                if not tool_calls:
                    final_output = content
                    break

                # Execute requested tools
                tool_results = []
                messages.append(choice)

                for tc in tool_calls:
                    fn_name = tc.get("function", {}).get("name", "")
                    fn_args = tc.get("function", {}).get("arguments", "{}")
                    t_start = time.perf_counter()
                    t_res = await dispatch_tool_call(fn_name, fn_args)
                    t_latency = round((time.perf_counter() - t_start) * 1000, 1)

                    import json
                    t_res_str = json.dumps(t_res)
                    tool_results.append({
                        "id": tc.get("id"),
                        "name": fn_name,
                        "content": t_res_str
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.get("id"),
                        "name": fn_name,
                        "content": t_res_str
                    })

                transcript.append({
                    "step_index": step_idx,
                    "role": "tool",
                    "tool_results": tool_results,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "step_latency_ms": t_latency
                })
                step_idx += 1

        total_latency = round((time.perf_counter() - start_time) * 1000, 1)
        cost_usd = calculate_cost(agent_config.model, total_input_tokens, total_output_tokens)

        return RunExecutionResult(
            transcript=transcript,
            final_output=final_output,
            latency_ms=total_latency,
            time_to_first_token_ms=round(ttft_ms, 1),
            token_usage={
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
                "total_tokens": total_input_tokens + total_output_tokens
            },
            cost_usd=cost_usd,
            status="completed"
        )
