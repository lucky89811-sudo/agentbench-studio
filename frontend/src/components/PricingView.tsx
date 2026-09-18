import React, { useState, useEffect } from 'react';
import { DollarSign, Edit3, Save, Check, RefreshCw } from 'lucide-react';
import { PricingModel } from '../types';
import { api } from '../api/client';

export const PricingView: React.FC = () => {
  const [pricingList, setPricingList] = useState<PricingModel[]>([]);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editInputPrice, setEditInputPrice] = useState<number>(0);
  const [editOutputPrice, setEditOutputPrice] = useState<number>(0);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadPricing();
  }, []);

  const loadPricing = async () => {
    try {
      const data = await api.getPricing();
      setPricingList(data);
    } catch (err) {
      console.error('Failed to load pricing table:', err);
    }
  };

  const startEdit = (item: PricingModel) => {
    setEditingId(item.id);
    setEditInputPrice(item.input_price_per_m);
    setEditOutputPrice(item.output_price_per_m);
  };

  const handleSave = async (id: string) => {
    setIsSaving(true);
    try {
      const updated = await api.updatePricing(id, editInputPrice, editOutputPrice);
      setPricingList(pricingList.map(p => p.id === id ? updated : p));
      setEditingId(null);
      setSaveSuccess(id);
      setTimeout(() => setSaveSuccess(null), 2000);
    } catch (err: any) {
      alert(`Failed to update pricing: ${err.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
      
      {/* Header */}
      <div className="border-b border-slate-800 pb-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center space-x-2.5">
            <DollarSign className="w-6 h-6 text-cyan-400" />
            <span>Model Pricing & Cost Table</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Maintain exact per-token pricing rates (USD per 1 Million tokens). Used to instrument total run cost and the headline metric: Cost per Successful Task.
          </p>
        </div>
        <button
          onClick={loadPricing}
          className="flex items-center space-x-1.5 text-xs text-slate-400 hover:text-white px-3 py-1.5 rounded-lg hover:bg-slate-800 transition"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Rates</span>
        </button>
      </div>

      {/* Pricing Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider text-[10px]">
              <tr>
                <th className="px-6 py-3.5 font-semibold">Model Name</th>
                <th className="px-5 py-3.5 font-semibold">Provider</th>
                <th className="px-5 py-3.5 font-semibold">Input Tokens ($ / 1M)</th>
                <th className="px-5 py-3.5 font-semibold">Output Tokens ($ / 1M)</th>
                <th className="px-5 py-3.5 font-semibold">Last Updated</th>
                <th className="px-6 py-3.5 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-200">
              {pricingList.map((item) => {
                const isEditing = editingId === item.id;
                const wasSaved = saveSuccess === item.id;
                return (
                  <tr key={item.id} className="hover:bg-slate-800/40 transition">
                    <td className="px-6 py-4 font-bold text-white">
                      <code className="text-cyan-400 font-mono text-xs">{item.model_name}</code>
                    </td>
                    <td className="px-5 py-4 uppercase text-[11px] font-semibold text-slate-400">
                      {item.provider}
                    </td>
                    <td className="px-5 py-4 font-mono">
                      {isEditing ? (
                        <div className="flex items-center space-x-1">
                          <span className="text-slate-400">$</span>
                          <input
                            type="number"
                            step="0.01"
                            value={editInputPrice}
                            onChange={(e) => setEditInputPrice(parseFloat(e.target.value) || 0)}
                            className="w-24 bg-slate-950 border border-cyan-500 rounded px-2 py-1 text-xs text-white"
                          />
                        </div>
                      ) : (
                        <span className="text-slate-200 font-semibold">${item.input_price_per_m.toFixed(3)}</span>
                      )}
                    </td>
                    <td className="px-5 py-4 font-mono">
                      {isEditing ? (
                        <div className="flex items-center space-x-1">
                          <span className="text-slate-400">$</span>
                          <input
                            type="number"
                            step="0.01"
                            value={editOutputPrice}
                            onChange={(e) => setEditOutputPrice(parseFloat(e.target.value) || 0)}
                            className="w-24 bg-slate-950 border border-cyan-500 rounded px-2 py-1 text-xs text-white"
                          />
                        </div>
                      ) : (
                        <span className="text-slate-200 font-semibold">${item.output_price_per_m.toFixed(3)}</span>
                      )}
                    </td>
                    <td className="px-5 py-4 text-slate-500 text-[11px]">
                      {item.updated_at ? item.updated_at.slice(0, 10) : 'Active'}
                    </td>
                    <td className="px-6 py-4 text-right">
                      {isEditing ? (
                        <div className="flex items-center justify-end space-x-2">
                          <button
                            onClick={() => setEditingId(null)}
                            className="text-slate-400 hover:text-white text-xs px-2 py-1 rounded"
                          >
                            Cancel
                          </button>
                          <button
                            onClick={() => handleSave(item.id)}
                            disabled={isSaving}
                            className="flex items-center space-x-1 bg-emerald-500 hover:bg-emerald-400 text-white text-xs font-semibold px-3 py-1 rounded-lg"
                          >
                            <Save className="w-3.5 h-3.5" />
                            <span>Save</span>
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => startEdit(item)}
                          className="inline-flex items-center space-x-1 text-cyan-400 hover:text-cyan-300 font-medium"
                        >
                          {wasSaved ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Edit3 className="w-3.5 h-3.5" />}
                          <span>{wasSaved ? 'Saved' : 'Edit Rate'}</span>
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
