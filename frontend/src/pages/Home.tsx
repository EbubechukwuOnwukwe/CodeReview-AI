import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import type { Review } from "../types/review";
import { getReviews } from "../services/api";
import { FiPlusCircle, FiShield, FiCheckCircle, FiCpu, FiArrowRight, FiFileText, FiGithub, FiActivity } from "react-icons/fi";

export const Home = () => {

  const [recentReviews, setRecentReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    getReviews()
      .then((data) => setRecentReviews(data.slice(0, 6)))
      .catch((err) => console.error("Failed to load reviews:", err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-12 pb-16">
      {/* Hero Section */}
      <section className="relative pt-12 pb-8 px-4 sm:px-6 lg:px-8 text-center max-w-4xl mx-auto space-y-6">
        <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-indigo-950/80 border border-indigo-700/60 text-indigo-300 text-xs font-bold uppercase tracking-widest shadow-lg shadow-indigo-950/40">
          <FiShield className="w-4 h-4 text-indigo-400" />
          <span>Hackathon Release — Multi-Agent Verification Architecture</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold text-white tracking-tight leading-tight">
          AI-Powered <span className="gradient-text">Verified Code Review</span>
        </h1>

        <p className="text-slate-300 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed">
          Eliminate AI hallucinations and false positives. CodeReview AI uses a 4-agent workflow to analyze requirements, discover bugs, formally verify findings, and produce high-confidence reports.
        </p>

        <div className="pt-4 flex flex-wrap items-center justify-center gap-4">
          <Link
            to="/new"
            className="px-8 py-4 gradient-btn text-white font-extrabold text-base rounded-xl shadow-xl flex items-center space-x-3 group"
          >
            <FiPlusCircle className="w-5 h-5 group-hover:rotate-90 transition-transform" />
            <span>Start Code Review</span>
            <FiArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Link>

          <Link
            to="/evaluation"
            className="px-6 py-4 bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700/80 font-bold text-base rounded-xl transition-all flex items-center space-x-2"
          >
            <FiActivity className="w-5 h-5 text-indigo-400" />
            <span>View Benchmarks</span>
          </Link>
        </div>
      </section>

      {/* 4 Agent Pipeline Cards */}
      <section className="max-w-6xl mx-auto px-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-3">
          <div className="w-10 h-10 rounded-xl bg-blue-900/60 border border-blue-700/40 flex items-center justify-center text-blue-400 font-bold text-sm">
            01
          </div>
          <h3 className="font-bold text-white text-lg">Requirements Agent</h3>
          <p className="text-slate-400 text-xs leading-relaxed">
            Analyzes raw requirements and extracts functional, security, and acceptance criteria.
          </p>
        </div>

        <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-900/60 border border-indigo-700/40 flex items-center justify-center text-indigo-400 font-bold text-sm">
            02
          </div>
          <h3 className="font-bold text-white text-lg">Code Reviewer Agent</h3>
          <p className="text-slate-400 text-xs leading-relaxed">
            Scans submitted codebase for vulnerabilities, logic flaws, edge cases, and anti-patterns.
          </p>
        </div>

        <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-900/60 border border-emerald-700/40 flex items-center justify-center text-emerald-400 font-bold text-sm">
            03
          </div>
          <h3 className="font-bold text-white text-lg">Verification Agent</h3>
          <p className="text-slate-400 text-xs leading-relaxed">
            Independently tests and verifies each finding to reject false positives and unsupported claims.
          </p>
        </div>

        <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-3">
          <div className="w-10 h-10 rounded-xl bg-purple-900/60 border border-purple-700/40 flex items-center justify-center text-purple-400 font-bold text-sm">
            04
          </div>
          <h3 className="font-bold text-white text-lg">Summary Agent</h3>
          <p className="text-slate-400 text-xs leading-relaxed">
            Synthesizes verified findings into executive summary reports and prioritized remediation actions.
          </p>
        </div>
      </section>

      {/* Recent Reviews Table */}
      <section className="max-w-6xl mx-auto px-4">
        <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-slate-800 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h2 className="text-xl font-extrabold text-white flex items-center gap-2">
                <FiFileText className="text-indigo-400" />
                Recent Code Reviews
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Past verified code review executions and results
              </p>
            </div>
            <Link
              to="/new"
              className="text-xs font-bold text-indigo-400 hover:text-indigo-300 flex items-center space-x-1"
            >
              <span>+ New Review</span>
            </Link>
          </div>

          {loading ? (
            <div className="py-12 text-center text-slate-400 text-sm">
              Loading recent reviews...
            </div>
          ) : recentReviews.length === 0 ? (
            <div className="py-12 text-center space-y-3">
              <FiCpu className="w-10 h-10 text-slate-600 mx-auto" />
              <p className="text-slate-400 text-sm">No code reviews submitted yet.</p>
              <Link
                to="/new"
                className="inline-flex items-center space-x-2 text-xs font-bold text-indigo-400 hover:underline"
              >
                <span>Create your first code review</span>
                <FiArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {recentReviews.map((review) => {
                const verifiedCount = review.findings?.filter(
                  (f) => f.verification_status === "verified"
                ).length || 0;

                return (
                  <div
                    key={review.id}
                    onClick={() => navigate(`/review/${review.id}`)}
                    className="glass-card p-5 rounded-xl border border-slate-800 hover:border-indigo-500/50 transition-all cursor-pointer space-y-3"
                  >
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <span className="text-xs font-bold font-mono text-indigo-300">
                          Review #{review.id}
                        </span>
                        <h4 className="font-bold text-white text-sm line-clamp-1">
                          {review.repository_url ? (
                            <span className="flex items-center gap-1.5">
                              <FiGithub className="w-4 h-4 text-slate-400" />
                              {review.repository_url.replace("https://github.com/", "")}
                            </span>
                          ) : (
                            `Source Code (${review.language || "Code"})`
                          )}
                        </h4>
                      </div>

                      <span
                        className={`px-2.5 py-0.5 rounded text-[11px] font-extrabold uppercase ${
                          review.status === "completed"
                            ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                            : review.status === "running"
                            ? "bg-indigo-950 text-indigo-400 border border-indigo-800 animate-pulse"
                            : "bg-slate-800 text-slate-400"
                        }`}
                      >
                        {review.status}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800/80">
                      <span className="flex items-center space-x-1">
                        <FiCheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                        <span>{verifiedCount} Verified Findings</span>
                      </span>

                      <span className="text-indigo-400 font-bold flex items-center gap-1">
                        View Results <FiArrowRight className="w-3 h-3" />
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </section>
    </div>
  );
};
