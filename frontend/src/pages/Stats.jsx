import React, { useEffect, useMemo, useState } from "react";
import { apiFetch } from "../api.js";

const statLabels = {
  total: "Total",
  toxic: "Flagged",
  safe: "Safe",
  processing: "Processing",
  pending_review: "Review",
  approved: "Approved",
  rejected: "Rejected",
  errors: "Errors"
};

export default function Stats({ apiBase }) {
  const [stats, setStats] = useState(null);
  const [status, setStatus] = useState("Ready to load statistics.");
  const [isLoading, setIsLoading] = useState(false);

  async function refreshStats() {
    setIsLoading(true);
    setStatus("Loading GET /api/stats...");

    try {
      const data = await apiFetch(apiBase, "/api/stats");
      setStats(data);
      setStatus("Statistics loaded.");
    } catch (error) {
      setStatus(error.message);
      setStats(null);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    refreshStats();
  }, []);

  const statusRows = useMemo(() => {
    const rows = [
      ["processing", "Processing", "processing"],
      ["pending_review", "Review", "review"],
      ["approved", "Approved", "approved"],
      ["rejected", "Rejected", "rejected"],
      ["errors", "Errors", "errors"]
    ];

    if (!stats) {
      return rows.map((row) => ({
        key: row[0],
        label: row[1],
        tone: row[2],
        value: 0,
        width: 0
      }));
    }

    const maxStatus = Math.max(
      1,
      ...rows.map(([key]) => Number(stats[key] || 0))
    );

    return rows.map(([key, label, tone]) => {
      const value = Number(stats[key] || 0);
      const width = Math.max(value ? 8 : 0, Math.round((value / maxStatus) * 100));
      return { key, label, tone, value, width };
    });
  }, [stats]);

  const toxicity = useMemo(() => {
    const toxic = Number(stats?.toxic || 0);
    const safe = Number(stats?.safe || 0);
    const total = Math.max(1, toxic + safe);
    const toxicWidth = Math.round((toxic / total) * 100);
    return {
      toxic,
      safe,
      toxicWidth,
      safeWidth: 100 - toxicWidth
    };
  }, [stats]);

  const summary = useMemo(() => {
    const total = Number(stats?.total || 0);
    const toxic = Number(stats?.toxic || 0);
    const safe = Number(stats?.safe || 0);
    const pending = Number(stats?.pending_review || 0);
    const approved = Number(stats?.approved || 0);
    const rejected = Number(stats?.rejected || 0);
    const moderated = Math.max(1, toxic + safe);
    const decisions = approved + rejected;
    const decisionRate = Math.round((decisions / Math.max(1, pending + decisions)) * 100);

    return {
      total,
      toxic,
      safe,
      pending,
      approved,
      rejected,
      flaggedRate: Math.round((toxic / moderated) * 100),
      safeRate: Math.round((safe / moderated) * 100),
      reviewRate: Math.round((pending / Math.max(1, total)) * 100),
      decisionRate,
      moderated
    };
  }, [stats]);

  return (
    <section className="panel">
      <div className="panel-head">
        <div>
          <p className="eyebrow">GET</p>
          <h2>Moderation Statistics</h2>
        </div>
        <button type="button" onClick={refreshStats} disabled={isLoading}>
          {isLoading ? "Loading..." : "Refresh"}
        </button>
      </div>

      <div className="status-line">{status}</div>

      <section className="stats-summary">
        <article className="stat-card">
          <div>
            <p className="stat-label">Total items</p>
            <h3 className="stat-kpi">{summary.total}</h3>
          </div>
          <div className="stat-meta">
            <span className="stat-pill">Moderated {summary.moderated}</span>
            <span className="stat-pill">Pending {summary.pending}</span>
          </div>
        </article>
        <article className="stat-card accent">
          <div>
            <p className="stat-label">Flagged rate</p>
            <h3 className="stat-kpi">{summary.flaggedRate}%</h3>
          </div>
          <div className="stat-meta">
            <span className="stat-pill danger">Flagged {summary.toxic}</span>
            <span className="stat-pill">Safe {summary.safe}</span>
          </div>
          <div className="stat-progress">
            <span style={{ width: `${summary.safeRate}%` }} />
          </div>
        </article>
        <article className="stat-card">
          <div>
            <p className="stat-label">Decision rate</p>
            <h3 className="stat-kpi">{summary.decisionRate}%</h3>
          </div>
          <div className="stat-meta">
            <span className="stat-pill">Review load {summary.reviewRate}%</span>
            <span className="stat-pill">Pending {summary.pending}</span>
          </div>
        </article>
      </section>

      <section className="stats-grid">
        {Object.entries(statLabels).map(([key, label]) => (
          <article className="stat" key={key}>
            <strong>{stats?.[key] ?? 0}</strong>
            <span>{label}</span>
          </article>
        ))}
      </section>

      <section className="chart-layout" aria-label="Moderation charts">
        <article className="chart">
          <h3>Status Distribution</h3>
          <div className="bars">
            {statusRows.map((row) => (
              <div className="bar-row" key={row.key}>
                <div className="bar-label">
                  <span>{row.label}</span>
                  <strong>{row.value}</strong>
                </div>
                <div className="bar-track">
                  <div
                    className={`bar-fill ${row.tone}`}
                    style={{ width: `${row.width}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="chart">
          <h3>Toxicity Split</h3>
          <div className="split">
            <div className="split-meter" aria-label="Toxicity split">
              <div
                className="split-segment toxic"
                style={{ width: `${toxicity.toxicWidth}%` }}
              />
              <div
                className="split-segment safe"
                style={{ width: `${toxicity.safeWidth}%` }}
              />
            </div>
            <div className="split-legend">
              <span>
                <i className="legend-dot toxic" />Flagged {toxicity.toxic}
              </span>
              <span>
                <i className="legend-dot safe" />Safe {toxicity.safe}
              </span>
            </div>
            <div className="donut" style={{ "--toxic": toxicity.toxicWidth }}>
              <strong>{toxicity.toxicWidth}%</strong>
              <span>flagged</span>
            </div>
          </div>
        </article>
      </section>
    </section>
  );
}
