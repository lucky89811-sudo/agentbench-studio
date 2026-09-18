"""
Transcripts and mock payloads for testing all evaluators in isolation without network calls.
"""

LAPTOP_TASK_SCHEMA = {
    "type": "object",
    "required": ["laptops"],
    "properties": {
        "laptops": {
            "type": "array",
            "minItems": 3,
            "maxItems": 3,
            "items": {
                "type": "object",
                "required": ["model_name", "price_usd", "ram_gb", "weight_kg"],
                "properties": {
                    "model_name": {"type": "string"},
                    "price_usd": {"type": "number", "maximum": 1200},
                    "ram_gb": {"type": "integer", "minimum": 16},
                    "weight_kg": {"type": "number", "maximum": 2.0}
                }
            }
        }
    }
}

# 1. Valid laptop recommendation run with proper tool use
VALID_LAPTOP_RUN = {
    "final_output": """Here are 3 laptops matching your criteria under $1200:
```json
{
  "laptops": [
    {"model_name": "Acer Swift Go 14", "price_usd": 799.99, "ram_gb": 16, "weight_kg": 1.3},
    {"model_name": "Lenovo Yoga Slim 7", "price_usd": 949.00, "ram_gb": 16, "weight_kg": 1.4},
    {"model_name": "ASUS Zenbook 14 OLED", "price_usd": 1049.99, "ram_gb": 16, "weight_kg": 1.28}
  ]
}
```
All models have 16GB RAM and are under 1.5kg.""",
    "transcript": [
        {
            "step_index": 1,
            "role": "assistant",
            "content": "Searching for laptops under $1200 with 16GB RAM.",
            "step_latency_ms": 320.0,
            "tool_calls": [
                {
                    "id": "call_search_1",
                    "name": "web_search",
                    "arguments": {"query": "best laptops under $1200 16GB RAM 2026"}
                }
            ]
        },
        {
            "step_index": 2,
            "role": "tool",
            "step_latency_ms": 150.0,
            "tool_results": [
                {
                    "name": "web_search",
                    "content": "Acer Swift Go 14: $799.99, 16GB RAM, 1.3kg. Lenovo Yoga Slim 7: $949, 16GB RAM, 1.4kg. ASUS Zenbook 14 OLED: $1049.99, 16GB RAM, 1.28kg."
                }
            ]
        }
    ],
    "token_usage": {"input_tokens": 450, "output_tokens": 180, "total_tokens": 630},
    "latency_ms": 950.0,
    "cost_usd": 0.0029
}

# 2. Schema violation run (only 2 laptops instead of 3, missing weight_kg)
SCHEMA_VIOLATION_RUN = {
    "final_output": """```json
{
  "laptops": [
    {"model_name": "Dell Inspiron 14", "price_usd": 850.00, "ram_gb": 16},
    {"model_name": "HP Pavilion Plus", "price_usd": 920.00, "ram_gb": 16}
  ]
}
```""",
    "transcript": [
        {
            "step_index": 1,
            "role": "assistant",
            "step_latency_ms": 400.0,
            "tool_calls": [
                {"id": "c1", "name": "web_search", "arguments": {"query": "cheap laptops 16gb"}}
            ]
        }
    ],
    "token_usage": {"input_tokens": 300, "output_tokens": 90, "total_tokens": 390},
    "latency_ms": 800.0,
    "cost_usd": 0.001
}

# 3. Phantom Tool Use Run (claims search & calculator without calling any tool)
PHANTOM_TOOL_RUN = {
    "final_output": "I searched the web for 2026 budget laptops and found the HP Envy. Using the calculator tool, I calculated the discount to be 15%. Here is the recommendation.",
    "transcript": [
        {
            "step_index": 1,
            "role": "assistant",
            "content": "I searched the web for 2026 budget laptops and found the HP Envy. Using the calculator tool, I calculated the discount to be 15%.",
            "step_latency_ms": 500.0,
            "tool_calls": []  # Empty! No tools called!
        }
    ],
    "token_usage": {"input_tokens": 150, "output_tokens": 80, "total_tokens": 230},
    "latency_ms": 500.0,
    "cost_usd": 0.001
}

# 4. Ignored Tool Error Run (tool fails, agent ignores and hallucinates answer)
IGNORED_TOOL_ERROR_RUN = {
    "final_output": "The calculated total cost is $4,250.",
    "transcript": [
        {
            "step_index": 1,
            "role": "assistant",
            "tool_calls": [
                {"id": "call_calc_fail", "name": "calculator", "arguments": {"expression": "4250 / 0"}}
            ]
        },
        {
            "step_index": 2,
            "role": "tool",
            "tool_results": [
                {"name": "calculator", "is_error": True, "content": "ZeroDivisionError: division by zero"}
            ]
        },
        {
            "step_index": 3,
            "role": "assistant",
            "content": "The calculated total cost is $4,250."  # Proceeded as if call succeeded!
        }
    ],
    "token_usage": {"input_tokens": 200, "output_tokens": 50, "total_tokens": 250},
    "latency_ms": 600.0,
    "cost_usd": 0.0008
}

# 5. Citation Run with 1 valid and 1 broken link
CITATION_RUN = {
    "final_output": "According to the trial report at https://valid-source.org/paper, the efficacy was 94%. However, earlier notes from https://broken-link-example-404.org/notes suggested lower response rates.",
    "transcript": [],
    "token_usage": {"input_tokens": 200, "output_tokens": 60, "total_tokens": 260},
    "latency_ms": 400.0,
    "cost_usd": 0.0007
}
