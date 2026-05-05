import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib import request
from urllib.error import URLError


class SuccessfulAdSearchAgent:
    """Finds recent winning ads, using Apify when configured and mock data otherwise."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.mock_file = data_dir / "mock_successful_ads.json"
        self.output_file = data_dir / "working_ads.json"

    def run(self, product_url: str, niche: str, days: int = 30, limit: int = 5) -> dict:
        ads = self._load_from_apify(product_url, niche) or self._load_mock_ads()
        selected_ads = self._select_best_recent_ads(ads, days=days, limit=limit)
        self._save_json(selected_ads)

        return {
            "source": "apify" if os.getenv("APIFY_TOKEN") else "mock",
            "selected_ads": selected_ads,
            "saved_to": str(self.output_file),
        }

    def _load_from_apify(self, product_url: str, niche: str) -> list[dict]:
        token = os.getenv("APIFY_TOKEN")
        actor_id = os.getenv("APIFY_META_ADS_ACTOR_ID")
        if not token or not actor_id:
            return []

        url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items?token={token}"
        payload = json.dumps(
            {
                "query": product_url,
                "niche": niche,
                "platform": "facebook",
                "activeWithinDays": 30,
            }
        ).encode("utf-8")

        req = request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=45) as response:
                raw_items = json.loads(response.read().decode("utf-8"))
        except (OSError, URLError, json.JSONDecodeError):
            return []

        return [self._normalize_apify_item(item) for item in raw_items if isinstance(item, dict)]

    def _normalize_apify_item(self, item: dict) -> dict:
        text = item.get("adText") or item.get("text") or item.get("body") or ""
        started_at = item.get("startDate") or item.get("startedAt") or item.get("createdAt") or ""
        metrics = item.get("metrics") or {}

        return {
            "brand": item.get("pageName") or item.get("brand") or "Unknown advertiser",
            "ad_text": text,
            "hook": item.get("headline") or text[:90],
            "cta": item.get("cta") or item.get("callToAction") or "Learn More",
            "started_at": started_at[:10],
            "spend": self._safe_number(metrics.get("spend") or item.get("spend"), default=0),
            "engagement": self._safe_number(metrics.get("engagement") or item.get("engagement"), default=0),
            "impressions": self._safe_number(metrics.get("impressions") or item.get("impressions"), default=0),
            "platform": "Meta Ads",
            "url": item.get("url") or item.get("adArchiveUrl") or "",
        }

    def _load_mock_ads(self) -> list[dict]:
        with self.mock_file.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _select_best_recent_ads(self, ads: list[dict], days: int, limit: int) -> list[dict]:
        cutoff = date.today() - timedelta(days=days)
        recent_ads = [ad for ad in ads if self._parse_date(ad.get("started_at")) >= cutoff]
        if not recent_ads:
            recent_ads = ads
        scored_ads = sorted(recent_ads, key=self._score_ad, reverse=True)
        return scored_ads[:limit]

    def _score_ad(self, ad: dict) -> float:
        engagement = self._safe_number(ad.get("engagement"))
        impressions = max(self._safe_number(ad.get("impressions")), 1)
        spend = max(self._safe_number(ad.get("spend")), 1)
        engagement_rate = engagement / impressions
        return (engagement_rate * 1000) + (engagement / spend)

    def _parse_date(self, value: str | None) -> date:
        if not value:
            return date.min
        try:
            return datetime.strptime(value[:10], "%Y-%m-%d").date()
        except ValueError:
            return date.min

    def _safe_number(self, value, default: float = 0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _save_json(self, ads: list[dict]) -> None:
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with self.output_file.open("w", encoding="utf-8") as file:
            json.dump(ads, file, indent=2)
