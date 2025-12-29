import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { clearToken } from "../auth";
import { apiFetch } from "../api";

export default function TopBar() {
  const nav = useNavigate();
  const [name, setName] = useState("");

  useEffect(() => {
    let ignore = false;

    (async () => {
      try {
        const me = await apiFetch("/me", { auth: true });
        if (!ignore) setName(me.name);
      } catch {
        // ignore; if token invalid, other guards will redirect
      }
    })();

    return () => {
      ignore = true;
    };
  }, []);

  function logout() {
    clearToken();
    nav("/login", { replace: true });
  }

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: 18,
        paddingBottom: 12,
        borderBottom: "1px solid #444",
      }}
    >
      <div style={{ opacity: 0.9 }}>
        <b>AI Crypto Advisor</b>
        {name ? <span style={{ marginLeft: 10, opacity: 0.7 }}>({name})</span> : null}
      </div>

      <button onClick={logout} type="button">
        Logout
      </button>
    </div>
  );
}

