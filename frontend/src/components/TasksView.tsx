import React, { useState, useEffect } from 'react';
import { Layers, Plus, Check, Clock, DollarSign, Wrench, FileCode2, BookOpen } from 'lucide-react';
import { Task } from '../types';
import { api } from '../api/client';

export const TasksView: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [isCreating, setIsCreating] = useState<boolean>(false);
  const [newTaskName, setNewTaskName] = useState<string>('');
  const [newTaskCategory, setNewTaskCategory] = useState<string>('tool-use');
  const [newTaskPrompt, setNewTaskPrompt] = useState<string>('');
  const [newTaskTools, setNewTaskTools] = useState<string>('web_search');
  const [newTaskRubric, setNewTaskRubric] = useState<string>('');

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      const data = await api.getTasks();
      setTasks(data);
      if (data.length > 0 && !selectedTask) {
        setSelectedTask(data[0]);
      }
    } catch (err) {
      console.error('Failed to load tasks:', err);
    }
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTaskName || !newTaskPrompt) return;

    try {
      const created = await api.createTask({
        name: newTaskName,
        category: newTaskCategory,
        prompt_template: newTaskPrompt,
        required_tools: newTaskTools ? newTaskTools.split(',').map(s => s.trim()).filter(Boolean) : [],
        success_criteria: { rubric: newTaskRubric },
        budget_constraints: { max_latency_ms: 6000.0, max_cost_usd: 0.05 }
      });
      setTasks([created, ...tasks]);
      setSelectedTask(created);
      setIsCreating(false);
      setNewTaskName('');
      setNewTaskPrompt('');
      setNewTaskRubric('');
    } catch (err: any) {
      alert(`Create task error: ${err.message}`);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
      
      {/* Header */}
      <div className="border-b border-slate-800 pb-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center space-x-2.5">
            <Layers className="w-6 h-6 text-cyan-400" />
            <span>Benchmark Task Library</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Standardized task definitions with deterministic JSON output schemas, required tools, and evaluation rubrics.
          </p>
        </div>
        <button
          onClick={() => setIsCreating(!isCreating)}
          className="flex items-center space-x-2 bg-cyan-500 hover:bg-cyan-400 text-white text-xs font-semibold px-4 py-2.5 rounded-xl shadow-lg shadow-cyan-500/20 transition"
        >
          <Plus className="w-4 h-4" />
          <span>{isCreating ? 'Cancel' : 'Create Benchmark Task'}</span>
        </button>
      </div>

      {/* Create Task Form */}
      {isCreating && (
        <form onSubmit={handleCreateTask} className="bg-slate-900 border border-slate-800 p-6 rounded-2xl space-y-4">
          <h2 className="text-sm font-bold text-white">Define New Benchmark Task</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Task Name</label>
              <input
                type="text"
                value={newTaskName}
                onChange={(e) => setNewTaskName(e.target.value)}
                placeholder="e.g. Competitive Price Audit"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Category</label>
              <select
                value={newTaskCategory}
                onChange={(e) => setNewTaskCategory(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              >
                <option value="tool-use">tool-use</option>
                <option value="research">research</option>
                <option value="citation">citation</option>
                <option value="coding">coding</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Prompt Template</label>
            <textarea
              value={newTaskPrompt}
              onChange={(e) => setNewTaskPrompt(e.target.value)}
              placeholder="Enter exact instructions provided to the agent..."
              rows={3}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Required Tools (comma-separated)</label>
              <input
                type="text"
                value={newTaskTools}
                onChange={(e) => setNewTaskTools(e.target.value)}
                placeholder="web_search, calculator"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Success Criteria Rubric</label>
              <input
                type="text"
                value={newTaskRubric}
                onChange={(e) => setNewTaskRubric(e.target.value)}
                placeholder="e.g. Must extract 3 items with exact prices"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <button
              type="submit"
              className="bg-cyan-500 hover:bg-cyan-400 text-white text-xs font-semibold px-5 py-2 rounded-xl"
            >
              Save Benchmark Task
            </button>
          </div>
        </form>
      )}

      {/* Task List & Detail Split View */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Task List */}
        <div className="space-y-3">
          {tasks.map((t) => {
            const isSelected = selectedTask?.id === t.id;
            return (
              <div
                key={t.id}
                onClick={() => setSelectedTask(t)}
                className={`p-4 rounded-2xl border cursor-pointer transition ${
                  isSelected
                    ? 'bg-slate-900 border-cyan-500/60 shadow-lg shadow-cyan-500/10'
                    : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <h3 className="text-sm font-bold text-white line-clamp-1">{t.name}</h3>
                  <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                    {t.category}
                  </span>
                </div>
                <p className="text-xs text-slate-400 line-clamp-2 mt-1">
                  {t.prompt_template}
                </p>
                <div className="flex items-center space-x-3 text-[11px] text-slate-500 mt-3 pt-2 border-t border-slate-800/60">
                  <span className="flex items-center space-x-1">
                    <Wrench className="w-3 h-3" />
                    <span>{t.required_tools?.length || 0} tools</span>
                  </span>
                  <span>•</span>
                  <span>{t.expected_output_schema ? 'JSON Schema' : 'Rubric'}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right Column: Task Inspection Card */}
        {selectedTask && (
          <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <span className="text-[11px] font-bold text-cyan-400 uppercase tracking-wider">{selectedTask.category} Task</span>
                <h2 className="text-xl font-bold text-white mt-0.5">{selectedTask.name}</h2>
              </div>
              <div className="flex items-center space-x-2 text-xs text-slate-400">
                <Clock className="w-4 h-4" />
                <span>Max {selectedTask.budget_constraints?.max_latency_ms || 5000}ms</span>
              </div>
            </div>

            {/* Prompt Template */}
            <div>
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
                <span>Prompt Template</span>
              </h4>
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-xs text-slate-200 leading-relaxed">
                {selectedTask.prompt_template}
              </div>
            </div>

            {/* Expected Output JSON Schema if available */}
            {selectedTask.expected_output_schema && (
              <div>
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                  <FileCode2 className="w-3.5 h-3.5 text-purple-400" />
                  <span>Deterministic Output JSON Schema</span>
                </h4>
                <pre className="bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-[11px] text-purple-300 overflow-x-auto max-h-48">
                  {JSON.stringify(selectedTask.expected_output_schema, null, 2)}
                </pre>
              </div>
            )}

            {/* Evaluation Rubric & Criteria */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
              <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Required Tools</h4>
                {selectedTask.required_tools && selectedTask.required_tools.length > 0 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {selectedTask.required_tools.map((t, idx) => (
                      <span key={idx} className="px-2 py-1 bg-slate-900 border border-slate-800 text-cyan-300 rounded text-xs font-mono">
                        {t}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-500">None required (direct reasoning)</p>
                )}
              </div>

              <div className="bg-slate-950/80 p-4 rounded-xl border border-slate-800">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Success Criteria</h4>
                <p className="text-xs text-slate-300">
                  {selectedTask.success_criteria?.rubric || 'Standard completion checks apply.'}
                </p>
              </div>
            </div>

          </div>
        )}

      </div>

    </div>
  );
};
