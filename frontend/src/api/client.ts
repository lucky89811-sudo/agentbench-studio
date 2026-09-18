import { Task, AgentConfig, RunBatch, Run, EvaluationReport, Comparison, PricingModel } from '../types';

const API_BASE = '/api';

export const api = {
  // Tasks
  getTasks: async (): Promise<Task[]> => {
    const res = await fetch(`${API_BASE}/tasks`);
    if (!res.ok) throw new Error('Failed to fetch tasks');
    return res.json();
  },
  createTask: async (data: Partial<Task>): Promise<Task> => {
    const res = await fetch(`${API_BASE}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create task');
    return res.json();
  },

  // Agent Configs
  getConfigs: async (): Promise<AgentConfig[]> => {
    const res = await fetch(`${API_BASE}/agent-configs`);
    if (!res.ok) throw new Error('Failed to fetch agent configs');
    return res.json();
  },
  createConfig: async (data: Partial<AgentConfig>): Promise<AgentConfig> => {
    const res = await fetch(`${API_BASE}/agent-configs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create agent config');
    return res.json();
  },

  // Batches & Runs
  startBatch: async (task_id: string, agent_config_id: string, n_runs: number = 5, concurrency_limit: number = 3): Promise<RunBatch> => {
    const res = await fetch(`${API_BASE}/runs/batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task_id, agent_config_id, n_runs, concurrency_limit }),
    });
    if (!res.ok) throw new Error('Failed to start batch');
    return res.json();
  },
  getBatches: async (): Promise<RunBatch[]> => {
    const res = await fetch(`${API_BASE}/runs/batch`);
    if (!res.ok) throw new Error('Failed to fetch batches');
    return res.json();
  },
  getBatch: async (id: string): Promise<RunBatch> => {
    const res = await fetch(`${API_BASE}/runs/batch/${id}`);
    if (!res.ok) throw new Error('Failed to fetch batch');
    return res.json();
  },
  getRun: async (id: string): Promise<Run> => {
    const res = await fetch(`${API_BASE}/runs/${id}`);
    if (!res.ok) throw new Error('Failed to fetch run');
    return res.json();
  },

  // Reports
  getReport: async (batch_id: string): Promise<EvaluationReport> => {
    const res = await fetch(`${API_BASE}/reports/${batch_id}`);
    if (!res.ok) throw new Error('Failed to fetch report');
    return res.json();
  },
  getReportPdfUrl: (batch_id: string): string => {
    return `${API_BASE}/reports/${batch_id}/pdf`;
  },

  // Comparisons
  getComparisons: async (): Promise<Comparison[]> => {
    const res = await fetch(`${API_BASE}/comparisons`);
    if (!res.ok) throw new Error('Failed to fetch comparisons');
    return res.json();
  },
  createComparison: async (task_id: string, agent_config_ids: string[], n_runs_per_config: number = 5): Promise<Comparison> => {
    const res = await fetch(`${API_BASE}/comparisons`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task_id, agent_config_ids, n_runs_per_config }),
    });
    if (!res.ok) throw new Error('Failed to create comparison');
    return res.json();
  },

  // Pricing
  getPricing: async (): Promise<PricingModel[]> => {
    const res = await fetch(`${API_BASE}/pricing`);
    if (!res.ok) throw new Error('Failed to fetch pricing');
    return res.json();
  },
  updatePricing: async (id: string, input_price_per_m: number, output_price_per_m: number): Promise<PricingModel> => {
    const res = await fetch(`${API_BASE}/pricing/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input_price_per_m, output_price_per_m }),
    });
    if (!res.ok) throw new Error('Failed to update pricing');
    return res.json();
  },
};
