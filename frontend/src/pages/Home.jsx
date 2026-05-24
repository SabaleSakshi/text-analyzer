import React from "react";
import { Link } from "react-router-dom";

const routes = [
  {
    method: "POST",
    tone: "post",
    path: "/api/moderate",
    description: "Analyze text and return a toxicity score with explainability.",
    link: "/moderate"
  },
  {
    method: "GET",
    tone: "get",
    path: "/api/queue",
    description: "View items waiting for human review.",
    link: "/queue"
  },
  {
    method: "POST",
    tone: "post",
    path: "/api/queue/{id}/decide",
    description: "Approve or reject items in the queue.",
    link: "/queue"
  },
  {
    method: "GET",
    tone: "get",
    path: "/api/stats",
    description: "Monitor moderation totals and review status counts.",
    link: "/stats"
  }
];

export default function Home() {
  return (
    <section className="grid">
      {routes.map((route) => (
        <Link key={route.path} to={route.link} className="card">
          <span className={`pill ${route.tone}`}>{route.method}</span>
          <h2>{route.path}</h2>
          <p>{route.description}</p>
        </Link>
      ))}
    </section>
  );
}
