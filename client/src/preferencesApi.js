import { apiFetch } from "./api";

// helper that keeps pages clean

export function savePreferences(prefs) {
  return apiFetch("/preferences", { method: "POST", body: prefs, auth: true });
}

export function getPreferences() {
  return apiFetch("/preferences", { method: "GET", auth: true });
}
