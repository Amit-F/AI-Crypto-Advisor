import { getToken } from "./auth";

// Single source of truth for backend base URL.
// In Vercel, set VITE_API_URL to your Render backend URL, e.g.:
//   https://ai-crypto-advisor-eetg.onrender.com
// Locally, it falls back to http://localhost:8000
const RAW_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Normalize: remove trailing slashes so `${BASE_URL}${path}` is safe.
const BASE_URL = RAW_BASE_URL.replace(/\/+$/, "");

function normalizePath(path) {
  if (!path) return "";
  return path.startsWith("/") ? path : `/${path}`;
}

export async function apiFetch(
  path,
  { method = "GET", body, auth = false } = {}
) {
  const headers = { "Content-Type": "application/json" };

  if (auth) {
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const url = `${BASE_URL}${normalizePath(path)}`;

  const res = await fetch(url, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  let data = null;
  const text = await res.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { raw: text };
    }
  }

  function humanizeField(locArr) {
    // loc looks like ["body", "password"] or ["body", "email"]
    const last = Array.isArray(locArr) ? locArr[locArr.length - 1] : "";
    if (last === "password") return "Password";
    if (last === "email") return "Email";
    if (last === "name") return "Name";
    return last ? last[0].toUpperCase() + last.slice(1) : "Field";
  }

  function extractErrorMessage(data, status) {
    if (!data) return `Request failed (${status})`;

    // FastAPI: detail can be a string
    if (typeof data.detail === "string") return data.detail;

    // FastAPI/Pydantic: detail is an array (422 validation)
    if (Array.isArray(data.detail)) {
      for (const e of data.detail) {
        const field = humanizeField(e.loc);

        // Password min length
        if (
          field === "Password" &&
          typeof e.msg === "string" &&
          e.msg.includes("at least")
        ) {
          return "Password must be at least 6 characters.";
        }

        // Password max length
        if (
          field === "Password" &&
          typeof e.msg === "string" &&
          e.msg.includes("at most")
        ) {
          return "Password must be at most 128 characters.";
        }
      }

      return data.detail
        .map((e) => {
          const field = humanizeField(e.loc);
          const msg = e.msg || "Invalid value";
          return `${field}: ${msg}`;
        })
        .join("\n");
    }

    if (typeof data.message === "string") return data.message;

    try {
      return JSON.stringify(data);
    } catch {
      return `Request failed (${status})`;
    }
  }

  if (!res.ok) {
    const message = extractErrorMessage(data, res.status);
    const err = new Error(message);
    err.status = res.status;
    err.data = data;
    err.url = url;
    throw err;
  }

  return data;
}
