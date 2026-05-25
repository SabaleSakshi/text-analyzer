import React, { useState } from "react";
import { apiFetch, sleep } from "../api.js";

function badgeClass(item) {
  if (item.status === "ERROR" || item.severity === "HIGH") {
    return "danger";
  }

  if (item.status === "PENDING_REVIEW" || item.is_toxic) {
    return "warn";
  }

  if (item.status === "APPROVED") {
    return "safe";
  }

  return "";
}

function Labels({ labels }) {
  const entries = Object.entries(labels || {});

  if (!entries.length) {
    return null;
  }

  return (
    <div className="labels">
      {entries.map(([label, score]) => (
        <div className="label" key={label}>
          <span>{label.replaceAll("_", " ")}</span>
          <strong>{Math.round(Number(score) * 100)}%</strong>
        </div>
      ))}
    </div>
  );
}

export default function Moderate({ apiBase }) {
  const [text, setText] = useState("");
  const [status, setStatus] = useState("Ready when you are.");
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  async function pollModeration(id) {
    let lastItem = null;

    for (let attempt = 0; attempt < 120; attempt += 1) {
      const item = await apiFetch(apiBase, `/api/moderate/${id}`);
      lastItem = item;
      setResult(item);

      if (item.status !== "PROCESSING") {
        setStatus(
          item.status === "ERROR"
            ? "Analysis failed. Check that the AI service is running."
            : "Analysis complete."
        );
        return item;
      }

      setStatus("AI explainability is still running. Waiting for the result...");
      await sleep(2000);
    }

    setStatus("Still processing. Refresh by id later if needed.");
    return lastItem;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setIsLoading(true);
    setStatus("Submitting text to POST /api/moderate...");
    setResult(null);

    try {
      const created = await apiFetch(apiBase, "/api/moderate", {
        method: "POST",
        body: JSON.stringify({ text: text.trim() })
      });

      setResult(created);
      await pollModeration(created.id);
    } catch (error) {
      setStatus(error.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="panel">
      <div className="panel-head">
        <div>
          <p className="eyebrow">POST</p>
          <h2>Analyze Text</h2>
        </div>
        <button type="submit" form="moderationForm" disabled={isLoading}>
          {isLoading ? "Working..." : "Analyze"}
        </button>
      </div>

      <form id="moderationForm" onSubmit={handleSubmit}>
        <textarea
          value={text}
          onChange={(event) => setText(event.target.value)}
          required
          minLength={2}
          placeholder="Paste or type user text here"
        />
      </form>

      <div className="status-line">{status}</div>

      {result && (
        <article className="result-card">
          <div className="row">
            <span className={`badge ${badgeClass(result)}`}>{result.status}</span>
            {result.severity && <span className="badge">{result.severity}</span>}
            {result.confidence !== null && result.confidence !== undefined && (
              <span className="badge">
                {Math.round(result.confidence * 100)}% confidence
              </span>
            )}
          </div>
          <p className="result-text">{result.text}</p>
          {result.reason && <div className="reason">{result.reason}</div>}
          {result.error && <div className="reason danger">{result.error}</div>}
          <Labels labels={result.labels} />
        </article>
      )}
    </section>
  );
}
