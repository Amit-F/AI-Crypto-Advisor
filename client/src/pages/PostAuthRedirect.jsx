import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../api";
import { clearToken } from "../auth";

export default function PostAuthRedirect() {
  const nav = useNavigate();
  const [error, setError] = useState("");

  useEffect(() => {
    let ignore = false;

    async function run() {
      try {
        const me = await apiFetch("/me", { auth: true });
        if (ignore) return;

        if (me.has_preferences) nav("/dashboard", { replace: true });
        else nav("/onboarding", { replace: true });
      } catch (e) {
        // Token invalid/expired etc. -> force logout
        clearToken();
        if (!ignore) {
          setError(e.message || "Session expired. Please login again.");
          nav("/login", { replace: true });
        }
      }
    }

    run();
    return () => { ignore = true; };
  }, [nav]);

  return (
    <div style={{ maxWidth: 520, margin: "40px auto" }}>
      <h1>Loading…</h1>
      <p>Checking your profile and preferences.</p>
      {error && <p style={{ color: "tomato" }}>{error}</p>}
    </div>
  );
}
