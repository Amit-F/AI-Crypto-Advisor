import { apiFetch } from "./api";

export function getDashboard() {
  return apiFetch("/dashboard", { auth: true });
}

export function voteOnItem(dashboard_item_id, value) {
  return apiFetch("/votes", { method: "POST", auth: true, body: { dashboard_item_id, value } });
}
