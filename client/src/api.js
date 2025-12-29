import { getToken } from "./auth";

// API helper centralizes backend calls

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function apiFetch(path, { method = "GET", body, auth = false } = {}) {
  const headers = { "Content-Type": "application/json" };

  if (auth) {
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  let data = null;
  const text = await res.text();
  if (text) {
    try { data = JSON.parse(text); } catch { data = { raw: text }; }
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
      // Try to produce the best single message for common cases
      for (const e of data.detail) {
        const field = humanizeField(e.loc);

        // Password min length
        if (field === "Password" && typeof e.msg === "string" && e.msg.includes("at least")) {
          return "Password must be at least 6 characters.";
        }

        // Password max length
        if (field === "Password" && typeof e.msg === "string" && e.msg.includes("at most")) {
          return "Password must be at most 128 characters.";
        }
      }

      // Generic fallback: "Email: value is not a valid email address"
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


//   function extractErrorMessage(data, status) {
//     if (!data) return `Request failed (${status})`;

//     // FastAPI common patterns:
//     // 1) detail is a string
//     if (typeof data.detail === "string") return data.detail;

//     // 2) detail is an array of validation issues (422)
//     if (Array.isArray(data.detail)) {
//         // Try to turn Pydantic errors into readable lines
//         const lines = data.detail.map((e) => {
//         const loc = Array.isArray(e.loc) ? e.loc.join(".") : "";
//         const msg = e.msg || "Validation error";
//         return loc ? `${loc}: ${msg}` : msg;
//         });
//         return lines.join("\n");
//     }

//     // 3) generic message fields
//     if (typeof data.message === "string") return data.message;

//     // 4) fallback to JSON string
//     try {
//         return JSON.stringify(data);
//     } catch {
//         return `Request failed (${status})`;
//     }
//   }


  if (!res.ok) {
    const message = extractErrorMessage(data, res.status);
    const err = new Error(message);
    err.status = res.status;
    err.data = data;
    throw err;
  }

//   if (!res.ok) {
//     const message = data?.detail || data?.message || `Request failed (${res.status})`;
//     const err = new Error(message);
//     err.status = res.status;
//     err.data = data;
//     throw err;
//   }

  return data;
}
