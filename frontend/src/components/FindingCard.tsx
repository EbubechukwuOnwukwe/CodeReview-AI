import { useState } from "react";
import type { Finding } from "../types/review";
import { SeverityBadge } from "./SeverityBadge";
import { FiCheckCircle, FiXCircle, FiCode, FiAlertCircle, FiChevronDown, FiChevronUp, FiCopy, FiCheck } from "react-icons/fi";

interface FindingCardProps {
  finding: Finding;
}

export const FindingCard = ({ finding }: FindingCardProps) => {

  const [isExpanded, setIsExpanded] = useState(true);
  const [copied, setCopied] = useState(false);

  const isVerified = finding.verification_status === "verified";
  const confidencePercent = finding.confidence != null ? Math.round(finding.confidence * 100) : 90;

  const handleCopyFix = () => {
    if (finding.suggested_fix) {
      navigator.clipboard.writeText(finding.suggested_fix);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div
      className={`glass-card rounded-2xl border transition-all overflow-hidden ${
        isVerified
          ? "border-emerald-500/30 hover:border-emerald-500/50 shadow-lg shadow-emerald-950/20"
          : "border-slate-800/80 opacity-80"
      }`}
    >
      {/* Header Bar */}
      <div className="p-5 flex items-start justify-between gap-4 bg-slate-900/60 border-b border-slate-800/80">
        <div className="space-y-2 flex-1">
          <div className="flex flex-wrap items-center gap-2.5">
            <SeverityBadge severity={finding.severity} size="sm" />

            {/* Verification Status Badge */}
            {isVerified ? (
              <span className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-md text-xs font-bold bg-emerald-950/80 text-emerald-300 border border-emerald-700/60">
                <FiCheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                <span>✓ VERIFIED — {confidencePercent}% confidence</span>
              </span>
            ) : (
              <span className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-md text-xs font-bold bg-rose-950/80 text-rose-300 border border-rose-700/60">
                <FiXCircle className="w-3.5 h-3.5 text-rose-400" />
                <span>✗ REJECTED BY VERIFIER</span>
              </span>
            )}

            {/* File Path & Line Number */}
            {(finding.file_path || finding.line_number != null) && (
              <span className="inline-flex items-center space-x-1 text-xs font-mono text-indigo-300 bg-indigo-950/60 px-2 py-0.5 rounded border border-indigo-800/40">
                <FiCode className="w-3 h-3 text-indigo-400" />
                <span>
                  {finding.file_path || "source"}
                  {finding.line_number != null ? `:${finding.line_number}` : ""}
                </span>
              </span>
            )}
          </div>

          <h4 className="text-lg font-bold text-white leading-snug">
            {finding.title || finding.explanation || "Code Finding"}
          </h4>
        </div>

        <button
          type="button"
          onClick={() => setIsExpanded(!isExpanded)}
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
        >
          {isExpanded ? <FiChevronUp className="w-5 h-5" /> : <FiChevronDown className="w-5 h-5" />}
        </button>
      </div>

      {/* Body Details */}
      {isExpanded && (
        <div className="p-5 space-y-4 text-sm">
          {/* Explanation */}
          {finding.explanation && (
            <div className="space-y-1">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">
                Explanation
              </span>
              <p className="text-slate-200 leading-relaxed font-sans">
                {finding.explanation}
              </p>
            </div>
          )}

          {/* Verification Reason */}
          {finding.verification_reason && (
            <div className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-xs text-slate-300 flex items-start gap-2.5">
              <FiAlertCircle className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-indigo-300 block mb-0.5">Verifier Notes:</span>
                <span>{finding.verification_reason}</span>
              </div>
            </div>
          )}

          {/* Evidence Code Block */}
          {finding.evidence && (
            <div className="space-y-1.5">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">
                Evidence
              </span>
              <pre className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-rose-300 text-xs font-mono overflow-x-auto leading-relaxed">
                <code>{finding.evidence}</code>
              </pre>
            </div>
          )}

          {/* Suggested Fix */}
          {finding.suggested_fix && (
            <div className="space-y-1.5 pt-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 block">
                  Suggested Fix
                </span>
                <button
                  type="button"
                  onClick={handleCopyFix}
                  className="text-xs text-slate-400 hover:text-white flex items-center space-x-1 px-2 py-1 rounded bg-slate-800/80 hover:bg-slate-700 transition-colors"
                >
                  {copied ? <FiCheck className="w-3.5 h-3.5 text-emerald-400" /> : <FiCopy className="w-3.5 h-3.5" />}
                  <span>{copied ? "Copied" : "Copy Fix"}</span>
                </button>
              </div>
              <pre className="p-3.5 rounded-xl bg-slate-950 border border-emerald-900/60 text-emerald-300 text-xs font-mono overflow-x-auto leading-relaxed">
                <code>{finding.suggested_fix}</code>
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
