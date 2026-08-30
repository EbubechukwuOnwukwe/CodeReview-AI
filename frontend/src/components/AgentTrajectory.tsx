import { useState } from "react";
import type { AgentTrajectory as TrajectoryType } from "../types/review";
import { FiCpu, FiCheckCircle, FiXCircle, FiChevronDown, FiChevronUp, FiTerminal, FiLayers } from "react-icons/fi";

interface AgentTrajectoryProps {
  trajectories: TrajectoryType[];
}

export const AgentTrajectory = ({ trajectories }: AgentTrajectoryProps) => {

  const [openIndex, setOpenIndex] = useState<number | null>(null);

  if (!trajectories || trajectories.length === 0) {
    return (
      <div className="glass-panel p-8 rounded-2xl border border-slate-800 text-center text-slate-400 space-y-2">
        <FiCpu className="w-8 h-8 text-indigo-400 mx-auto animate-bounce" />
        <p className="font-semibold text-sm">No agent trajectory recorded yet.</p>
      </div>
    );
  }

  // Sort trajectories by step order then ID
  const sortedTrajectories = [...trajectories].sort((a, b) => a.step - b.step || a.id - b.id);

  const toggleStep = (idx: number) => {
    setOpenIndex(openIndex === idx ? null : idx);
  };

  return (
    <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-indigo-900/40 shadow-2xl space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-purple-900/60 border border-purple-500/30 flex items-center justify-center text-purple-300">
            <FiLayers className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-xl font-extrabold text-white">Agent Execution Trajectory</h3>
            <p className="text-xs text-slate-400">
              Full step-by-step audit trace of agent reasoning, inputs, and outputs
            </p>
          </div>
        </div>
        <span className="px-3 py-1 bg-purple-950 text-purple-300 border border-purple-800/60 rounded-full text-xs font-bold font-mono">
          {sortedTrajectories.length} Steps
        </span>
      </div>

      <div className="space-y-4">
        {sortedTrajectories.map((traj, index) => {
          const isOpen = openIndex === index;
          const stepNumStr = String(index + 1).padStart(2, "0");

          return (
            <div
              key={traj.id || index}
              className="glass-card rounded-xl border border-slate-800/80 overflow-hidden transition-all"
            >
              {/* Header Button */}
              <button
                type="button"
                onClick={() => toggleStep(index)}
                className="w-full p-4 flex items-center justify-between bg-slate-900/80 hover:bg-slate-800/60 transition-colors text-left"
              >
                <div className="flex items-center space-x-3.5">
                  <span className="font-mono text-sm font-extrabold text-indigo-400 bg-indigo-950 px-2.5 py-1 rounded border border-indigo-800/50">
                    {stepNumStr}
                  </span>

                  <div>
                    <h4 className="font-bold text-white text-base flex items-center gap-2">
                      <span>{traj.agent_name}</span>
                    </h4>
                    <span className="text-xs text-slate-400 block font-mono">
                      Step {traj.step} • Status: {traj.status}
                    </span>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  {traj.status === "completed" ? (
                    <span className="inline-flex items-center text-xs font-bold text-emerald-400 bg-emerald-950/80 border border-emerald-800/60 px-2.5 py-1 rounded-md">
                      <FiCheckCircle className="w-3.5 h-3.5 mr-1" />
                      Completed
                    </span>
                  ) : (
                    <span className="inline-flex items-center text-xs font-bold text-rose-400 bg-rose-950/80 border border-rose-800/60 px-2.5 py-1 rounded-md">
                      <FiXCircle className="w-3.5 h-3.5 mr-1" />
                      Failed
                    </span>
                  )}
                  {isOpen ? <FiChevronUp className="w-5 h-5 text-slate-400" /> : <FiChevronDown className="w-5 h-5 text-slate-400" />}
                </div>
              </button>

              {/* Expandable Content */}
              {isOpen && (
                <div className="p-5 border-t border-slate-800 space-y-4 text-xs font-mono bg-slate-950/90">
                  {/* Input Data */}
                  <div className="space-y-1.5">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
                      <FiTerminal className="w-3.5 h-3.5" />
                      Input Data
                    </span>
                    <pre className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 overflow-x-auto max-h-60 leading-relaxed">
                      <code>{JSON.stringify(traj.input_data, null, 2)}</code>
                    </pre>
                  </div>

                  {/* Output Data */}
                  <div className="space-y-1.5">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                      <FiTerminal className="w-3.5 h-3.5" />
                      Output Data
                    </span>
                    <pre className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 text-emerald-300 overflow-x-auto max-h-60 leading-relaxed">
                      <code>{JSON.stringify(traj.output_data, null, 2)}</code>
                    </pre>
                  </div>

                  {/* Error Message if any */}
                  {traj.error_message && (
                    <div className="p-3 rounded-lg bg-rose-950/80 border border-rose-800 text-rose-300 text-xs font-sans">
                      <span className="font-bold block mb-1">Error Trace:</span>
                      <span>{traj.error_message}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
