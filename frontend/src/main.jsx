import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [productUrl, setProductUrl] = useState("https://crowdwisdomtrading.com");
  const [niche, setNiche] = useState("trading research and market signals");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  async function generateAd() {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/generate-ad`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_url: productUrl, niche }),
      });

      if (!response.ok) {
        throw new Error("The backend could not generate the ad flow.");
      }

      setResult(await response.json());
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <section className="panel">
        <h1>AI Ad Generator</h1>

        <label>
          Product URL
          <input value={productUrl} onChange={(event) => setProductUrl(event.target.value)} />
        </label>

        <label>
          Niche
          <input value={niche} onChange={(event) => setNiche(event.target.value)} />
        </label>

        <button onClick={generateAd} disabled={loading}>
          {loading ? "Generating..." : "Generate Ad"}
        </button>

        {error && <p className="error">{error}</p>}
      </section>

      {result && (
        <section className="panel results">
          <ResultList title="Pain Points" items={result.pain_points} />
          <ResultList title="Marketing Angles" items={result.marketing_angles} />
          <ResultList title="Concepts" items={result.concepts} />

          <h2>Generated Script</h2>
          <pre>{result.ad_script}</pre>

          <h2>Selected Working Ads</h2>
          <div className="ads">
            {result.selected_ads.map((ad) => (
              <article className="ad" key={`${ad.brand}-${ad.started_at}`}>
                <strong>{ad.brand}</strong>
                <span>{ad.started_at}</span>
                <p>{ad.hook}</p>
              </article>
            ))}
          </div>

          <h2>Video Plan</h2>
          <p className="muted">Remotion input, voice text, and subtitles were saved by the backend.</p>
          <pre>{JSON.stringify(result.video_plan, null, 2)}</pre>
        </section>
      )}
    </main>
  );
}

function ResultList({ title, items = [] }) {
  return (
    <>
      <h2>{title}</h2>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </>
  );
}

createRoot(document.getElementById("root")).render(<App />);
