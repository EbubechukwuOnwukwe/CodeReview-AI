import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import type { Review } from "../types/review";
import { getReview, retryReview } from "../services/api";
import { FindingCard } from "../components/FindingCard";
import { AgentTrajectory } from "../components/AgentTrajectory";
import { AgentProgress } from "../components/AgentProgress";
import { FiCheckCircle, FiShield, FiAlertTriangle, FiList, FiCpu, FiRefreshCw, FiArrowLeft, FiGithub, FiCode, FiRotateCw } from "react-icons/fi";

export const ReviewResults = () => {
  const { id } = useParams<{ id: string }>();
  const [review, setReview] = useState<Review | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRetrying, setIsRetrying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"verified" | "all" | "trajectory">("verified");

  const fetchReviewData = async () => {
    if (!id) return;
    try {
      const data = await getReview(id);
      setReview(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to load review results.");
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = async () => {
    if (!id) return;
    setIsRetrying(true);
    try {
      const data = await retryReview(id);
      setReview(data);
    } catch (err: any) {
      setError(err.message || "Failed to retry review.");
    } finally {
      setIsRetrying(false);
    }
  };

  const formatErrorMessage = (msg: string | null) => {
    if (!msg) return "An unexpected error occurred during execution.";
    if (msg.includes("429") || msg.includes("RESOURCE_EXHAUSTED") || msg.includes("Quota exceeded")) {
      return "GROQ AI API Rate Limit Reached (429 Resource Exhausted). The free tier API quota was briefly exceeded. Please wait a few moments and click 'Retry Review'.";
    }
    return msg;
  };


  useEffect(() => {
    fetchReviewData();

    // Auto poll if running or pending
    const interval = setInterval(() => {
      if (review?.status === "running" || review?.status === "pending") {
        fetchReviewData();
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [id, review?.status]);

  if (loading) {
    return (
      <div className="py-24 text-center space-y-4">
        <FiRefreshCw className="w-10 h-10 text-indigo-400 animate-spin mx-auto" />
        <p className="text-slate-300 font-semibold text-base">Fetching code review results...</p>
      </div>
    );
  }

  if (error || !review) {
    return (
      <div className="max-w-2xl mx-auto py-16 px-4 text-center space-y-6">
        <div className="glass-panel p-8 rounded-2xl border border-rose-900/50 space-y-4">
          <FiAlertTriangle className="w-12 h-12 text-rose-400 mx-auto" />
          <h2 className="text-2xl font-extrabold text-white">Review Not Found</h2>
          <p className="text-slate-300 text-sm">{error || "Could not locate review data."}</p>
          <Link
            to="/new"
            className="inline-flex items-center space-x-2 px-6 py-3 gradient-btn text-white font-bold text-sm rounded-xl"
          >
            <FiArrowLeft className="w-4 h-4" />
            <span>Submit New Review</span>
          </Link>
        </div>
      </div>
    );
  }

  // Calculate statistics
  const allFindings = review.findings || [];
  const verifiedFindings = allFindings.filter((f) => f.verification_status === "verified");

  const criticalCount = verifiedFindings.filter((f) => f.severity === "critical").length;
  const warningsCount = verifiedFindings.filter((f) => f.severity === "high" || f.severity === "medium").length;
  const suggestionsCount = verifiedFindings.filter((f) => f.severity === "low" || f.severity === "info").length;

  const currentFindingsList = activeTab === "verified" ? verifiedFindings : allFindings;

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-8 pb-16">
      {/* Top Header Navigation */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="space-y-1">
          <div className="flex items-center space-x-3">
            <Link
              to="/"
              className="text-xs font-bold text-slate-400 hover:text-white flex items-center space-x-1"
            >
              <FiArrowLeft className="w-4 h-4" />
              <span>Back to Overview</span>
            </Link>
            <span className="text-slate-600">•</span>
            <span className="text-xs font-mono text-indigo-400 font-bold">Review #{review.id}</span>
          </div>

          <h1 className="text-xl sm:text-2xl lg:text-3xl font-extrabold text-white flex items-center gap-2 min-w-0">
            {review.repository_url ? (
              <span className="flex items-center gap-2 min-w-0">
                <FiGithub className="w-6 h-6 text-indigo-400 shrink-0" />
                <span className="truncate">{review.repository_url.replace("https://github.com/", "")}</span>
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <FiCode className="w-6 h-6 text-indigo-400 shrink-0" />
                Pasted Code ({review.language})
              </span>
            )}
          </h1>
        </div>

        <div className="flex items-center space-x-3">
          <button
            type="button"
            onClick={fetchReviewData}
            className="p-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 transition-colors"
            title="Refresh"
          >
            <FiRefreshCw className="w-4 h-4" />
          </button>

          <span
            className={`px-4 py-1.5 rounded-xl text-xs font-extrabold uppercase tracking-wider ${
              review.status === "completed"
                ? "bg-emerald-950 text-emerald-300 border border-emerald-700/80 shadow-lg shadow-emerald-950/40"
                : review.status === "running"
                ? "bg-indigo-950 text-indigo-300 border border-indigo-700/80 animate-pulse"
                : "bg-rose-950 text-rose-300 border border-rose-700/80"
            }`}
          >
            {review.status}
          </span>
        </div>
      </div>

      {/* If Currently Processing: Render Progress Component */}
      {(review.status === "running" || review.status === "pending") && (
        <AgentProgress status={review.status} stepCount={review.trajectories?.length || 2} />
      )}

      {/* Error Banner if Failed */}
      {review.status === "failed" && (
        <div className="glass-panel p-6 rounded-2xl border border-rose-800/80 bg-rose-950/40 text-rose-200 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 font-bold text-base text-rose-300">
              <FiAlertTriangle className="w-5 h-5 text-rose-400" />
              <span>Execution Error / Rate Limit Encountered</span>
            </div>

            <button
              type="button"
              onClick={handleRetry}
              disabled={isRetrying}
              className="px-4 py-2 bg-rose-900/80 hover:bg-rose-800 text-white font-bold text-xs rounded-xl border border-rose-700/80 flex items-center space-x-2 transition-all shadow-lg shadow-rose-950/50 disabled:opacity-50"
            >
              <FiRotateCw className={`w-4 h-4 ${isRetrying ? "animate-spin" : ""}`} />
              <span>{isRetrying ? "Retrying Review..." : "Retry Review"}</span>
            </button>
          </div>

          <p className="text-xs font-sans leading-relaxed text-slate-300 bg-slate-950 p-4 rounded-xl border border-rose-900/60">
            {formatErrorMessage(review.error_message)}
          </p>
        </div>
      )}


      {/* CODE REVIEW Summary Header Stats (PART 20) */}
      <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-indigo-900/50 shadow-2xl space-y-6">
        <div className="flex flex-wrap items-center justify-between border-b border-slate-800 pb-4 gap-4">
          <div>
            <span className="text-xs font-extrabold uppercase tracking-widest text-indigo-400 block">
              CODE REVIEW SUMMARY
            </span>
            <h2 className="text-2xl font-extrabold text-white flex items-center gap-2 mt-1">
              <span>{verifiedFindings.length} Verified Findings</span>
              <span className="text-xs font-semibold text-slate-400 font-mono">
                ({allFindings.length} raw findings checked)
              </span>
            </h2>
          </div>

          {review.final_report?.risk_level && (
            <div className="flex items-center space-x-2 bg-slate-900 px-4 py-2 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400 uppercase font-bold">Overall Risk:</span>
              <span
                className={`text-xs font-extrabold uppercase tracking-wider px-2.5 py-0.5 rounded ${
                  review.final_report.risk_level.toLowerCase() === "critical" ||
                  review.final_report.risk_level.toLowerCase() === "high"
                    ? "bg-rose-950 text-rose-300 border border-rose-800"
                    : "bg-emerald-950 text-emerald-300 border border-emerald-800"
                }`}
              >
                {review.final_report.risk_level}
              </span>
            </div>
          )}
        </div>

        {/* Severity Counters Grid */}
        <div className="grid grid-cols-3 gap-3 text-center">
          <div className="glass-card p-3 sm:p-4 rounded-xl border border-rose-900/40 bg-rose-950/20 space-y-1">
            <span className="text-[10px] sm:text-xs font-extrabold uppercase tracking-wider text-rose-400 block">
              Critical
            </span>
            <span className="text-2xl sm:text-3xl font-extrabold text-rose-200">{criticalCount}</span>
          </div>

          <div className="glass-card p-3 sm:p-4 rounded-xl border border-amber-900/40 bg-amber-950/20 space-y-1">
            <span className="text-[10px] sm:text-xs font-extrabold uppercase tracking-wider text-amber-400 block">
              Warnings
            </span>
            <span className="text-2xl sm:text-3xl font-extrabold text-amber-200">{warningsCount}</span>
          </div>

          <div className="glass-card p-3 sm:p-4 rounded-xl border border-cyan-900/40 bg-cyan-950/20 space-y-1">
            <span className="text-[10px] sm:text-xs font-extrabold uppercase tracking-wider text-cyan-400 block">
              Suggestions
            </span>
            <span className="text-2xl sm:text-3xl font-extrabold text-cyan-200">{suggestionsCount}</span>
          </div>
        </div>

        {/* Executive Summary Text */}
        {review.final_report?.overall_summary && (
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-sm text-slate-200 leading-relaxed">
            <span className="font-bold text-indigo-300 block mb-1">Executive Summary:</span>
            <p>{review.final_report.overall_summary}</p>
          </div>
        )}
      </div>

      {/* Tabs & Content Switcher */}
      <div className="space-y-6">
        <div className="flex overflow-x-auto border-b border-slate-800 gap-0 scrollbar-none">
          <button
            type="button"
            onClick={() => setActiveTab("verified")}
            className={`py-3 px-4 font-bold text-sm border-b-2 transition-all flex items-center space-x-2 whitespace-nowrap shrink-0 ${
              activeTab === "verified"
                ? "border-emerald-500 text-emerald-400 bg-emerald-950/20"
                : "border-transparent text-slate-400 hover:text-white"
            }`}
          >
            <FiCheckCircle className="w-4 h-4" />
            <span>Verified ({verifiedFindings.length})</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("all")}
            className={`py-3 px-4 font-bold text-sm border-b-2 transition-all flex items-center space-x-2 whitespace-nowrap shrink-0 ${
              activeTab === "all"
                ? "border-indigo-500 text-indigo-400 bg-indigo-950/20"
                : "border-transparent text-slate-400 hover:text-white"
            }`}
          >
            <FiList className="w-4 h-4" />
            <span>All ({allFindings.length})</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("trajectory")}
            className={`py-3 px-4 font-bold text-sm border-b-2 transition-all flex items-center space-x-2 whitespace-nowrap shrink-0 ${
              activeTab === "trajectory"
                ? "border-purple-500 text-purple-400 bg-purple-950/20"
                : "border-transparent text-slate-400 hover:text-white"
            }`}
          >
            <FiCpu className="w-4 h-4" />
            <span>Agent Trajectory ({review.trajectories?.length || 0})</span>
          </button>
        </div>

        {/* Tab Content Display */}
        {activeTab === "trajectory" ? (
          <AgentTrajectory trajectories={review.trajectories || []} />
        ) : (
          <div className="space-y-4">
            {currentFindingsList.length === 0 ? (
              <div className="glass-panel p-12 rounded-2xl border border-slate-800 text-center space-y-3">
                <FiShield className="w-10 h-10 text-emerald-400 mx-auto" />
                <h3 className="text-lg font-bold text-white">No Issues Detected</h3>
                <p className="text-slate-400 text-sm">
                  {activeTab === "verified"
                    ? "No verified security or quality findings were confirmed by the Verification Agent."
                    : "No findings were reported during analysis."}
                </p>
              </div>
            ) : (
              currentFindingsList.map((finding) => (
                <FindingCard key={finding.id} finding={finding} />
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};
