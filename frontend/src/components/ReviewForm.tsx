import { useState } from "react";
import { FiGithub, FiCode, FiFileText, FiSend, FiLoader, FiZap } from "react-icons/fi";
import type { CreateReviewPayload } from "../types/review";

interface ReviewFormProps {
  onSubmit: (payload: CreateReviewPayload) => Promise<void>;
  isLoading: boolean;
}

const LANGUAGES = [
  "JavaScript",
  "TypeScript",
  "Python",
  "Java",
  "Go",
  "Rust",
  "C++",
  "C#",
  "PHP",
  "Ruby",
  "Swift",
  "Kotlin",
  "SQL",
];

export const ReviewForm = ({ onSubmit, isLoading }: ReviewFormProps) => {

  const [activeMode, setActiveMode] = useState<"repo" | "code">("repo");
  const [repositoryUrl, setRepositoryUrl] = useState("");
  const [code, setCode] = useState("");
  const [requirements, setRequirements] = useState("");
  const [language, setLanguage] = useState("JavaScript");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (activeMode === "repo" && !repositoryUrl.trim()) {
      setError("Please enter a valid GitHub repository URL.");
      return;
    }

    if (activeMode === "code" && !code.trim()) {
      setError("Please paste the source code to review.");
      return;
    }

    try {
      const payload: CreateReviewPayload = {
        requirements: requirements.trim() || undefined,
        language: activeMode === "code" ? language : undefined,
      };

      if (activeMode === "repo") {
        payload.repository_url = repositoryUrl.trim();
      } else {
        payload.code = code.trim();
      }

      await onSubmit(payload);
    } catch (err: any) {
      setError(err.message || "An error occurred while submitting the code review.");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="glass-panel p-6 sm:p-8 rounded-2xl border border-slate-800 shadow-2xl space-y-6">
      {/* Title Header */}
      <div className="border-b border-slate-800 pb-5">
        <h2 className="text-2xl font-extrabold text-white flex items-center gap-3">
          <FiZap className="text-indigo-400 w-6 h-6" />
          CodeReview <span className="gradient-text">AI</span>
        </h2>
        <p className="text-slate-400 text-sm mt-1">
          AI-powered verified code review via multi-agent architecture
        </p>
      </div>

      {/* Mode Switcher */}
      <div className="flex bg-slate-900/80 p-1.5 rounded-xl border border-slate-800">
        <button
          type="button"
          onClick={() => setActiveMode("repo")}
          className={`flex-1 py-2.5 px-4 rounded-lg font-semibold text-sm transition-all flex items-center justify-center gap-2 ${
            activeMode === "repo"
              ? "bg-indigo-600 text-white shadow-md"
              : "text-slate-400 hover:text-white"
          }`}
        >
          <FiGithub className="w-4 h-4" />
          <span>GitHub Repository</span>
        </button>
        <button
          type="button"
          onClick={() => setActiveMode("code")}
          className={`flex-1 py-2.5 px-4 rounded-lg font-semibold text-sm transition-all flex items-center justify-center gap-2 ${
            activeMode === "code"
              ? "bg-indigo-600 text-white shadow-md"
              : "text-slate-400 hover:text-white"
          }`}
        >
          <FiCode className="w-4 h-4" />
          <span>Paste Code</span>
        </button>
      </div>

      {/* Inputs according to Mode */}
      {activeMode === "repo" ? (
        <div className="space-y-2">
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-300">
            Repository URL
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
              <FiGithub className="w-5 h-5" />
            </div>
            <input
              type="text"
              value={repositoryUrl}
              onChange={(e) => setRepositoryUrl(e.target.value)}
              placeholder="https://github.com/owner/repository"
              className="w-full pl-11 pr-4 py-3 bg-slate-900/90 border border-slate-700/80 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 text-sm font-mono transition-all"
            />
          </div>
          <span className="text-xs text-slate-500 block">
            Public GitHub repository URL to analyze codebase automatically.
          </span>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-300">
                Source Code
              </label>
              <div className="flex items-center space-x-2">
                <span className="text-xs text-slate-400">Language:</span>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="bg-slate-900 border border-slate-700 rounded-lg text-xs font-semibold text-indigo-300 px-3 py-1.5 focus:outline-none focus:border-indigo-500"
                >
                  {LANGUAGES.map((lang) => (
                    <option key={lang} value={lang}>
                      {lang}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              rows={9}
              placeholder="Paste your source code here..."
              className="w-full p-4 bg-slate-950/90 border border-slate-800 rounded-xl text-emerald-400 placeholder-slate-600 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 font-mono text-sm leading-relaxed transition-all resize-y"
            />
          </div>
        </div>
      )}

      {/* Requirements Input */}
      <div className="space-y-2">
        <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center justify-between">
          <span>Requirements / Expectations</span>
          <span className="text-slate-500 text-[11px] normal-case font-normal">(Optional)</span>
        </label>
        <div className="relative">
          <textarea
            value={requirements}
            onChange={(e) => setRequirements(e.target.value)}
            rows={3}
            placeholder="What should this code accomplish? (e.g., Add user authentication with JWT token verification and password hashing...)"
            className="w-full p-3.5 bg-slate-900/90 border border-slate-700/80 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 text-sm transition-all"
          />
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-rose-950/60 border border-rose-800/80 rounded-xl p-3.5 text-rose-300 text-xs flex items-center gap-2">
          <FiFileText className="w-4 h-4 shrink-0 text-rose-400" />
          <span>{error}</span>
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-4 px-6 gradient-btn text-white font-extrabold text-base rounded-xl shadow-lg flex items-center justify-center space-x-3 group disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? (
          <>
            <FiLoader className="w-5 h-5 animate-spin" />
            <span>Initiating Agents...</span>
          </>
        ) : (
          <>
            <FiSend className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            <span>Review Code</span>
          </>
        )}
      </button>
    </form>
  );
};
