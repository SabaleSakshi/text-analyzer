import React, { useMemo, useState } from "react";
import { BrowserRouter, NavLink, Route, Routes } from "react-router-dom";
import { getStoredApiBase, normalizeApiBase, storeApiBase } from "./api.js";
import Home from "./pages/Home.jsx";
import Moderate from "./pages/Moderate.jsx";
import Queue from "./pages/Queue.jsx";
import Stats from "./pages/Stats.jsx";

export default function App() {
  const [apiBase, setApiBase] = useState(getStoredApiBase());

  const normalizedBase = useMemo(() => normalizeApiBase(apiBase), [apiBase]);

  function handleApiBaseChange(event) {
    const nextValue = event.target.value;
    setApiBase(nextValue);
    storeApiBase(nextValue);
  }

  return (
    <BrowserRouter>
      <div className="shell">
        <header className="hero">
          <div>
            <p className="eyebrow">Signal Shield</p>
            <h1>Content Moderation Console</h1>
            <p className="subtitle">
              Review, analyze, and monitor moderation activity in one focused
              workspace.
            </p>
          </div>
          <label className="api-control">
            <span>Backend URL</span>
            <input
              value={apiBase}
              onChange={handleApiBaseChange}
              spellCheck={false}
            />
          </label>
        </header>

        <nav className="nav" aria-label="Moderation pages">
          <NavLink to="/" end>
            Overview
          </NavLink>
          <NavLink to="/moderate">Analyze Text</NavLink>
          <NavLink to="/queue">Review Queue</NavLink>
          <NavLink to="/stats">Statistics</NavLink>
        </nav>

        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/moderate" element={<Moderate apiBase={normalizedBase} />} />
            <Route path="/queue" element={<Queue apiBase={normalizedBase} />} />
            <Route path="/stats" element={<Stats apiBase={normalizedBase} />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
