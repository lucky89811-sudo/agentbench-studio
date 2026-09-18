import React, { useState, useEffect } from 'react';
import { X, Play, Loader2, CheckCircle2, AlertCircle, ArrowRight, Gauge, Layers, Cpu } from 'lucide-react';
import { Task, AgentConfig, RunBatch } from '../types';
import { api } from '../api/client';

interface BatchRunnerModalProps {
  isOpen: boolean;
  onClose: () => void;
  tasks: Task[];
  configs: AgentConfig[];
  onBatchStarted: (batchId: string) => void;
  onViewReport: (batchId: string) => void;
}

export const BatchRunnerModal: React.FC<BatchRunnerModalProps> = ({
  isOpen,
  onClose,
  tasks,
  configs,
  onBatchStarted,
  onViewReport
}) => {
  const [selectedTask, setSelectedTask] = useState<string>(tasks[0]?.id || '');
  const [selectedConfig, setSelectedConfig] = useState<string>(configs[0]?.id || '');
  const [nRuns, setNRuns] = useState<number>(5);
  const [concurrency, setConcurrency] = useState<number>(3);
  const [isLaunching, setIsLaunching] = useState<boolean>(false);
  const [activeBatch, setActiveBatch] = useState<RunBatch | null>(null);

  useEffect(() => {
    if (tasks.length > 0 && !selectedTask) setSelectedTask(tasks[0].id);
    if (configs.length > 0 && !selectedConfig) setSelectedConfig(configs[0].id);
  }, [tasks, configs]);

  // Polling active batch progress
  useEffect(() => {
    if (!activeBatch || activeBatch.status === 'completed' || activeBatch.status === 'failed') return;

    const interval = setInterval(async () => {
      try {
        const updated = await api.getBatch(activeBatch.id);
        setActiveBatch(updated);
      } catch (err) {
        console.error('Polling error:', err);
      }
    }, 1200);

    return () => clearInterval(interval);
  }, [activeBatch]);

  if (!isOpen) return null;

  const handleLaunch = async () => {
    if (!selectedTask || !selectedConfig) return;
    setIsLaunching(true);
    try {
      const batch = await api.startBatch(selectedTask, selectedConfig, nRuns, concurrency);
      setActiveBatch(batch);
      onBatchStarted(batch.id);
    } catch (err: any) {
      alert(`Launch error: ${err.message}`);
    } finally {
      setIsLaunching(false);
    }
  };

  const currentTaskObj = tasks.find(t => t.id === selectedTask);
  const currentConfigObj = configs.find(c => c.id === selectedConfig);

  const completedCount = activeBatch?.completed_runs_count || 0;
  const totalRuns = activeBatch?.n_runs || nRuns;
  const progressPercent = totalRuns > 0 ? Math.round((completedCount / totalRuns) * 100) : 0;
  const isFinished = activeBatch?.status === 'completed';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/50">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
              <Play className="w-4 h-4 fill-current" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-white">Execute Reliability Benchmark Batch</h3>
              <p className="text-xs text-slate-400">Repeatedly stress-test an agent configuration across N runs</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-5">
          {!activeBatch ? (
            <>
              {/* Task Selection */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                  <Layers className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Target Benchmark Task</span>
                </label>
                <select
                  value={selectedTask}
                  onChange={(e) => setSelectedTask(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  {tasks.map(t => (
                    <option key={t.id} value={t.id}>{t.name} ({t.category})</option>
                  ))}
                </select>
                {currentTaskObj && (
                  <div className="mt-2 p-3 bg-slate-950/60 rounded-lg border border-slate-800/80 text-xs text-slate-400 space-y-1">
                    <p className="line-clamp-2"><span className="text-slate-300 font-medium">Prompt:</span> {currentTaskObj.prompt_template}</p>
                    <div className="flex items-center space-x-3 text-[11px] text-slate-500 pt-1">
                      <span>Required Tools: {currentTaskObj.required_tools?.join(', ') || 'None'}</span>
                      <span>•</span>
                      <span>Budget: {currentTaskObj.budget_constraints?.max_latency_ms || 5000}ms max</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Agent Config Selection */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                  <Cpu className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Agent Configuration under Test</span>
                </label>
                <select
                  value={selectedConfig}
                  onChange={(e) => setSelectedConfig(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  {configs.map(c => (
                    <option key={c.id} value={c.id}>{c.name} — [{c.model} / {c.prompt_version}]</option>
                  ))}
                </select>
                {currentConfigObj && (
                  <div className="mt-2 p-3 bg-slate-950/60 rounded-lg border border-slate-800/80 text-xs text-slate-400">
                    <p className="line-clamp-2"><span className="text-slate-300 font-medium">System Prompt:</span> {currentConfigObj.system_prompt || 'No system prompt specified'}</p>
                    <p className="text-[11px] text-slate-500 pt-1">
                      Temperature: {currentConfigObj.temperature} &nbsp;•&nbsp; Tools: {currentConfigObj.tool_definitions?.length || 0} enabled &nbsp;•&nbsp; Max Steps: {currentConfigObj.max_steps}
                    </p>
                  </div>
                )}
              </div>

              {/* Repetitions & Concurrency Sliders */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3.5">
                  <div className="flex justify-between items-center mb-1.5">
                    <span className="text-xs font-medium text-slate-300">Iterations (N Runs)</span>
                    <span className="text-xs font-bold text-cyan-400 px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">{nRuns} runs</span>
                  </div>
                  <input
                    type="range"
                    min={1}
                    max={20}
                    value={nRuns}
                    onChange={(e) => setNRuns(parseInt(e.target.value))}
                    className="w-full accent-cyan-500 cursor-pointer"
                  />
                  <p className="text-[10px] text-slate-500 mt-1">Recommended: 5–10 runs to measure variance</p>
                </div>

                <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3.5">
                  <div className="flex justify-between items-center mb-1.5">
                    <span className="text-xs font-medium text-slate-300">Concurrency Limit</span>
                    <span className="text-xs font-bold text-blue-400 px-2 py-0.5 rounded bg-blue-500/10 border border-blue-500/20">{concurrency} workers</span>
                  </div>
                  <input
                    type="range"
                    min={1}
                    max={5}
                    value={concurrency}
                    onChange={(e) => setConcurrency(parseInt(e.target.value))}
                    className="w-full accent-blue-500 cursor-pointer"
                  />
                  <p className="text-[10px] text-slate-500 mt-1">Async parallel executions bounded by semaphore</p>
                </div>
              </div>
            </>
          ) : (
            /* Live Execution Progress State */
            <div className="py-6 space-y-6 text-center">
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 mb-1">
                {isFinished ? (
                  <CheckCircle2 className="w-8 h-8 text-emerald-400 animate-in zoom-in" />
                ) : (
                  <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
                )}
              </div>

              <div>
                <h4 className="text-lg font-bold text-white">
                  {isFinished ? 'Evaluation Batch Completed!' : `Executing Batch (${completedCount}/${totalRuns} Runs)`}
                </h4>
                <p className="text-xs text-slate-400 mt-1">
                  {isFinished
                    ? 'Evaluators scored all executions across deterministic checks and model rubrics.'
                    : 'Running iterations, capturing full step transcripts, tool outputs, and timings...'}
                </p>
              </div>

              {/* Progress Bar */}
              <div className="space-y-2 max-w-md mx-auto">
                <div className="w-full bg-slate-950 rounded-full h-3.5 border border-slate-800 overflow-hidden p-0.5">
                  <div
                    className="bg-gradient-to-r from-cyan-500 to-blue-500 h-full rounded-full transition-all duration-300"
                    style={{ width: `${progressPercent}%` }}
                  ></div>
                </div>
                <div className="flex justify-between text-xs text-slate-400">
                  <span>{completedCount} completed</span>
                  <span className="font-semibold text-cyan-400">{progressPercent}%</span>
                  <span>{totalRuns} total</span>
                </div>
              </div>

              {/* Summary preview if finished */}
              {isFinished && activeBatch.summary_metrics && (
                <div className="grid grid-cols-3 gap-3 max-w-md mx-auto text-left pt-2">
                  <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                    <p className="text-[10px] text-slate-400">Pass Rate</p>
                    <p className="text-base font-bold text-emerald-400">{activeBatch.summary_metrics.overall_pass_rate}%</p>
                  </div>
                  <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                    <p className="text-[10px] text-slate-400">Avg Latency</p>
                    <p className="text-base font-bold text-cyan-400">{activeBatch.summary_metrics.avg_latency_ms} ms</p>
                  </div>
                  <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                    <p className="text-[10px] text-slate-400">Cost/Success</p>
                    <p className="text-base font-bold text-blue-400">${activeBatch.summary_metrics.cost_per_successful_task.toFixed(4)}</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-900/50 flex justify-end space-x-3">
          {!activeBatch ? (
            <>
              <button
                onClick={onClose}
                className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleLaunch}
                disabled={isLaunching}
                className="flex items-center space-x-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-semibold px-5 py-2.5 rounded-xl shadow-lg shadow-cyan-500/25 disabled:opacity-50 transition"
              >
                {isLaunching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
                <span>Start N={nRuns} Evaluation Runs</span>
              </button>
            </>
          ) : (
            <>
              <button
                onClick={onClose}
                className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800 transition"
              >
                Close
              </button>
              {isFinished && (
                <button
                  onClick={() => {
                    onViewReport(activeBatch.id);
                    onClose();
                  }}
                  className="flex items-center space-x-2 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white text-xs font-semibold px-5 py-2.5 rounded-xl shadow-lg shadow-emerald-500/25 transition"
                >
                  <span>View Full Reliability Report</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              )}
            </>
          )}
        </div>

      </div>
    </div>
  );
};
