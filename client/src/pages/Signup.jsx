import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { apiFetch } from "../api";
import { setToken } from "../auth";

export default function Signup() {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    // if (password.length < 6) {
    //   setError("Password must be at least 6 characters.");
    //   setLoading(false);
    //   return;
    // }

    // if (password.length > 128) {
    //   setError("Password must be at most 128 characters.");
    //   setLoading(false);
    //   return;
    // }

    try {
      const data = await apiFetch("/auth/signup", {
        method: "POST",
        body: { email, name, password },
      });

      setToken(data.access_token);
      nav("/post-auth"); 
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 420, margin: "40px auto" }}>
      <h1>Signup</h1>

      <form onSubmit={onSubmit}>
        <label>Email</label>
        <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" required style={{ width: "100%", marginBottom: 12 }} />

        <label>Name</label>
        <input value={name} onChange={(e) => setName(e.target.value)} required style={{ width: "100%", marginBottom: 12 }} />

        <label>Password</label>
        <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" required maxLength={128} style={{ width: "100%", marginBottom: 12 }} />

        {error && <p style={{ color: "tomato" }}>{error}</p>}

        <button disabled={loading} type="submit">
          {loading ? "Creating account..." : "Create account"}
        </button>
      </form>

      <p style={{ marginTop: 12 }}>
        Already have an account? <Link to="/login">Login</Link>
      </p>
    </div>
  );
}
