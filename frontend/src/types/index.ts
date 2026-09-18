export interface Task {
  id: string;
  name: string;
  category: string;
  prompt_template: string;
  expected_output_schema?: any;
  success_criteria: {
    rubric?: string;
    rules?: string[];
    [key: string]: any;
  };
  required_tools: string[];
  budget_constraints?: {
    max_latency_ms?: number;
    max_cost_usd?: number;
    [key: string]: any;
  };
  created_at: string;
  updated_at: string;
}

export interface AgentConfig {
  id: string;
  name: string;
  description?: string;
  provider: string;
  model: string;
  system_prompt: string;
  prompt_version: string;
  temperature: number;
  tool_definitions: any[];
  max_steps: number;
  created_at: string;
  updated_at: string;
}

export interface Evaluation {
  id: string;
  run_id: string;
  overall_passed: boolean;
  overall_score: number;
  completion_rate: boolean;
  completion_score: number;
  completion_details: any;
  tool_call_accuracy: number;
  tool_error_count: number;
  unnecessary_tool_calls: number;
  ignored_tool_errors: number;
  tool_details: any;
  citation_precision: number;
  uncited_claims_count: number;
  broken_link_count: number;
  citation_details: any;
  hallucination_rate: number;
  phantom_tool_use_count: number;
  hallucination_details: any;
  latency_details: any;
  cost_details: any;
  raw_evaluator_results: any[];
  created_at: string;
}

export interface Run {
  id: string;
  batch_id?: string;
  task_id: string;
  agent_config_id: string;
  run_index: number;
  status: string;
  full_transcript: Array<{
    step_index: number;
    role: string;
    content?: string;
    tool_calls?: any[];
    tool_results?: any[];
    step_latency_ms?: number;
    timestamp?: string;
    defect_flags?: string[];
  }>;
  final_output: string;
  latency_ms: number;
  time_to_first_token_ms: number;
  token_usage: {
    input_tokens: number;
    output_tokens: number;
    total_tokens: number;
  };
  cost_usd: number;
  error_trace?: string;
  created_at: string;
  completed_at?: string;
  evaluation?: Evaluation;
}

export interface RunBatch {
  id: string;
  task_id: string;
  agent_config_id: string;
  n_runs: number;
  concurrency_limit: number;
  status: string;
  completed_runs_count: number;
  failed_runs_count: number;
  summary_metrics?: {
    overall_pass_rate: number;
    completion_rate: number;
    tool_call_accuracy: number;
    citation_precision: number;
    hallucination_rate: number;
    avg_score: number;
    score_variance: number;
    score_std_dev: number;
    avg_latency_ms: number;
    latency_variance: number;
    latency_std_dev: number;
    avg_cost_usd: number;
    total_cost_usd: number;
    cost_per_successful_task: number;
    passing_runs_count: number;
    total_runs_count: number;
  };
  created_at: string;
  completed_at?: string;
  task?: Task;
  agent_config?: AgentConfig;
  runs?: Run[];
}

export interface EvaluationReport {
  batch_id: string;
  status: string;
  created_at: string;
  completed_at?: string;
  task: {
    id: string;
    name: string;
    category: string;
    prompt_template: string;
  };
  agent_config: {
    id: string;
    name: string;
    model: string;
    provider: string;
    prompt_version: string;
  };
  scorecard: {
    overall_pass_rate: number;
    completion_rate: number;
    tool_call_accuracy: number;
    citation_precision: number;
    hallucination_rate: number;
    avg_score: number;
    score_variance: number;
    score_std_dev: number;
    avg_latency_ms: number;
    latency_std_dev: number;
    avg_cost_usd: number;
    total_cost_usd: number;
    cost_per_successful_task: number;
    passing_runs_count: number;
    total_runs_count: number;
  };
  distributions: {
    score: { min: number; p25: number; p50: number; p75: number; max: number; mean: number; std_dev: number };
    latency: { min: number; p25: number; p50: number; p75: number; max: number; mean: number; std_dev: number };
    tokens: { min: number; p25: number; p50: number; p75: number; max: number; mean: number; std_dev: number };
    cost: { min: number; p25: number; p50: number; p75: number; max: number; mean: number; std_dev: number };
    raw_run_scores: Array<{
      run_index: number;
      score: number;
      latency_ms: number;
      cost_usd: number;
      passed: boolean;
    }>;
  };
  worst_runs: Array<{
    run_id: string;
    run_index: number;
    overall_score: number;
    overall_passed: boolean;
    latency_ms: number;
    cost_usd: number;
    final_output: string;
    failure_reasons: string[];
    evaluator_scores: any;
    transcript: any[];
  }>;
  historical_trend: Array<{
    batch_id: string;
    created_at: string;
    pass_rate: number;
    avg_score: number;
    avg_latency_ms: number;
    cost_per_successful_task: number;
  }>;
}

export interface Comparison {
  id: string;
  name: string;
  task_id: string;
  batch_ids: string[];
  metrics_matrix: {
    configs: Array<{
      batch_id: string;
      agent_config_id: string;
      agent_name: string;
      model: string;
      n_runs: number;
      overall_pass_rate: number;
      completion_rate: number;
      tool_call_accuracy: number;
      citation_precision: number;
      hallucination_rate: number;
      avg_score: number;
      avg_latency_ms: number;
      cost_per_successful_task: number;
      passing_runs_count: number;
    }>;
  };
  statistical_confidence: {
    z_score?: number;
    p_value?: number;
    is_significant?: boolean;
    ci_95?: [number, number];
    difference?: number;
    comparison_pair?: string;
  };
  created_at: string;
}

export interface PricingModel {
  id: string;
  model_name: string;
  provider: string;
  input_price_per_m: number;
  output_price_per_m: number;
  updated_at: string;
}
