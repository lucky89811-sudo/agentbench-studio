# AgentBench Studio

> A production-ready web platform for stress-testing and evaluating the **reliability, variance, and cost** of AI agents across repeated benchmark executions ($N$ iterations).

---

## 🎯 Core Philosophy

AgentBench Studio does not generate agent responses for end users. Instead, it stress-tests agent configurations by repeatedly running tasks ($N$ runs), capturing step-level execution transcripts, instrumenting timings and token costs, and evaluating each execution against deterministic and model-judged criteria.

**The unit of value is the evaluation report, not any single agent response.**

---

## 🏗 System Architecture

```
                               ┌─────────────────────────────┐
                               │  React + TypeScript UI      │
                               │  (Tailwind, Recharts)       │
                               └──────────────┬──────────────┘
                                              │ REST API / JSON
                               ┌──────────────▼──────────────┐
                               │     FastAPI Backend         │
                               └──────┬───────┬───────┬──────┘
                                      │       │       │
            ┌─────────────────────────┘       │       └─────────────────────────┐
            ▼                                 ▼                                 ▼
┌───────────────────────┐         ┌───────────────────────┐         ┌───────────────────────┐
│   Execution Engine    │         │   Evaluation Engine   │         │  Comparison & Report  │
│  - Multi-Provider     │         │  - Task Completion    │         │  - Scorecard Metrics  │
│  - Sandboxed Tools    │         │  - Tool Accuracy      │         │  - Distribution Stats │
│  - Bounded Batch Pool │         │  - Citation Precision │         │  - 2-Prop Z-Test      │
│  - Idempotent/Retry   │         │  - Hallucination Det. │         │  - PDF ReportLab Exp. │
└───────────────────────┘         │  - Latency & Cost     │         └───────────────────────┘
                                  └───────────────────────┘
```

---

## 🔬 Pluggable Evaluator Pipeline

1. **Task Completion Evaluator** (`task_completion.py`)
   - Deterministic schema validation against `expected_output_schema` using `jsonschema` (e.g. "exactly 3 laptops under $1200 with 16GB RAM").
   - Structured JSON LLM-judge fallback when free-text rubrics are specified.
   - Outputs `completion_rate` (bool) and `completion_score` (0–100).

2. **Tool-Call Accuracy Evaluator** (`tool_accuracy.py`)
   - Inspects transcript:
     - Verifies required tools were invoked.
     - Validates tool arguments against parameter JSON schemas.
     - Identifies disallowed tool calls.
     - Detects **ignored tool errors** (when an agent receives an error result but proceeds without retrying).
   - Outputs `tool_call_accuracy`, `tool_error_count`, `unnecessary_tool_calls`, and `ignored_tool_errors`.

3. **Citation Correctness Evaluator** (`citation.py`)
   - Extracts claims and associated URLs/citations.
   - Asynchronously probes live HTTP URLs with timeouts to detect broken links.
   - Verifies claim-source alignment against retrieved tool content.
   - Outputs `citation_precision`, `uncited_claims_count`, and `broken_link_count`.

4. **Hallucination Detector** (`hallucination.py`)
   - **Deterministic Internal Consistency Check (Phantom Tool Use)**: Identifies claims where the agent claims actions ("I searched the web", "I used the calculator") without any corresponding tool call in the transcript.
   - **Fact-Grounding Check**: Evaluates factual specifications/prices against retrieved tool content and task prompts.
   - Outputs `hallucination_rate` and `phantom_tool_use_count`.

5. **Latency & Cost Tracker** (`latency_cost.py`)
   - Instruments total latency, per-step timing breakdown, and Time-to-First-Token (TTFT).
   - Tracks exact input and output tokens against a versioned, editable pricing table.
   - Computes the headline efficiency metric: **Cost per Successful Task** (`total_batch_cost / max(1, passing_runs)`).

---

## 🚀 Quick Start

### 1. Backend Setup & Startup
```powershell
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### 2. Frontend Development Server
```powershell
cd frontend
npm run dev
```
- UI: `http://localhost:5173`

*(Note: The FastAPI backend also serves the built frontend production assets directly on `http://localhost:8000`).*

---

## 🧪 Automated Unit Tests

Run the complete isolated test suite (no external APIs required):
```powershell
cd backend
python -m pytest tests/ -v
```

Tests verify:
- Deterministic schema validation & partial credit scoring
- Phantom tool invocation detection
- Tool argument validation & ignored error tracking
- Asynchronous link liveness & broken citation detection
- Token pricing calculations & budget enforcement
- Two-proportion z-test statistical confidence calculations ($z$-score, $p$-value, 95% CI)
- End-to-end batch execution and idempotency
Live Link :-https://agentbench-studio.onrender.com
