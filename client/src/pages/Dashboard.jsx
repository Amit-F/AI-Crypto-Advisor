import { useEffect, useState } from "react";
import { getDashboard, voteOnItem } from "../dashboardApi";
import { clearToken } from "../auth";
import { useNavigate } from "react-router-dom";

function SectionCard({ title, children }) {
  return (
    <div style={{ border: "1px solid #444", borderRadius: 12, padding: 16, marginBottom: 14 }}>
      <h2 style={{ marginTop: 0 }}>{title}</h2>
      {children}
    </div>
  );
}

function VoteButtons({ itemId, currentVote, onVote }) {
  const upActive = currentVote === 1;
  const downActive = currentVote === -1;

  return (
    <div style={{ display: "flex", gap: 10, marginTop: 12 }}>
      <button
        onClick={() => onVote(itemId, 1)}
        style={{ opacity: upActive ? 1 : 0.6 }}
        title="Thumbs up"
        type="button"
      >
        👍
      </button>
      <button
        onClick={() => onVote(itemId, -1)}
        style={{ opacity: downActive ? 1 : 0.6 }}
        title="Thumbs down"
        type="button"
      >
        👎
      </button>
    </div>
  );
}

export default function Dashboard() {
  const nav = useNavigate();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [data, setData] = useState(null);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const d = await getDashboard();
      setData(d);
    } catch (e) {
      // if token is invalid/expired, force logout
      if (e.status === 401) {
        clearToken();
        nav("/login", { replace: true });
        return;
      }
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleVote(itemId, value) {
    // optimistic UI update
    setData((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        items: prev.items.map((it) =>
          it.id === itemId ? { ...it, user_vote: value } : it
        ),
      };
    });

    try {
      await voteOnItem(itemId, value);
    } catch (e) {
      // revert on failure
      setData((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          items: prev.items.map((it) =>
            it.id === itemId ? { ...it, user_vote: null } : it
          ),
        };
      });
      setError(e.message);
    }
  }

  if (loading) return <div style={{ maxWidth: 900, margin: "40px auto" }}><h1>Dashboard</h1><p>Loading…</p></div>;

  if (error)
    return (
      <div style={{ maxWidth: 900, margin: "40px auto" }}>
        <h1>Dashboard</h1>
        <p style={{ color: "tomato" }}>{error}</p>
        <button onClick={load} type="button">Retry</button>
      </div>
    );

  const itemsByType = Object.fromEntries((data?.items || []).map((it) => [it.item_type, it]));
  const news = itemsByType.news;
  const prices = itemsByType.prices;
  const ai = itemsByType.ai;
  const meme = itemsByType.meme;

  return (
    <div style={{ maxWidth: 900, margin: "40px auto" }}>
      <h1>Dashboard</h1>
      <p style={{ opacity: 0.8 }}>Date: {data.date}</p>

      {news && (
        <SectionCard title="Market News">
          <p><b>{news.payload.title}</b></p>
          <p style={{ opacity: 0.8 }}>{news.payload.summary}</p>
          <a href={news.payload.url} target="_blank" rel="noreferrer">
            Source: {news.payload.source}
          </a>

          <VoteButtons itemId={news.id} currentVote={news.user_vote} onVote={handleVote} />
        </SectionCard>
      )}

      {prices && (
        <SectionCard title="Coin Prices">
          <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(prices.payload, null, 2)}</pre>
          <VoteButtons itemId={prices.id} currentVote={prices.user_vote} onVote={handleVote} />
        </SectionCard>
      )}

      {ai && (
        <SectionCard title="AI Insight">
          <p>{ai.payload.text}</p>
          <VoteButtons itemId={ai.id} currentVote={ai.user_vote} onVote={handleVote} />
        </SectionCard>
      )}

      {meme && (
        <SectionCard title="Meme">
          <p style={{ opacity: 0.8 }}>{meme.payload.caption}</p>
          <img
            src={meme.payload.imageUrl}
            alt="meme"
            style={{ maxWidth: "100%", borderRadius: 12 }}
          />
          <VoteButtons itemId={meme.id} currentVote={meme.user_vote} onVote={handleVote} />
        </SectionCard>
      )}
    </div>
  );
}
