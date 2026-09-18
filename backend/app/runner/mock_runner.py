import asyncio
import json
import random
import time
from datetime import datetime, timezone
from app.runner.base import BaseRunner, RunExecutionResult
from app.models.task import Task
from app.models.agent_config import AgentConfig
from app.tools.registry import dispatch_tool_call
from app.evaluators.latency_cost import calculate_cost

class MockRunner(BaseRunner):
    async def execute(self, task: Task, agent_config: AgentConfig) -> RunExecutionResult:
        start_time = time.perf_counter()
        name_lower = agent_config.name.lower()
        model_lower = agent_config.model.lower()
        prompt_lower = (task.prompt_template or "").lower()
        category = task.category or "tool-use"
        
        # Determine archetype
        is_rigorous = "rigorous" in name_lower or "strict" in name_lower or "gpt-4o" in model_lower
        is_creative = "creative" in name_lower or "fast" in name_lower
        is_fragile = "fragile" in name_lower or "flaky" in name_lower

        transcript = []
        step_idx = 1

        # Simulated initial model think & TTFT
        ttft_ms = random.uniform(180.0, 320.0) if not is_creative else random.uniform(90.0, 150.0)
        await asyncio.sleep(0.05)  # Quick non-blocking yield

        # Step 1: User task prompt
        transcript.append({
            "step_index": step_idx,
            "role": "user",
            "content": task.prompt_template,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "step_latency_ms": 0.0
        })
        step_idx += 1

        called_tools = []
        tool_results_list = []
        input_tokens = len(task.prompt_template.split()) * 4 + 120
        output_tokens = 0

        # Decide whether to execute tools based on task.required_tools and config
        required_tools = task.required_tools or []

        if required_tools and not (is_creative and random.random() < 0.35):
            # Agent calls tools
            for tool_name in required_tools:
                step_start = time.perf_counter()
                
                # Formulate arguments
                if tool_name == "web_search":
                    args = {"query": f"benchmark query for {task.name}"}
                elif tool_name == "calculator":
                    args = {"expression": "1200 * 0.85 - 50"}
                elif tool_name == "fetch_url":
                    args = {"url": "https://valid-source.org/tech/laptops-2026"}
                else:
                    args = {"input": "default"}

                # Simulate fragile tool error on first try if fragile archetype
                if is_fragile and random.random() < 0.5:
                    args = {"expression": "100 / 0"}

                tool_call_id = f"call_{tool_name}_{step_idx}"
                transcript.append({
                    "step_index": step_idx,
                    "role": "assistant",
                    "content": f"Calling {tool_name} to fulfill task criteria.",
                    "tool_calls": [{"id": tool_call_id, "name": tool_name, "arguments": args}],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "step_latency_ms": round((time.perf_counter() - step_start) * 1000 + 150.0, 1)
                })
                step_idx += 1
                output_tokens += 35

                # Execute sandboxed tool
                t_exec_start = time.perf_counter()
                res = await dispatch_tool_call(tool_name, args)
                t_exec_ms = round((time.perf_counter() - t_exec_start) * 1000 + 80.0, 1)

                transcript.append({
                    "step_index": step_idx,
                    "role": "tool",
                    "tool_results": [{"id": tool_call_id, "name": tool_name, "content": json.dumps(res)}],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "step_latency_ms": t_exec_ms
                })
                step_idx += 1
                input_tokens += 120

        # Step Final: Formulate final output
        final_start = time.perf_counter()
        
        if "laptop" in prompt_lower or task.expected_output_schema:
            if is_rigorous or (not is_creative and random.random() > 0.15):
                # Valid JSON with 3 laptops
                final_data = {
                    "laptops": [
                        {"model_name": "Acer Swift Go 14", "price_usd": 799.99, "ram_gb": 16, "weight_kg": 1.3},
                        {"model_name": "Lenovo Yoga Slim 7", "price_usd": 949.00, "ram_gb": 16, "weight_kg": 1.4},
                        {"model_name": "ASUS Zenbook 14 OLED", "price_usd": 1049.99, "ram_gb": 16, "weight_kg": 1.28}
                    ]
                }
                final_output = f"Here are 3 recommended laptops matching all budget and weight criteria:\n```json\n{json.dumps(final_data, indent=2)}\n```\nAll specifications verified at https://valid-source.org/tech/laptops-2026."
            else:
                # Schema violation or missing laptop
                final_data = {
                    "laptops": [
                        {"model_name": "Dell Inspiron 14", "price_usd": 899.99, "ram_gb": 16}
                    ]
                }
                final_output = f"I searched the web and found these laptops:\n```json\n{json.dumps(final_data, indent=2)}\n```"
        
        elif "clinical" in prompt_lower or category == "citation":
            if is_rigorous:
                final_output = "According to the phase 3 clinical trial report at https://valid-source.org/medical/oncology-pd1-2025, overall survival was 71.4% at 24 months in the combination arm vs 58.2% with monotherapy (p=0.002)."
            else:
                final_output = "I checked the medical database and found 85% survival rate at https://broken-link-example-404.org/oncology-data."

        elif "financial" in prompt_lower or category == "tool-use":
            if not is_fragile:
                final_output = "Based on our calculation and earnings data from https://valid-source.org/finance/tech-q3-2026, Q3 cloud division revenue grew 28% to $12.4B, generating $4.1B in free cash flow."
            else:
                final_output = "I used the calculator tool to compute the growth rate which is 45%."

        else:
            final_output = f"Completed the requested task '{task.name}' successfully adhering to the defined criteria."

        # Add phantom tool claim if creative archetype skipped tools
        if is_creative and not required_tools:
            final_output = "I searched online and verified the parameters. " + final_output

        transcript.append({
            "step_index": step_idx,
            "role": "assistant",
            "content": final_output,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "step_latency_ms": round((time.perf_counter() - final_start) * 1000 + 250.0, 1)
        })

        output_tokens += len(final_output.split()) * 3 + 80
        total_latency_ms = round((time.perf_counter() - start_time) * 1000 + 400.0, 1)
        cost_usd = calculate_cost(agent_config.model, input_tokens, output_tokens)

        return RunExecutionResult(
            transcript=transcript,
            final_output=final_output,
            latency_ms=total_latency_ms,
            time_to_first_token_ms=round(ttft_ms, 1),
            token_usage={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens
            },
            cost_usd=cost_usd,
            status="completed"
        )
