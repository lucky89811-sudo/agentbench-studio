import json
from typing import Any
from app.tools.web_search import execute_web_search
from app.tools.fetch_url import execute_fetch_url
from app.tools.calculator import execute_calculator

AVAILABLE_TOOL_SCHEMAS = [
    {
        "name": "web_search",
        "description": "Searches the web for facts, specifications, products, and articles.",
        "parameters": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {"type": "string", "description": "The search keywords or query."}
            }
        }
    },
    {
        "name": "fetch_url",
        "description": "Fetches raw text content from a web URL.",
        "parameters": {
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {"type": "string", "description": "The URL to fetch."}
            }
        }
    },
    {
        "name": "calculator",
        "description": "Computes arithmetic and mathematical expressions safely.",
        "parameters": {
            "type": "object",
            "required": ["expression"],
            "properties": {
                "expression": {"type": "string", "description": "Arithmetic expression, e.g. '(1200 - 800) * 0.15'"}
            }
        }
    }
]

async def dispatch_tool_call(tool_name: str, arguments: dict[str, Any] | str) -> dict[str, Any]:
    """Dispatches tool execution by name."""
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except Exception:
            return {"is_error": True, "content": f"Invalid JSON string passed as arguments: {arguments}"}

    name = tool_name.lower().strip()
    if name == "web_search":
        query = arguments.get("query", "")
        return execute_web_search(query)
    elif name == "fetch_url":
        url = arguments.get("url", "")
        return await execute_fetch_url(url)
    elif name == "calculator":
        expr = arguments.get("expression", "")
        return execute_calculator(expr)
    else:
        return {"is_error": True, "content": f"Unknown tool '{tool_name}'"}
