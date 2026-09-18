import React, { useState, useEffect } from 'react';
import { 
  GitCompare, 
  Play, 
  CheckCircle2, 
  AlertCircle, 
  TrendingUp, 
  ArrowRight, 
  Scale, 
  HelpCircle,
  Loader2
} from 'lucide-react';
import { Task, AgentConfig, Comparison } from '../types';
import { api } from '../api/client';

interface ComparisonViewProps {
  tasks: Task[];
  configs: AgentConfig[];
  onViewReport: (batchId: string) => void;
}

export const ComparisonView: React.FC<ComparisonViewProps> = ({ tasks, configs, onViewReport }) => {
  const [selectedTask, setSelectedTask] = useState<string>(tasks[0]?.id || '');
  const [selectedConfigs, setSelectedConfigs] = useState<string[]>([
    configs[0]?.id || '',
    configs[1]?.id || ''
  ]);
  const [nRuns, setNRuns] = useState<number>(5);
  const [comparisons, setComparisons] = useState<Comparison[]>([]);
  const [activeComparison, setActiveComparison] = useState<Comparison | null>(null);
  const [isComparing, setIsComparing] = useState<boolean>(false);

  useEffect(() => {
    loadComparisons();
  }, []);

  const loadComparisons = async () => {
    try {
      const data = await api.getComparisons();
      setComparisons(data);
      if (data.length > 0) {
        setActiveComparison(data[0]);
      }
    } catch (err) {
      console.error('Failed to load comparisons:', err);
    }
  };

  const handleConfigToggle = (cfgId: string) => {
    if (selectedConfigs.includes(cfgId)) {
      if (selectedConfigs.length > 2) {
        setSelectedConfigs(selectedConfigs.filter(id => id !== cfgId));
      }
    } else {
      setSelectedConfigs([...selectedConfigs, cfgId]);
    }
  };

  const handleRunComparison = async () => {
    if (!selectedTask || selectedConfigs.length < 2) return;
    setIsComparing(true);
    try {
      const comp = await api.createComparison(selectedTask, selectedConfigs, nRuns);
      setActiveComparison(comp);
      setComparisons([comp, ...comparisons]);
    } catch (err: any) {
      alert(`Comparison error: ${err.message}`);
    } finally {
      setIsComparing(false);
    }
  };

  const matrixConfigs = activeComparison?.metrics_matrix?.configs || [];
  const stats = activeComparison?.statistical_confidence || {};

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
      
      {/* Header */}
      <div className="border-b border-slate-800 pb-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center space-x-2.5">
            <GitCompare className="w-6 h-6 text-cyan-400" />
            <span>Agent Reliability Comparison Engine</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Evaluate 2+ Agent Configs head-to-head on the same benchmark task with two-proportion statistical significance testing.
          </p>
        </div>
      </div>

      {/* Comparison Setup Card */}
      <div className="bg-slate-900/90 border border-slate-800 p-6 rounded-2xl space-y-5">
        <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Configure Head-to-Head Comparison
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {/* Task Select */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Select Benchmark Task</label>
            <select
              value={selectedTask}
              onChange={(e) => setSelectedTask(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
            >
              {tasks.map(t => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
          </div>

          {/* Configs Checklist */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Select Agent Configs (Pick 2+)</label>
            <div className="space-y-1.5 max-h-32 overflow-y-auto bg-slate-950 p-2.5 rounded-xl border border-slate-800">
              {configs.map(c => {
                const isSelected = selectedConfigs.includes(c.id);
                return (
                  <label key={c.id} className="flex items-center space-x-2 text-xs text-slate-300 cursor-pointer hover:text-white">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => handleConfigToggle(c.id)}
                      className="rounded accent-cyan-500"
                    />
                    <span>{c.name} ({c.model})</span>
                  </label>
                );
              })}
            </div>
          </div>

          {/* Iterations & Action */}
          <div className="flex flex-col justify-between">
            <div>
              <div className="flex justify-between items-center mb-1">
                <span className="text-xs font-medium text-slate-300">Iterations / Config</span>
                <span className="text-xs font-bold text-cyan-400">{nRuns} runs</span>
              </div>
              <input
                type="range"
                min={2}
                max={15}
                value={nRuns}
                onChange={(e) => setNRuns(parseInt(e.target.value))}
                className="w-full accent-cyan-500 cursor-pointer"
              />
            </div>
            
            <button
              onClick={handleRunComparison}
              disabled={isComparing || selectedConfigs.length < 2}
              className="mt-3 flex items-center justify-center space-x-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-semibold px-4 py-2.5 rounded-xl shadow-lg shadow-cyan-500/20 disabled:opacity-50 transition"
            >
              {isComparing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Scale className="w-4 h-4" />}
              <span>Compute Comparison & Confidence</span>
            </button>
          </div>
        </div>
      </div>

      {/* Comparison Results */}
      {activeComparison ? (
        <div className="space-y-6">
          
          {/* Statistical Significance Headline Card */}
          {stats.z_score !== undefined && (
            <div className={`p-5 rounded-2xl border ${
              stats.is_significant
                ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300'
                : 'bg-slate-900 border-slate-800 text-slate-300'
            }`}>
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-start space-x-3">
                  <div className={`p-2 rounded-xl mt-0.5 ${
                    stats.is_significant ? 'bg-emerald-500/20 text-emerald-400' : 'bg-slate-800 text-slate-400'
                  }`}>
                    <Scale className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <h3 className="text-sm font-bold text-white">Statistical Significance Test</h3>
                      <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${
                        stats.is_significant 
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' 
                          : 'bg-slate-800 text-slate-400 border border-slate-700'
                      }`}>
                        {stats.is_significant ? 'STATISTICALLY SIGNIFICANT (p < 0.05)' : 'NOT STATISTICALLY SIGNIFICANT (p >= 0.05)'}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">
                      Two-proportion z-test comparing <strong className="text-slate-200">{stats.comparison_pair}</strong> across {nRuns} iterations each.
                    </p>
                  </div>
                </div>

                {/* Key Stat Values */}
                <div className="flex items-center space-x-6 text-xs bg-slate-950/60 px-4 py-2.5 rounded-xl border border-slate-800">
                  <div>
                    <span className="text-slate-500 block text-[10px]">SUCCESS DELTA</span>
                    <strong className="text-white text-sm">
                      {stats.difference !== undefined ? (stats.difference * 100).toFixed(1) : '0.0'}%
                    </strong>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px]">Z-SCORE</span>
                    <strong className="text-cyan-400 text-sm">{stats.z_score}</strong>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px]">P-VALUE</span>
                    <strong className={`text-sm ${stats.is_significant ? 'text-emerald-400 font-bold' : 'text-slate-300'}`}>
                      {stats.p_value}
                    </strong>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px]">95% CI</span>
                    <code className="text-[11px] text-purple-300">
                      [{stats.ci_95?.[0]}, {stats.ci_95?.[1]}]
                    </code>
                  </div>
                </div>

              </div>
            </div>
          )}

          {/* Side-by-Side Metric Matrix Table */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
            <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
              <h3 className="text-sm font-bold text-white">Side-by-Side Metric Matrix</h3>
              <span className="text-xs text-slate-400">{matrixConfigs.length} Configurations Evaluated</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider text-[10px]">
                  <tr>
                    <th className="px-5 py-3 font-semibold">Agent Configuration</th>
                    <th className="px-4 py-3 font-semibold">Model</th>
                    <th className="px-4 py-3 font-semibold text-center">Pass Rate</th>
                    <th className="px-4 py-3 font-semibold text-center">Task Completion</th>
                    <th className="px-4 py-3 font-semibold text-center">Tool Accuracy</th>
                    <th className="px-4 py-3 font-semibold text-center">Citation Precision</th>
                    <th className="px-4 py-3 font-semibold text-center">Hallucination</th>
                    <th className="px-4 py-3 font-semibold text-center">Avg Latency</th>
                    <th className="px-4 py-3 font-semibold text-center">Cost / Success</th>
                    <th className="px-5 py-3 font-semibold text-right">Report</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800 text-slate-200">
                  {matrixConfigs.map((cfg, idx) => (
                    <tr key={idx} className="hover:bg-slate-800/40 transition">
                      <td className="px-5 py-3.5 font-semibold text-white">
                        {cfg.agent_name}
                      </td>
                      <td className="px-4 py-3.5">
                        <code className="text-cyan-300 bg-slate-950 px-2 py-0.5 rounded text-[11px] font-mono">
                          {cfg.model}
                        </code>
                      </td>
                      <td className="px-4 py-3.5 text-center">
                        <span className={`font-bold px-2 py-0.5 rounded-full text-[11px] ${
                          cfg.overall_pass_rate >= 80 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'
                        }`}>
                          {cfg.overall_pass_rate}%
                        </span>
                      </td>
                      <td className="px-4 py-3.5 text-center font-medium">
                        {cfg.completion_rate}%
                      </td>
                      <td className="px-4 py-3.5 text-center font-medium text-blue-400">
                        {cfg.tool_call_accuracy}%
                      </td>
                      <td className="px-4 py-3.5 text-center font-medium text-purple-400">
                        {cfg.citation_precision}%
                      </td>
                      <td className="px-4 py-3.5 text-center font-medium">
                        <span className={cfg.hallucination_rate > 15 ? 'text-rose-400 font-bold' : 'text-slate-300'}>
                          {cfg.hallucination_rate}%
                        </span>
                      </td>
                      <td className="px-4 py-3.5 text-center text-slate-400">
                        {Math.round(cfg.avg_latency_ms)}ms
                      </td>
                      <td className="px-4 py-3.5 text-center font-bold text-cyan-300">
                        ${cfg.cost_per_successful_task.toFixed(4)}
                      </td>
                      <td className="px-5 py-3.5 text-right">
                        <button
                          onClick={() => onViewReport(cfg.batch_id)}
                          className="inline-flex items-center space-x-1 text-cyan-400 hover:text-cyan-300 text-xs font-semibold"
                        >
                          <span>View Report</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center">
          <GitCompare className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-white">No Comparison Computed Yet</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto mt-1">
            Pick a benchmark task and 2 or more agent configurations above to generate a statistical comparison report.
          </p>
        </div>
      )}

    </div>
  );
};
