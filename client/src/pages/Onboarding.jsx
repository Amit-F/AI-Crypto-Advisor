import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { savePreferences } from "../preferencesApi";
import { apiFetch } from "../api";
import TopBar from "../components/TopBar";


const ASSET_OPTIONS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "AVAX", "ADA"];
const INVESTOR_TYPES = ["HODLer", "Day Trader", "NFT Collector", "DeFi Farmer", "Just Curious"];
const CONTENT_TYPES = ["Market News", "Charts", "Social", "Fun", "AI Insights"];

function toggleInList(list, value) {
  return list.includes(value) ? list.filter((x) => x !== value) : [...list, value];
}

export default function Onboarding() {
  const nav = useNavigate();

  const [assets, setAssets] = useState([]);
  const [investorType, setInvestorType] = useState("HODLer");
  const [contentTypes, setContentTypes] = useState(["Market News", "AI Insights"]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // If user already has preferences, will not stay on onboarding
  useEffect(() => {
    let ignore = false;

    (async () => {
      try {
        const me = await apiFetch("/me", { auth: true });
        if (ignore) return;

        if (me.has_preferences) {
          nav("/dashboard", { replace: true });
        }
      } catch {
        // If /me fails (token issues etc.), onboarding isn't blocked here.
        // The route guard (RequireAuth) handles logged-out users.
      }
    })();

    return () => {
      ignore = true;
    };
  }, [nav]);

  const canSubmit = useMemo(() => {
    return assets.length > 0 && investorType && contentTypes.length > 0;
  }, [assets, investorType, contentTypes]);

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await savePreferences({
        assets,
        investor_type: investorType,
        content_types: contentTypes,
      });
      nav("/dashboard", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 700, margin: "40px auto" }}>
      <TopBar />
      <h1>Onboarding</h1>
      <p>Answer a few quick questions so the dashboard can personalize your content!</p>

      <form onSubmit={onSubmit}>
        <section style={{ marginTop: 20 }}>
          <h3>1) What crypto assets are you interested in?</h3>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            {ASSET_OPTIONS.map((a) => (
              <label
                key={a}
                style={{
                  border: "1px solid #444",
                  padding: "8px 10px",
                  borderRadius: 8,
                }}
              >
                <input
                  type="checkbox"
                  checked={assets.includes(a)}
                  onChange={() => setAssets((prev) => toggleInList(prev, a))}
                  style={{ marginRight: 8 }}
                />
                {a}
              </label>
            ))}
          </div>
          {assets.length === 0 && <p style={{ color: "tomato" }}>Pick at least one asset.</p>}
        </section>

        <section style={{ marginTop: 20 }}>
          <h3>2) What type of investor are you?</h3>
          <select value={investorType} onChange={(e) => setInvestorType(e.target.value)}>
            {INVESTOR_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </section>

        <section style={{ marginTop: 20 }}>
          <h3>3) What kind of content would you like to see?</h3>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            {CONTENT_TYPES.map((c) => (
              <label
                key={c}
                style={{
                  border: "1px solid #444",
                  padding: "8px 10px",
                  borderRadius: 8,
                }}
              >
                <input
                  type="checkbox"
                  checked={contentTypes.includes(c)}
                  onChange={() => setContentTypes((prev) => toggleInList(prev, c))}
                  style={{ marginRight: 8 }}
                />
                {c}
              </label>
            ))}
          </div>
          {contentTypes.length === 0 && <p style={{ color: "tomato" }}>Pick at least one content type.</p>}
        </section>

        {error && <p style={{ color: "tomato", marginTop: 12 }}>{error}</p>}

        <button disabled={!canSubmit || loading} type="submit" style={{ marginTop: 20 }}>
          {loading ? "Saving..." : "Save & Continue"}
        </button>
      </form>
    </div>
  );
}
