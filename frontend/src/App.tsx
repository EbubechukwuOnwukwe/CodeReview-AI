import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Navbar } from "./components/Navbar";
import { Home } from "./pages/Home";
import { NewReview } from "./pages/NewReview";
import { ReviewResults } from "./pages/ReviewResults";
import { Evaluation } from "./pages/Evaluation";


function App() {
  return (
    <Router>
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
        {/* Navigation Bar */}
        <Navbar />

        {/* Main Content Area */}
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/new" element={<NewReview />} />
            <Route path="/review/:id" element={<ReviewResults />} />
            <Route path="/evaluation" element={<Evaluation />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="border-t border-slate-900 bg-slate-950 py-5 px-4 text-center text-xs text-slate-500 space-y-1">
          <p className="font-semibold text-slate-400">
            CodeReview AI — Multi-Agent AI Code Verification Engine
          </p>
          <p>© 2026 CodeReview AI • Built with Django &amp; React</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
