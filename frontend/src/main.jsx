import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API_URL = import.meta.env.VITE_API_URL || "";

function App() {
  const [productUrl, setProductUrl] = useState("https://crowdwisdomtrading.com");
  const [niche, setNiche] = useState("trading research and market signals");
  const [days, setDays] = useState(30);
  const [limit, setLimit] = useState(5);
  const [forceMock, setForceMock] = useState(false);
  const [apifyStatus, setApifyStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/apify-status`)
      .then((response) => response.json())
      .then(setApifyStatus)
      .catch(() => setApifyStatus(null));
  }, []);

  async function generateAd() {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/generate-ad`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          product_url: productUrl,
          niche,
          days: Number(days),
          limit: Number(limit),
          force_mock: forceMock,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "The backend could not generate the ad flow.");
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
        {apifyStatus && (
          <p className={apifyStatus.configured ? "status good" : "status"}>
            Apify: {apifyStatus.configured ? `${apifyStatus.target_type} configured` : "mock fallback"}
          </p>
        )}

        <label>
          Product URL
          <input value={productUrl} onChange={(event) => setProductUrl(event.target.value)} />
        </label>

        <label>
          Niche
          <input value={niche} onChange={(event) => setNiche(event.target.value)} />
        </label>

        <div className="grid">
          <label>
            Last days
            <input
              min="1"
              max="90"
              type="number"
              value={days}
              onChange={(event) => setDays(event.target.value)}
            />
          </label>

          <label>
            Ad limit
            <input
              min="1"
              max="25"
              type="number"
              value={limit}
              onChange={(event) => setLimit(event.target.value)}
            />
          </label>
        </div>

        <label className="checkbox">
          <input
            type="checkbox"
            checked={forceMock}
            onChange={(event) => setForceMock(event.target.checked)}
          />
          Use mock ads instead of Apify
        </label>

        <button onClick={generateAd} disabled={loading}>
          {loading ? "Generating..." : "Generate Ad"}
        </button>

        {error && <p className="error">{error}</p>}
      </section>

      {result && (
        <section className="panel results">
          <div className="meta">
            <span>Source: {result.ad_source}</span>
            <span>Days: {result.search_days}</span>
            <span>Limit: {result.search_limit}</span>
          </div>

          {result.apify?.last_error && <p className="warning">{result.apify.last_error}</p>}

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
                {ad.url && (
                  <a href={ad.url} target="_blank" rel="noreferrer">
                    View ad
                  </a>
                )}
              </article>
            ))}
          </div>

          <h2>Saved Files</h2>
          <pre>{JSON.stringify(result.saved_files, null, 2)}</pre>

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
