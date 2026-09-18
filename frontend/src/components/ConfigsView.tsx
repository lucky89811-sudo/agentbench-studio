import React, { useState, useEffect } from 'react';
import { Cpu, Plus, Thermometer, Hash, Wrench, FileText, CheckCircle2 } from 'lucide-react';
import { AgentConfig } from '../types';
import { api } from '../api/client';

export const ConfigsView: React.FC = () => {
  const [configs, setConfigs] = useState<AgentConfig[]>([]);
  const [selectedConfig, setSelectedConfig] = useState<AgentConfig | null>(null);
  const [isCreating, setIsCreating] = useState<boolean>(false);
  
  // New config form
  const [name, setName] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [provider, setProvider] = useState<string>('mock');
  const [model, setModel] = useState<string>('gpt-4o');
  const [systemPrompt, setSystemPrompt] = useState<string>('');
  const [promptVersion, setPromptVersion] = useState<string>('v1.0.0');
  const [temperature, setTemperature] = useState<number>(0.0);
  const [maxSteps, setMaxSteps] = useState<number>(8);

  useEffect(() => {
    loadConfigs();
  }, []);

  const loadConfigs = async () => {
    try {
      const data = await api.getConfigs();
      setConfigs(data);
      if (data.length > 0 && !selectedConfig) {
        setSelectedConfig(data[0]);
      }
    } catch (err) {
      console.error('Failed to load configs:', err);
    }
  };

  const handleCreateConfig = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name) return;

    try {
      const created = await api.createConfig({
        name,
        description,
        provider,
        model,
        system_prompt: systemPrompt,
        prompt_version: promptVersion,
        temperature,
        max_steps: maxSteps,
        tool_definitions: []
      });
      setConfigs([created, ...configs]);
      setSelectedConfig(created);
      setIsCreating(false);
      setName('');
      setDescription('');
      setSystemPrompt('');
    } catch (err: any) {
      alert(`Create config error: ${err.message}`);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
      
      {/* Header */}
      <div className="border-b border-slate-800 pb-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center space-x-2.5">
            <Cpu className="w-6 h-6 text-cyan-400" />
            <span>Agent Configurations</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Combinations of LLM model, prompt version, system instructions, temperature, and tool definitions to evaluate.
          </p>
        </div>
        <button
          onClick={() => setIsCreating(!isCreating)}
          className="flex items-center space-x-2 bg-cyan-500 hover:bg-cyan-400 text-white text-xs font-semibold px-4 py-2.5 rounded-xl shadow-lg shadow-cyan-500/20 transition"
        >
          <Plus className="w-4 h-4" />
          <span>{isCreating ? 'Cancel' : 'Create Agent Config'}</span>
        </button>
      </div>

      {/* Create Config Form */}
      {isCreating && (
        <form onSubmit={handleCreateConfig} className="bg-slate-900 border border-slate-800 p-6 rounded-2xl space-y-4">
          <h2 className="text-sm font-bold text-white">Create New Agent Configuration</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Config Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Rigorous Fact-Checking Agent"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Provider</label>
              <select
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              >
                <option value="mock">Mock Simulator (Offline Deterministic)</option>
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
                <option value="gemini">Google Gemini</option>
                <option value="generic">Generic OpenAI-Compatible</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Model Name</label>
              <input
                type="text"
                value={model}
                onChange={(e) => setModel(e.target.value)}
                placeholder="gpt-4o, claude-sonnet-4-6, gemini-1.5-pro"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">System Instructions / Prompt</label>
            <textarea
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              placeholder="Define system prompt instructions, guidelines, and tool-use policies..."
              rows={3}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Prompt Version</label>
              <input
                type="text"
                value={promptVersion}
                onChange={(e) => setPromptVersion(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Temperature ({temperature})</label>
              <input
                type="range"
                min={0}
                max={1.5}
                step={0.1}
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                className="w-full accent-cyan-500 cursor-pointer mt-2"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Max Steps ({maxSteps})</label>
              <input
                type="range"
                min={1}
                max={20}
                value={maxSteps}
                onChange={(e) => setMaxSteps(parseInt(e.target.value))}
                className="w-full accent-cyan-500 cursor-pointer mt-2"
              />
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <button
              type="submit"
              className="bg-cyan-500 hover:bg-cyan-400 text-white text-xs font-semibold px-5 py-2 rounded-xl"
            >
              Save Agent Configuration
            </button>
          </div>
        </form>
      )}

      {/* Grid of Configurations */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {configs.map((c) => {
          return (
            <div 
              key={c.id} 
              className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4 hover:border-slate-700 transition"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-sm font-bold text-white">{c.name}</h3>
                  <code className="text-[11px] text-cyan-400 font-mono">{c.model}</code>
                </div>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 uppercase">
                  {c.prompt_version}
                </span>
              </div>

              <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-xs text-slate-400 font-mono line-clamp-3">
                {c.system_prompt || 'No system prompt defined.'}
              </div>

              <div className="grid grid-cols-3 gap-2 text-center text-xs">
                <div className="bg-slate-950/60 p-2 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-500 block">TEMP</span>
                  <strong className="text-slate-200">{c.temperature}</strong>
                </div>
                <div className="bg-slate-950/60 p-2 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-500 block">STEPS</span>
                  <strong className="text-slate-200">{c.max_steps}</strong>
                </div>
                <div className="bg-slate-950/60 p-2 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-500 block">TOOLS</span>
                  <strong className="text-cyan-400">{c.tool_definitions?.length || 0}</strong>
                </div>
              </div>

            </div>
          );
        })}
      </div>

    </div>
  );
};
