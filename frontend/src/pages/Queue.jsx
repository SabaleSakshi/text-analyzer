import React, { useEffect, useState } from "react";
import { apiFetch } from "../api.js";

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

export default function Queue({ apiBase }) {
  const [items, setItems] = useState([]);
  const [status, setStatus] = useState("Ready to load the queue.");
  const [isLoading, setIsLoading] = useState(false);

  async function refreshQueue() {
    setIsLoading(true);
    setStatus("Loading GET /api/queue...");

    try {
      const data = await apiFetch(apiBase, "/api/queue");
      setItems(data);
      setStatus("Queue loaded.");
    } catch (error) {
      setStatus(error.message);
      setItems([]);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleDecision(itemId, decision) {
    setStatus(`Submitting POST /api/queue/${itemId}/decide...`);

    try {
      await apiFetch(apiBase, `/api/queue/${itemId}/decide`, {
        method: "POST",
        body: JSON.stringify({ decision })
      });
      await refreshQueue();
    } catch (error) {
      setStatus(error.message);
    }
  }

  useEffect(() => {
    refreshQueue();
  }, []);

  return (
    <section className="panel">
      <div className="panel-head">
        <div>
          <p className="eyebrow">GET + POST</p>
          <h2>Human Review Queue</h2>
        </div>
        <button type="button" onClick={refreshQueue} disabled={isLoading}>
          {isLoading ? "Loading..." : "Refresh"}
        </button>
      </div>

      <div className="status-line">{status}</div>

      <div className="stack">
        {items.length === 0 ? (
          <div className="empty">No items waiting for review.</div>
        ) : (
          items.map((item) => (
            <article className="queue-item" key={item.id}>
              <div className="row">
                <span className={`badge ${badgeClass(item)}`}>
                  {item.severity || item.status}
                </span>
                <span className="badge">
                  {Math.round((item.confidence || 0) * 100)}% confidence
                </span>
              </div>
              <p className="result-text">{item.text}</p>
              <div className="reason">
                {item.reason || "No explanation available."}
              </div>
              <div className="row queue-actions">
                <button
                  type="button"
                  className="secondary"
                  onClick={() => handleDecision(item.id, "APPROVED")}
                >
                  Approve
                </button>
                <button
                  type="button"
                  className="danger"
                  onClick={() => handleDecision(item.id, "REJECTED")}
                >
                  Reject
                </button>
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
