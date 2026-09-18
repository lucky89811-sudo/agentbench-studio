import React, { useState, useEffect } from 'react';
import { 
  ArrowLeft, 
  Download, 
  ShieldCheck, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Clock, 
  DollarSign, 
  TrendingUp, 
  Layers, 
  ChevronDown, 
  ChevronUp, 
  Wrench, 
  FileText, 
  ExternalLink,
  Loader2,
  Terminal,
  Activity
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  LineChart, 
  Line, 
  CartesianGrid, 
  AreaChart, 
  Area 
} from 'recharts';
import { EvaluationReport } from '../types';
import { api } from '../api/client';

interface ReportViewProps {
  batchId: string;
  onBack: () => void;
}

export const ReportView: React.FC<ReportViewProps> = ({ batchId, onBack }) => {
  const [report, setReport] = useState<EvaluationReport | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [expandedRunId, setExpandedRunId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadReport();
  }, [batchId]);

  const loadReport = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getReport(batchId);
      setReport(data);
      if (data.worst_runs && data.worst_runs.length > 0) {
        setExpandedRunId(data.worst_runs[0].run_id);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load report');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadPdf = () => {
    window.open(api.getReportPdfUrl(batchId), '_blank');
  };

  if (isLoading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center space-y-3">
        <Loader2 className="w-8 h-8 text-cyan-400 animate-spin" />
        <p className="text-sm text-slate-400">Loading evaluation report and computing distributions...</p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="p-8 max-w-4xl mx-auto">
        <button onClick={onBack} className="flex items-center space-x-2 text-sm text-slate-400 hover:text-white mb-4">
          <ArrowLeft className="w-4 h-4" />
          <span>Back</span>
        </button>
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-6 text-center text-red-400">
          <AlertTriangle className="w-8 h-8 mx-auto mb-2 text-red-400" />
          <h3 className="font-semibold text-white">Error Loading Report</h3>
          <p className="text-xs mt-1">{error || 'Unknown error occurred.'}</p>
        </div>
      </div>
    );
  }

  const { scorecard, distributions, worst_runs, historical_trend, task, agent_config } = report;

  // Chart data for run-by-run reliability
  const runData = distributions?.raw_run_scores || [];
  const chartData = runData.map(r => ({
    run: `Run #${r.run_index}`,
    score: r.score,
    latency: Math.round(r.latency_ms),
    cost: (r.cost_usd * 1000).toFixed(2), // in millidollars
    passed: r.passed ? 'Pass' : 'Fail'
  }));

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
      
      {/* Top Header & Breadcrumbs */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <button 
            onClick={onBack}
            className="flex items-center space-x-1.5 text-xs font-medium text-slate-400 hover:text-cyan-400 transition mb-2"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Dashboard</span>
          </button>
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-bold text-white tracking-tight">{task.name}</h1>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              {task.category}
            </span>
          </div>
          <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400 mt-1">
            <span>Agent: <strong className="text-slate-200">{agent_config.name}</strong></span>
            <span>•</span>
            <span>Model: <code className="text-cyan-300 font-mono text-[11px] bg-slate-900 px-1.5 py-0.5 rounded">{agent_config.model}</code></span>
            <span>•</span>
            <span>Version: <strong className="text-slate-200">{agent_config.prompt_version}</strong></span>
            <span>•</span>
            <span>Batch ID: <code className="text-slate-400 text-[11px]">{batchId.slice(0, 8)}</code></span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center space-x-3">
          <button
            onClick={handleDownloadPdf}
            className="flex items-center space-x-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-medium px-4 py-2.5 rounded-xl border border-slate-700 shadow-md transition active:scale-95"
          >
            <Download className="w-4 h-4 text-cyan-400" />
            <span>Export PDF Report</span>
          </button>
        </div>
      </div>

      {/* Headline Scorecard Cards */}
      <div>
        <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
          Executive Reliability Scorecard ({scorecard.total_runs_count} Runs)
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3.5">
          
          {/* Headline 1: Success Rate */}
          <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl relative overflow-hidden">
            <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
              <span>Overall Pass Rate</span>
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
            </div>
            <p className="text-2xl font-black text-white">{scorecard.overall_pass_rate}%</p>
            <div className="text-[11px] text-slate-500 mt-1">
              {scorecard.passing_runs_count}/{scorecard.total_runs_count} passed all checks
            </div>
            <div className={`absolute bottom-0 left-0 right-0 h-1 ${scorecard.overall_pass_rate >= 80 ? 'bg-emerald-500' : 'bg-amber-500'}`}></div>
          </div>

          {/* Headline 2: Task Completion */}
          <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl relative overflow-hidden">
            <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
              <span>Task Completion</span>
              <CheckCircle2 className="w-4 h-4 text-cyan-400" />
            </div>
            <p className="text-2xl font-black text-cyan-400">{scorecard.completion_rate}%</p>
            <div className="text-[11px] text-slate-500 mt-1">Schema & rubric met</div>
            <div className="absolute bottom-0 left-0 right-0 h-1 bg-cyan-500"></div>
          </div>

          {/* Headline 3: Tool-Call Accuracy */}
          <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl relative overflow-hidden">
            <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
              <span>Tool Accuracy</span>
              <Wrench className="w-4 h-4 text-blue-400" />
            </div>
            <p className="text-2xl font-black text-blue-400">{scorecard.tool_call_accuracy}%</p>
            <div className="text-[11px] text-slate-500 mt-1">Schema, retry & valid calls</div>
            <div className="absolute bottom-0 left-0 right-0 h-1 bg-blue-500"></div>
          </div>

          {/* Headline 4: Citation Correctness */}
          <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl relative overflow-hidden">
            <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
              <span>Citation Precision</span>
              <ExternalLink className="w-4 h-4 text-purple-400" />
            </div>
            <p className="text-2xl font-black text-purple-400">{scorecard.citation_precision}%</p>
            <div className="text-[11px] text-slate-500 mt-1">Live links & supported claims</div>
            <div className="absolute bottom-0 left-0 right-0 h-1 bg-purple-500"></div>
          </div>

          {/* Headline 5: Hallucination Rate */}
          <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl relative overflow-hidden">
            <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
              <span>Hallucination</span>
              <AlertTriangle className="w-4 h-4 text-amber-400" />
            </div>
            <p className={`text-2xl font-black ${scorecard.hallucination_rate > 15 ? 'text-rose-400' : 'text-emerald-400'}`}>
              {scorecard.hallucination_rate}%
            </p>
            <div className="text-[11px] text-slate-500 mt-1">Phantom tools & ungrounded</div>
            <div className={`absolute bottom-0 left-0 right-0 h-1 ${scorecard.hallucination_rate > 15 ? 'bg-rose-500' : 'bg-emerald-500'}`}></div>
          </div>

          {/* Headline 6: Avg Latency */}
          <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl relative overflow-hidden">
            <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
              <span>Avg Latency</span>
              <Clock className="w-4 h-4 text-slate-400" />
            </div>
            <p className="text-2xl font-black text-slate-200">{Math.round(scorecard.avg_latency_ms)}<span className="text-xs font-normal text-slate-400">ms</span></p>
            <div className="text-[11px] text-slate-500 mt-1">±{scorecard.latency_std_dev}ms std dev</div>
            <div className="absolute bottom-0 left-0 right-0 h-1 bg-slate-600"></div>
          </div>

          {/* Headline 7: Cost Per Successful Task (Key Metric!) */}
          <div className="bg-gradient-to-br from-cyan-950/60 to-blue-950/60 border border-cyan-500/30 p-4 rounded-2xl relative overflow-hidden col-span-2 md:col-span-1 shadow-lg shadow-cyan-950/40">
            <div className="flex items-center justify-between text-cyan-300 text-xs mb-1">
              <span className="font-semibold">Cost / Success</span>
              <DollarSign className="w-4 h-4 text-cyan-400" />
            </div>
            <p className="text-2xl font-black text-cyan-300">${scorecard.cost_per_successful_task.toFixed(4)}</p>
            <div className="text-[11px] text-cyan-400/80 mt-1 font-medium">Batch Cost / Passing Runs</div>
            <div className="absolute bottom-0 left-0 right-0 h-1 bg-cyan-400"></div>
          </div>

        </div>
      </div>

      {/* Distribution Charts & Variance Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Chart 1: Iteration-by-Iteration Scores */}
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Reliability Score Distribution across Iterations</h3>
              <p className="text-xs text-slate-400">Composite score (0–100) per run measuring consistency and variance</p>
            </div>
            <div className="text-right">
              <span className="text-xs text-slate-400">Std Dev: </span>
              <strong className="text-cyan-400 text-xs">{scorecard.score_std_dev} pts</strong>
            </div>
          </div>
          <div className="h-60">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="run" stroke="#64748b" fontSize={11} />
                <YAxis domain={[0, 100]} stroke="#64748b" fontSize={11} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} 
                  formatter={(val: any) => [`${val} / 100`, 'Score']}
                />
                <Bar dataKey="score" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Step Latency Breakdown across Runs */}
        <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Execution Latency (ms) across Iterations</h3>
              <p className="text-xs text-slate-400">End-to-end duration per run</p>
            </div>
            <div className="text-right">
              <span className="text-xs text-slate-400">Budget Max: </span>
              <strong className="text-slate-300 text-xs">{task.prompt_template ? '6,000ms' : '10,000ms'}</strong>
            </div>
          </div>
          <div className="h-60">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <defs>
                  <linearGradient id="latencyGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="run" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} 
                  formatter={(val: any) => [`${val} ms`, 'Latency']}
                />
                <Area type="monotone" dataKey="latency" stroke="#8b5cf6" fillOpacity={1} fill="url(#latencyGradient)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Variance & Quartiles Card */}
      <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
          Statistical Quartile Distribution (N Runs)
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800/80">
            <span className="text-xs text-slate-400 font-medium">Reliability Score (0–100)</span>
            <div className="flex items-baseline space-x-2 mt-1">
              <span className="text-lg font-bold text-white">{distributions.score.p50} <span className="text-xs text-slate-500 font-normal">median</span></span>
            </div>
            <div className="flex justify-between text-[11px] text-slate-500 mt-2 pt-2 border-t border-slate-800/60">
              <span>Min: {distributions.score.min}</span>
              <span>P25: {distributions.score.p25}</span>
              <span>P75: {distributions.score.p75}</span>
              <span>Max: {distributions.score.max}</span>
            </div>
          </div>

          <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800/80">
            <span className="text-xs text-slate-400 font-medium">Latency (ms)</span>
            <div className="flex items-baseline space-x-2 mt-1">
              <span className="text-lg font-bold text-white">{distributions.latency.p50} <span className="text-xs text-slate-500 font-normal">median</span></span>
            </div>
            <div className="flex justify-between text-[11px] text-slate-500 mt-2 pt-2 border-t border-slate-800/60">
              <span>Min: {distributions.latency.min}</span>
              <span>P25: {distributions.latency.p25}</span>
              <span>P75: {distributions.latency.p75}</span>
              <span>Max: {distributions.latency.max}</span>
            </div>
          </div>

          <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800/80">
            <span className="text-xs text-slate-400 font-medium">Token Consumption</span>
            <div className="flex items-baseline space-x-2 mt-1">
              <span className="text-lg font-bold text-white">{distributions.tokens.p50} <span className="text-xs text-slate-500 font-normal">median</span></span>
            </div>
            <div className="flex justify-between text-[11px] text-slate-500 mt-2 pt-2 border-t border-slate-800/60">
              <span>Min: {distributions.tokens.min}</span>
              <span>Mean: {distributions.tokens.mean}</span>
              <span>Max: {distributions.tokens.max}</span>
            </div>
          </div>

          <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800/80">
            <span className="text-xs text-slate-400 font-medium">Cost ($ USD)</span>
            <div className="flex items-baseline space-x-2 mt-1">
              <span className="text-lg font-bold text-white">${distributions.cost.mean.toFixed(5)} <span className="text-xs text-slate-500 font-normal">avg</span></span>
            </div>
            <div className="flex justify-between text-[11px] text-slate-500 mt-2 pt-2 border-t border-slate-800/60">
              <span>Min: ${distributions.cost.min.toFixed(4)}</span>
              <span>Total: ${scorecard.total_cost_usd?.toFixed(4)}</span>
              <span>Max: ${distributions.cost.max.toFixed(4)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Worst-Run Forensic Drilldown */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-white">Worst-Run Forensic Drilldown</h2>
            <p className="text-xs text-slate-400">Inspect the lowest-scoring runs with full execution transcripts and evaluator evidence</p>
          </div>
          <span className="text-xs text-amber-400/90 bg-amber-500/10 px-2.5 py-1 rounded-full border border-amber-500/20">
            {worst_runs.length} Runs Analyzed
          </span>
        </div>

        <div className="space-y-3">
          {worst_runs.map((wr) => {
            const isExpanded = expandedRunId === wr.run_id;
            return (
              <div 
                key={wr.run_id} 
                className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden transition-all"
              >
                {/* Header Row */}
                <div 
                  onClick={() => setExpandedRunId(isExpanded ? null : wr.run_id)}
                  className="px-5 py-4 flex items-center justify-between cursor-pointer hover:bg-slate-850 transition"
                >
                  <div className="flex items-center space-x-4">
                    <div className={`w-8 h-8 rounded-xl flex items-center justify-center text-xs font-bold ${
                      wr.overall_passed ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                    }`}>
                      #{wr.run_index}
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-semibold text-white">Iteration #{wr.run_index}</span>
                        <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full ${
                          wr.overall_passed ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
                        }`}>
                          Score: {wr.overall_score} / 100
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 mt-0.5">
                        Latency: {Math.round(wr.latency_ms)}ms &nbsp;•&nbsp; Cost: ${wr.cost_usd.toFixed(5)}
                      </p>
                    </div>
                  </div>

                  {/* Findings / Defect Pills */}
                  <div className="flex items-center space-x-3">
                    <div className="hidden md:flex items-center space-x-2 text-xs">
                      {wr.evaluator_scores.phantom_tool_count > 0 && (
                        <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30 text-[11px]">
                          Phantom Tool ({wr.evaluator_scores.phantom_tool_count})
                        </span>
                      )}
                      {wr.evaluator_scores.broken_link_count > 0 && (
                        <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[11px]">
                          Broken Link ({wr.evaluator_scores.broken_link_count})
                        </span>
                      )}
                      {wr.evaluator_scores.ignored_tool_errors > 0 && (
                        <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30 text-[11px]">
                          Ignored Tool Error
                        </span>
                      )}
                    </div>
                    {isExpanded ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
                  </div>
                </div>

                {/* Expanded Transcript & Findings */}
                {isExpanded && (
                  <div className="border-t border-slate-800 p-5 bg-slate-950/70 space-y-5">
                    
                    {/* Evaluator Evidence Box */}
                    {wr.failure_reasons.length > 0 && (
                      <div className="bg-rose-950/20 border border-rose-500/30 rounded-xl p-4">
                        <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                          <AlertTriangle className="w-3.5 h-3.5" />
                          <span>Evaluator Evidence & Diagnostic Findings</span>
                        </h4>
                        <ul className="space-y-1 text-xs text-rose-200">
                          {wr.failure_reasons.map((reason, idx) => (
                            <li key={idx} className="flex items-start space-x-2">
                              <span className="text-rose-400 font-bold">•</span>
                              <span>{reason}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Final Output */}
                    <div>
                      <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Final Output</h4>
                      <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5 text-xs text-slate-200 font-mono whitespace-pre-wrap max-h-48 overflow-y-auto">
                        {wr.final_output}
                      </div>
                    </div>

                    {/* Step-by-Step Transcript */}
                    <div>
                      <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                        <Terminal className="w-3.5 h-3.5 text-cyan-400" />
                        <span>Execution Step Transcript ({wr.transcript?.length || 0} Steps)</span>
                      </h4>
                      <div className="space-y-2">
                        {wr.transcript?.map((step, sIdx) => {
                          const hasDefect = step.defect_flags && step.defect_flags.length > 0;
                          return (
                            <div 
                              key={sIdx}
                              className={`p-3 rounded-xl border text-xs ${
                                hasDefect 
                                  ? 'bg-rose-950/20 border-rose-500/40' 
                                  : 'bg-slate-900/90 border-slate-800'
                              }`}
                            >
                              <div className="flex items-center justify-between mb-1.5">
                                <div className="flex items-center space-x-2">
                                  <span className="font-bold text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                                    Step {step.step_index}: {step.role}
                                  </span>
                                  {hasDefect && (
                                    <span className="text-[10px] font-semibold text-rose-400 bg-rose-500/20 px-2 py-0.5 rounded">
                                      {step.defect_flags?.join('; ')}
                                    </span>
                                  )}
                                </div>
                                <span className="text-[10px] text-slate-500">{step.step_latency_ms}ms</span>
                              </div>

                              {/* Content */}
                              {step.content && (
                                <p className="text-slate-300 whitespace-pre-wrap">{step.content}</p>
                              )}

                              {/* Tool Calls */}
                              {step.tool_calls && step.tool_calls.length > 0 && (
                                <div className="mt-2 space-y-1">
                                  {step.tool_calls.map((tc: any, tcIdx: number) => (
                                    <div key={tcIdx} className="bg-slate-950 p-2 rounded border border-slate-800 text-cyan-300 font-mono text-[11px]">
                                      <span className="text-slate-400">tool_call:</span> <strong>{tc.name}</strong>({JSON.stringify(tc.arguments)})
                                    </div>
                                  ))}
                                </div>
                              )}

                              {/* Tool Results */}
                              {step.tool_results && step.tool_results.length > 0 && (
                                <div className="mt-2 space-y-1">
                                  {step.tool_results.map((tr: any, trIdx: number) => (
                                    <div key={trIdx} className="bg-slate-950 p-2 rounded border border-slate-800 text-emerald-300 font-mono text-[11px] line-clamp-3">
                                      <span className="text-slate-400">result [{tr.name}]:</span> {tr.content}
                                    </div>
                                  ))}
                                </div>
                              )}

                            </div>
                          );
                        })}
                      </div>
                    </div>

                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Historical Trend / Regression Section */}
      {historical_trend && historical_trend.length > 1 && (
        <div className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Historical Regression Trend</h3>
              <p className="text-xs text-slate-400">Performance tracking across previous prompt or model versions</p>
            </div>
            <TrendingUp className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={historical_trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="created_at" tickFormatter={(t) => t.slice(5, 10)} stroke="#64748b" fontSize={11} />
                <YAxis domain={[0, 100]} stroke="#64748b" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }} />
                <Line type="monotone" dataKey="pass_rate" stroke="#10b981" strokeWidth={2} name="Pass Rate (%)" />
                <Line type="monotone" dataKey="avg_score" stroke="#0ea5e9" strokeWidth={2} name="Avg Score" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

    </div>
  );
};
