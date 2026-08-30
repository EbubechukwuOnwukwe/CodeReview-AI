import type { Severity } from "../types/review";

interface SeverityBadgeProps {
  severity: Severity | string;
  size?: "sm" | "md" | "lg";
}

export const SeverityBadge = ({ severity, size = "md" }: SeverityBadgeProps) => {

  const normSeverity = (severity || "info").toLowerCase();

  let colorClasses = "bg-slate-800 text-slate-300 border-slate-700";
  
  switch (normSeverity) {
    case "critical":
      colorClasses = "bg-rose-950/80 text-rose-300 border-rose-700/60 shadow-rose-900/30";
      break;
    case "high":
      colorClasses = "bg-amber-950/80 text-amber-300 border-amber-700/60 shadow-amber-900/30";
      break;
    case "medium":
    case "warning":
    case "warnings":
      colorClasses = "bg-yellow-950/70 text-yellow-300 border-yellow-700/50";
      break;
    case "low":
    case "info":
    case "suggestion":
    case "suggestions":
      colorClasses = "bg-cyan-950/70 text-cyan-300 border-cyan-700/50";
      break;
  }

  const sizeClasses = {
    sm: "px-2 py-0.5 text-xs font-semibold tracking-wider",
    md: "px-2.5 py-1 text-xs font-bold tracking-wider",
    lg: "px-3.5 py-1.5 text-sm font-extrabold tracking-widest",
  }[size];

  return (
    <span
      className={`inline-flex items-center uppercase rounded-md border shadow-sm ${colorClasses} ${sizeClasses}`}
    >
      {normSeverity}
    </span>
  );
};
