import React from 'react';
import { 
  ShieldCheck, 
  BarChart3, 
  Layers, 
  Cpu, 
  GitCompare, 
  DollarSign, 
  PlayCircle,
  Activity
} from 'lucide-react';

interface NavbarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  onOpenNewBatch: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentTab, setCurrentTab, onOpenNewBatch }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Activity },
    { id: 'tasks', label: 'Benchmark Tasks', icon: Layers },
    { id: 'configs', label: 'Agent Configs', icon: Cpu },
    { id: 'comparisons', label: 'Comparisons', icon: GitCompare },
    { id: 'pricing', label: 'Pricing Table', icon: DollarSign },
  ];

  return (
    <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-40 px-6 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Logo & Brand */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setCurrentTab('dashboard')}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <ShieldCheck className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg tracking-tight text-white">AgentBench</span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">STUDIO</span>
            </div>
            <p className="text-[11px] text-slate-400">Quantitative AI Agent Reliability Evaluator</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1 bg-slate-950/60 p-1 rounded-xl border border-slate-800">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentTab(item.id)}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  active
                    ? 'bg-cyan-500 text-white shadow-md shadow-cyan-500/25'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Action Button */}
        <div className="flex items-center space-x-3">
          <div className="hidden md:flex items-center space-x-2 text-xs text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Evaluator Engine Ready</span>
          </div>
          <button
            onClick={onOpenNewBatch}
            className="flex items-center space-x-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-semibold px-4 py-2 rounded-lg shadow-lg shadow-cyan-500/20 transition-all transform active:scale-95"
          >
            <PlayCircle className="w-4 h-4" />
            <span>New Reliability Run</span>
          </button>
        </div>
      </div>
    </header>
  );
};
