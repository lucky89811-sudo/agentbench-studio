import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { DashboardView } from './components/DashboardView';
import { ReportView } from './components/ReportView';
import { ComparisonView } from './components/ComparisonView';
import { TasksView } from './components/TasksView';
import { ConfigsView } from './components/ConfigsView';
import { PricingView } from './components/PricingView';
import { BatchRunnerModal } from './components/BatchRunnerModal';
import { Task, AgentConfig } from './types';
import { api } from './api/client';

export function App() {
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [activeReportBatchId, setActiveReportBatchId] = useState<string | null>(null);
  const [isBatchModalOpen, setIsBatchModalOpen] = useState<boolean>(false);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [configs, setConfigs] = useState<AgentConfig[]>([]);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [tList, cList] = await Promise.all([
        api.getTasks(),
        api.getConfigs()
      ]);
      setTasks(tList);
      setConfigs(cList);
    } catch (err) {
      console.error('Initial data load error:', err);
    }
  };

  const handleViewReport = (batchId: string) => {
    setActiveReportBatchId(batchId);
    setCurrentTab('report');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Navbar
        currentTab={currentTab}
        setCurrentTab={(tab) => {
          if (tab !== 'report') setActiveReportBatchId(null);
          setCurrentTab(tab);
        }}
        onOpenNewBatch={() => setIsBatchModalOpen(true)}
      />

      <main className="flex-1 pb-16">
        {currentTab === 'dashboard' && (
          <DashboardView
            onOpenNewBatch={() => setIsBatchModalOpen(true)}
            onViewReport={handleViewReport}
            onNavigateTab={(tab) => setCurrentTab(tab)}
          />
        )}

        {currentTab === 'report' && activeReportBatchId && (
          <ReportView
            batchId={activeReportBatchId}
            onBack={() => setCurrentTab('dashboard')}
          />
        )}

        {currentTab === 'tasks' && <TasksView />}

        {currentTab === 'configs' && <ConfigsView />}

        {currentTab === 'comparisons' && (
          <ComparisonView
            tasks={tasks}
            configs={configs}
            onViewReport={handleViewReport}
          />
        )}

        {currentTab === 'pricing' && <PricingView />}
      </main>

      {/* Batch Runner Modal */}
      <BatchRunnerModal
        isOpen={isBatchModalOpen}
        onClose={() => setIsBatchModalOpen(false)}
        tasks={tasks}
        configs={configs}
        onBatchStarted={(bId) => {
          // Can refresh tasks / batches
        }}
        onViewReport={handleViewReport}
      />

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 px-6 py-4 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>AgentBench Studio — AI Agent Reliability, Hallucination & Variance Evaluation</span>
          <span className="text-slate-600">v1.0.0 • Multi-Metric Evaluator Engine</span>
        </div>
      </footer>
    </div>
  );
}

export default App;
