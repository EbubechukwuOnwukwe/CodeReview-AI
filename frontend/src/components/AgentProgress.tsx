import { FiCheckCircle, FiLoader, FiCircle, FiShield, FiCpu } from "react-icons/fi";

interface AgentProgressProps {
  status: "pending" | "running" | "completed" | "failed";
  stepCount?: number;
  totalSteps?: number;
}

export const AgentProgress = ({ status, stepCount = 2 }: AgentProgressProps) => {

  // Steps definitions
  const steps = [
    { name: "Requirements analyzed", agent: "Requirements Agent", stepNum: 1 },
    { name: "Code reviewed", agent: "Code Reviewer Agent", stepNum: 2 },
    { name: "Verifying findings...", agent: "Verification Agent", stepNum: 3 },
    { name: "Generating final report", agent: "Summary Agent", stepNum: 4 },
  ];

  const getStepStatus = (stepIndex: number) => {
    if (status === "completed") return "completed";
    if (status === "failed") return stepIndex < stepCount ? "completed" : "pending";
    if (stepIndex < stepCount) return "completed";
    if (stepIndex === stepCount) return "active";
    return "pending";
  };

  return (
    <div className="glass-panel p-8 rounded-2xl border border-indigo-900/50 shadow-2xl space-y-6">
      <div className="flex items-center space-x-4 border-b border-slate-800 pb-5">
        <div className="w-12 h-12 rounded-2xl bg-indigo-900/60 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
          <FiCpu className="w-6 h-6 animate-pulse" />
        </div>
        <div>
          <h3 className="text-xl font-extrabold text-white flex items-center gap-2">
            Reviewing your code...
          </h3>
          <p className="text-xs text-indigo-300 font-medium">
            Multi-Agent System executing verification pipeline
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {steps.map((s, idx) => {
          const stepStatus = getStepStatus(idx);

          return (
            <div
              key={s.name}
              className={`flex items-center justify-between p-4 rounded-xl border transition-all ${
                stepStatus === "completed"
                  ? "bg-emerald-950/30 border-emerald-800/40 text-emerald-300"
                  : stepStatus === "active"
                  ? "bg-indigo-950/60 border-indigo-500/60 text-indigo-200 shadow-lg shadow-indigo-500/10"
                  : "bg-slate-900/40 border-slate-800 text-slate-500"
              }`}
            >
              <div className="flex items-center space-x-3.5">
                {stepStatus === "completed" ? (
                  <FiCheckCircle className="w-5 h-5 text-emerald-400 shrink-0" />
                ) : stepStatus === "active" ? (
                  <FiLoader className="w-5 h-5 text-indigo-400 animate-spin shrink-0" />
                ) : (
                  <FiCircle className="w-5 h-5 text-slate-600 shrink-0" />
                )}

                <div>
                  <span className={`font-semibold text-sm block ${
                    stepStatus === "completed" ? "text-emerald-300" : stepStatus === "active" ? "text-indigo-200 font-bold" : "text-slate-400"
                  }`}>
                    {stepStatus === "completed" ? `✓ ${s.name}` : stepStatus === "active" ? `⟳ ${s.name}` : `○ ${s.name}`}
                  </span>
                  <span className="text-[11px] text-slate-500 block font-mono">
                    {s.agent}
                  </span>
                </div>
              </div>

              {stepStatus === "active" && (
                <span className="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider bg-indigo-900/80 text-indigo-300 border border-indigo-700/60 rounded-md animate-pulse">
                  Executing
                </span>
              )}
              {stepStatus === "completed" && (
                <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-emerald-900/40 text-emerald-400 border border-emerald-700/40 rounded-md">
                  Done
                </span>
              )}
            </div>
          );
        })}
      </div>

      <div className="pt-2 text-center text-xs text-slate-400 flex items-center justify-center gap-2">
        <FiShield className="w-4 h-4 text-indigo-400" />
        <span>Verification Agent eliminates hallucinated bugs & false positives</span>
      </div>
    </div>
  );
};
