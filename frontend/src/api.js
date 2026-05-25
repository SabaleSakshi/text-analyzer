const DEFAULT_API_BASE = "https://content-moderation-backend.onrender.com";
const API_BASE = import.meta.env.VITE_API_BASE || DEFAULT_API_BASE;

export default API_BASE;

export function normalizeApiBase(value) {
  return (value || API_BASE).trim().replace(/\/+$/, "");
}

export function getStoredApiBase() {
  return normalizeApiBase(localStorage.getItem("apiBase") || API_BASE);
}

export function storeApiBase(value) {
  localStorage.setItem("apiBase", normalizeApiBase(value));
}

export async function apiFetch(apiBase, path, options = {}) {
  const response = await fetch(`${normalizeApiBase(apiBase)}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers
    },
    ...options
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with ${response.status}`);
  }

  return response.json();
}

export function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
