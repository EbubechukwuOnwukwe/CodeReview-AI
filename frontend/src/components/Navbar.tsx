import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { FiCode, FiPlusCircle, FiBarChart2, FiGithub, FiShield, FiMenu, FiX } from "react-icons/fi";

export const Navbar = () => {
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  const isActive = (path: string) => location.pathname === path;

  const navLinks = [
    { to: "/", label: "Overview", icon: <FiCode className="w-4 h-4" /> },
    { to: "/new", label: "New Review", icon: <FiPlusCircle className="w-4 h-4" /> },
    { to: "/evaluation", label: "Evaluation", icon: <FiBarChart2 className="w-4 h-4" /> },
  ];

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <Link to="/" className="flex items-center space-x-3 group shrink-0">
            <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl gradient-btn flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform">
              <FiShield className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
            </div>
            <div className="hidden xs:block sm:block">
              <span className="font-extrabold text-lg sm:text-xl tracking-tight text-white flex items-center gap-2">
                CodeReview <span className="gradient-text">AI</span>
              </span>
              <span className="text-[10px] uppercase font-bold tracking-widest text-indigo-400 block -mt-1 hidden sm:block">
                Multi-Agent Verification
              </span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-1">
            {navLinks.map(({ to, label, icon }) => (
              <Link
                key={to}
                to={to}
                className={`px-3.5 py-2 rounded-lg text-sm font-medium transition-all flex items-center space-x-2 ${
                  isActive(to)
                    ? to === "/new"
                      ? "gradient-btn text-white shadow-lg shadow-indigo-500/20"
                      : to === "/evaluation"
                      ? "bg-purple-600/20 text-purple-300 border border-purple-500/30"
                      : "bg-indigo-600/20 text-indigo-300 border border-indigo-500/30"
                    : to === "/new"
                    ? "bg-indigo-600/20 text-indigo-300 border border-indigo-500/40 hover:bg-indigo-600/30"
                    : "text-slate-300 hover:text-white hover:bg-slate-800/60"
                }`}
              >
                {icon}
                <span>{label}</span>
              </Link>
            ))}

            <a
              href="https://github.com"
              target="_blank"
              rel="noreferrer"
              className="p-2.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/80 transition-colors"
              title="GitHub Repository"
            >
              <FiGithub className="w-5 h-5" />
            </a>
          </nav>

          {/* Mobile: GitHub icon + Hamburger */}
          <div className="flex items-center space-x-2 md:hidden">
            <a
              href="https://github.com"
              target="_blank"
              rel="noreferrer"
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/80 transition-colors"
            >
              <FiGithub className="w-5 h-5" />
            </a>
            <button
              type="button"
              onClick={() => setMobileOpen((o) => !o)}
              className="p-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800/60 transition-colors"
              aria-label="Toggle navigation"
            >
              {mobileOpen ? <FiX className="w-6 h-6" /> : <FiMenu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Dropdown */}
      {mobileOpen && (
        <div className="md:hidden border-t border-slate-800/80 bg-slate-950/95 backdrop-blur-xl">
          <nav className="max-w-7xl mx-auto px-4 py-3 flex flex-col space-y-1">
            {navLinks.map(({ to, label, icon }) => (
              <Link
                key={to}
                to={to}
                onClick={() => setMobileOpen(false)}
                className={`flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all ${
                  isActive(to)
                    ? to === "/new"
                      ? "gradient-btn text-white"
                      : "bg-indigo-600/20 text-indigo-300 border border-indigo-500/30"
                    : "text-slate-300 hover:text-white hover:bg-slate-800/60"
                }`}
              >
                {icon}
                <span>{label}</span>
              </Link>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
};
