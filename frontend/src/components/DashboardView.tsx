import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  ShieldCheck, 
  Clock, 
  DollarSign, 
  Play, 
  ArrowRight, 
  Download, 
  CheckCircle2, 
  AlertCircle, 
  Layers, 
  Cpu, 
  RefreshCw,
  Sparkles
} from 'lucide-react';
import { RunBatch, Task, AgentConfig } from '../types';
import { api } from '../api/client';

interface DashboardViewProps {
  onOpenNewBatch: () => void;
  onViewReport: (batchId: string) => void;
  onNavigateTab: (tab: string) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  onOpenNewBatch,
  onViewReport,
  onNavigateTab
}) => {
  const [batches, setBatches] = useState<RunBatch[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [configs, setConfigs] = useState<AgentConfig[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [batchData, taskData, configData] = await Promise.all([
        api.getBatches(),
        api.getTasks(),
        api.getConfigs()
      ]);
      setBatches(batchData);
      setTasks(taskData);
      setConfigs(configData);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Compute aggregate platform stats
  const completedBatches = batches.filter(b => b.status === 'completed');
  const totalRunsCount = completedBatches.reduce((acc, b) => acc + (b.summary_metrics?.total_runs_count || b.n_runs), 0);
  const totalPassingCount = completedBatches.reduce((acc, b) => acc + (b.summary_metrics?.passing_runs_count || 0), 0);
  const avgPassRate = totalRunsCount > 0 ? Math.round((totalPassingCount / totalRunsCount) * 100) : 0;
  
  const avgLatency = completedBatches.length > 0
    ? Math.round(completedBatches.reduce((acc, b) => acc + (b.summary_metrics?.avg_latency_ms || 0), 0) / completedBatches.length)
    : 0;

  const totalCost = completedBatches.reduce((acc, b) => acc + (b.summary_metrics?.total_cost_usd || 0), 0);
  const costPerSuccess = totalPassingCount > 0 ? (totalCost / totalPassingCount) : 0;

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
      
      {/* Banner / Hero */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-900/90 to-cyan-950/40 border border-slate-800 rounded-3xl p-8 relative overflow-hidden shadow-2xl">
        <div className="relative z-10 max-w-3xl space-y-3">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Agent Reliability & Stress-Testing Platform</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl">
            Evaluate AI Agent Reliability at Scale
          </h1>
          <p className="text-slate-300 text-sm leading-relaxed">
            AgentBench Studio executes repetitive $N$-run stress tests across configurable model, prompt, and tool setups. 
            Capture step-by-step transcripts, audit hallucination rates and phantom tool calls, verify citations, and calculate quantitative reliability reports.
          </p>
          <div className="flex items-center space-x-4 pt-2">
            <button
              onClick={onOpenNewBatch}
              className="flex items-center space-x-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-semibold px-5 py-2.5 rounded-xl shadow-lg shadow-cyan-500/25 transition active:scale-95"
            >
              <Play className="w-4 h-4 fill-current" />
              <span>Launch Reliability Batch</span>
            </button>
            <button
              onClick={() => onNavigateTab('comparisons')}
              className="flex items-center space-x-2 bg-slate-800/80 hover:bg-slate-700/80 text-slate-200 text-xs font-semibold px-4 py-2.5 rounded-xl border border-slate-700 transition"
            >
              <span>Compare 2+ Agents</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
        <div className="absolute -right-16 -bottom-16 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>
      </div>

      {/* Aggregate Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Total Iterations Tested</span>
            <Activity className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-3xl font-black text-white">{totalRunsCount} <span className="text-xs text-slate-500 font-normal">runs</span></p>
          <div className="text-[11px] text-slate-400 mt-1">Across {batches.length} benchmark batches</div>
          <div className="absolute bottom-0 left-0 right-0 h-1 bg-cyan-500"></div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Aggregate Pass Rate</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-3xl font-black text-emerald-400">{avgPassRate}%</p>
          <div className="text-[11px] text-slate-400 mt-1">{totalPassingCount} successful runs</div>
          <div className="absolute bottom-0 left-0 right-0 h-1 bg-emerald-500"></div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
            <span>Average Total Latency</span>
            <Clock className="w-4 h-4 text-purple-400" />
          </div>
          <p className="text-3xl font-black text-purple-400">{avgLatency} <span className="text-xs text-slate-500 font-normal">ms</span></p>
          <div className="text-[11px] text-slate-400 mt-1">Instrumented model & tool time</div>
          <div className="absolute bottom-0 left-0 right-0 h-1 bg-purple-500"></div>
        </div>

        <div className="bg-gradient-to-br from-cyan-950/40 to-slate-900 border border-cyan-500/30 p-5 rounded-2xl relative overflow-hidden shadow-lg shadow-cyan-950/20">
          <div className="flex items-center justify-between text-cyan-300 text-xs mb-1">
            <span className="font-semibold">Cost / Successful Task</span>
            <DollarSign className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-3xl font-black text-cyan-300">${costPerSuccess.toFixed(4)}</p>
          <div className="text-[11px] text-cyan-400/70 mt-1 font-medium">Efficiency headline metric</div>
          <div className="absolute bottom-0 left-0 right-0 h-1 bg-cyan-400"></div>
        </div>

      </div>

      {/* Batches Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-white">Recent Evaluation Batches</h2>
            <p className="text-xs text-slate-400">Stress-test runs and aggregated reliability scorecards</p>
          </div>
          <button 
            onClick={loadData}
            className="flex items-center space-x-1.5 text-xs text-slate-400 hover:text-white px-3 py-1.5 rounded-lg hover:bg-slate-800 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
        </div>

        {batches.length === 0 ? (
          <div className="p-12 text-center">
            <Activity className="w-10 h-10 text-slate-600 mx-auto mb-3" />
            <h3 className="text-sm font-semibold text-white">No Evaluation Batches Yet</h3>
            <p className="text-xs text-slate-400 max-w-sm mx-auto mt-1 mb-4">
              Launch your first repeated benchmark batch to start stress-testing an agent configuration.
            </p>
            <button
              onClick={onOpenNewBatch}
              className="bg-cyan-500 hover:bg-cyan-400 text-white text-xs font-semibold px-4 py-2 rounded-xl"
            >
              Start First Batch
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="px-5 py-3 font-semibold">Benchmark Task</th>
                  <th className="px-4 py-3 font-semibold">Agent Config</th>
                  <th className="px-4 py-3 font-semibold text-center">Iterations (N)</th>
                  <th className="px-4 py-3 font-semibold text-center">Status</th>
                  <th className="px-4 py-3 font-semibold text-center">Pass Rate</th>
                  <th className="px-4 py-3 font-semibold text-center">Score</th>
                  <th className="px-4 py-3 font-semibold text-center">Avg Latency</th>
                  <th className="px-4 py-3 font-semibold text-center">Cost / Success</th>
                  <th className="px-5 py-3 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-200">
                {batches.map((b) => {
                  const sm = (b.summary_metrics || {}) as any;
                  const isDone = b.status === 'completed';
                  return (
                    <tr key={b.id} className="hover:bg-slate-800/40 transition">
                      <td className="px-5 py-3.5 font-semibold text-white">
                        <div className="flex items-center space-x-2">
                          <span>{b.task?.name || 'Task'}</span>
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                            {b.task?.category}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3.5">
                        <div className="text-slate-300 font-medium">{b.agent_config?.name || 'Config'}</div>
                        <code className="text-[10px] text-cyan-400 font-mono">{b.agent_config?.model}</code>
                      </td>
                      <td className="px-4 py-3.5 text-center font-bold">
                        {b.n_runs} runs
                      </td>
                      <td className="px-4 py-3.5 text-center">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          isDone 
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' 
                            : 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 animate-pulse'
                        }`}>
                          {b.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 text-center font-bold">
                        {isDone ? (
                          <span className={(sm.overall_pass_rate || 0) >= 80 ? 'text-emerald-400' : 'text-amber-400'}>
                            {sm.overall_pass_rate ?? 0}%
                          </span>
                        ) : '—'}
                      </td>
                      <td className="px-4 py-3.5 text-center font-semibold">
                        {isDone ? `${sm.avg_score ?? 0} / 100` : '—'}
                      </td>
                      <td className="px-4 py-3.5 text-center text-slate-400">
                        {isDone ? `${Math.round(sm.avg_latency_ms || 0)}ms` : '—'}
                      </td>
                      <td className="px-4 py-3.5 text-center font-bold text-cyan-300">
                        {isDone ? `$${(sm.cost_per_successful_task || 0).toFixed(4)}` : '—'}
                      </td>
                      <td className="px-5 py-3.5 text-right space-x-2">
                        {isDone && (
                          <>
                            <button
                              onClick={() => onViewReport(b.id)}
                              className="inline-flex items-center space-x-1 text-cyan-400 hover:text-cyan-300 font-semibold"
                            >
                              <span>Report</span>
                              <ArrowRight className="w-3 h-3" />
                            </button>
                            <button
                              onClick={() => window.open(api.getReportPdfUrl(b.id), '_blank')}
                              className="p-1 rounded text-slate-400 hover:text-white"
                              title="Export PDF"
                            >
                              <Download className="w-3.5 h-3.5" />
                            </button>
                          </>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
};
