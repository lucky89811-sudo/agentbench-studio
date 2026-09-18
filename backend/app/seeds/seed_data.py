from sqlalchemy.orm import Session
from app.models.task import Task
from app.models.agent_config import AgentConfig
from app.models.pricing import PricingModel
from app.tools.registry import AVAILABLE_TOOL_SCHEMAS

LAPTOP_SCHEMA = {
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

SEED_TASKS = [
    {
        "id": "task-laptop-matrix",
        "name": "Laptop Recommendation Matrix",
        "category": "tool-use",
        "prompt_template": "Find exactly 3 laptops under $1200 with at least 16GB RAM and weight under 2.0kg. Output strictly as JSON containing the 'laptops' array with model_name, price_usd, ram_gb, and weight_kg.",
        "expected_output_schema": LAPTOP_SCHEMA,
        "success_criteria": {
            "rubric": "Must provide exactly 3 laptops under $1200, 16GB RAM, under 2kg in valid JSON format.",
            "rules": ["model_name", "price_usd", "ram_gb", "weight_kg"]
        },
        "required_tools": ["web_search"],
        "budget_constraints": {"max_latency_ms": 6000.0, "max_cost_usd": 0.05}
    },
    {
        "id": "task-clinical-citation",
        "name": "Clinical Trial Efficacy Citation Check",
        "category": "citation",
        "prompt_template": "Summarize the phase 3 clinical trial results for NCT04512399 in advanced melanoma, citing the exact published URL and reporting the 24-month overall survival rate.",
        "expected_output_schema": None,
        "success_criteria": {
            "rubric": "Must include valid link to study, quote survival rate of 71.4%, and cite author/trial ID accurately.",
            "rules": ["71.4%", "NCT04512399"]
        },
        "required_tools": ["web_search", "fetch_url"],
        "budget_constraints": {"max_latency_ms": 7000.0, "max_cost_usd": 0.05}
    },
    {
        "id": "task-financial-analysis",
        "name": "Financial Portfolio & Free Cash Flow Calculator",
        "category": "tool-use",
        "prompt_template": "Retrieve tech sector Q3 cloud division revenue ($12.4B) and use the calculator to compute free cash flow margin given free cash flow was $4.1B.",
        "expected_output_schema": None,
        "success_criteria": {
            "rubric": "Must call calculator tool to compute 4.1 / 12.4 = 33.06%, and cite Q3 report.",
            "rules": ["calculator", "33%"]
        },
        "required_tools": ["calculator", "web_search"],
        "budget_constraints": {"max_latency_ms": 5000.0, "max_cost_usd": 0.04}
    },
    {
        "id": "task-coding-audit",
        "name": "Algorithmic Sorting Edge Case Audit",
        "category": "coding",
        "prompt_template": "Compare Merge Sort vs Quick Sort algorithmic complexity on nearly-sorted data, identifying worst-case recursion depths and stability differences.",
        "expected_output_schema": None,
        "success_criteria": {
            "rubric": "Must accurately identify O(n log n) vs O(n^2) worst case for quicksort with naive pivot.",
            "rules": ["O(n log n)", "O(n^2)", "stability"]
        },
        "required_tools": [],
        "budget_constraints": {"max_latency_ms": 4000.0, "max_cost_usd": 0.03}
    }
]

SEED_CONFIGS = [
    {
        "id": "config-rigorous-v1",
        "name": "Rigorous Fact-Checked Agent",
        "description": "Evidence-grounded agent with strict tool-calling discipline and JSON schema compliance.",
        "provider": "mock",
        "model": "gpt-4o",
        "prompt_version": "v1.2.0",
        "temperature": 0.0,
        "system_prompt": "You are a meticulous, evidence-driven verification agent. Always verify claims using authorized tools before responding. Adhere strictly to output JSON schemas. Never invent citations, URLs, or tool results.",
        "tool_definitions": AVAILABLE_TOOL_SCHEMAS,
        "max_steps": 8
    },
    {
        "id": "config-creative-fast-v1",
        "name": "Fast & Creative Agent",
        "description": "Conversational, low-latency agent prone to skipping tool calls and hallucinating unsupported claims.",
        "provider": "mock",
        "model": "gpt-4o-mini",
        "prompt_version": "v0.9.0",
        "temperature": 0.7,
        "system_prompt": "You are a fast, conversational assistant. Provide prompt answers and summarize quickly. Feel free to generalize and extrapolate without verifying every minor detail.",
        "tool_definitions": AVAILABLE_TOOL_SCHEMAS[:2],
        "max_steps": 6
    },
    {
        "id": "config-fragile-flaky-v1",
        "name": "Fragile & Flaky Agent",
        "description": "Demonstrates error recovery failures, ignored tool errors, and high score variance.",
        "provider": "mock",
        "model": "mock-fragile",
        "prompt_version": "v0.5.1",
        "temperature": 0.9,
        "system_prompt": "You are an experimental assistant prone to ignoring tool exceptions and hallucinating fake outcomes.",
        "tool_definitions": AVAILABLE_TOOL_SCHEMAS,
        "max_steps": 5
    }
]

SEED_PRICING = [
    {"model_name": "gpt-4o", "provider": "openai", "input_price_per_m": 2.50, "output_price_per_m": 10.00},
    {"model_name": "gpt-4o-mini", "provider": "openai", "input_price_per_m": 0.15, "output_price_per_m": 0.60},
    {"model_name": "claude-sonnet-4-6", "provider": "anthropic", "input_price_per_m": 3.00, "output_price_per_m": 15.00},
    {"model_name": "gemini-1.5-pro", "provider": "google", "input_price_per_m": 1.25, "output_price_per_m": 5.00},
    {"model_name": "gemini-1.5-flash", "provider": "google", "input_price_per_m": 0.075, "output_price_per_m": 0.30},
    {"model_name": "mock-fragile", "provider": "mock", "input_price_per_m": 0.0, "output_price_per_m": 0.0},
]

def seed_database(db: Session):
    # Seed Tasks
    for t_data in SEED_TASKS:
        existing = db.query(Task).filter(Task.id == t_data["id"]).first()
        if not existing:
            t = Task(**t_data)
            db.add(t)

    # Seed Configs
    for c_data in SEED_CONFIGS:
        existing = db.query(AgentConfig).filter(AgentConfig.id == c_data["id"]).first()
        if not existing:
            c = AgentConfig(**c_data)
            db.add(c)

    # Seed Pricing
    for p_data in SEED_PRICING:
        existing = db.query(PricingModel).filter(PricingModel.model_name == p_data["model_name"]).first()
        if not existing:
            p = PricingModel(**p_data)
            db.add(p)

    db.commit()
