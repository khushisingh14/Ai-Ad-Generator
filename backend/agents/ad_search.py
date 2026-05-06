import json
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

from .apify_fetch import ApifyMetaAdsClient


class SuccessfulAdSearchAgent:
    """Finds recent winning ads, using Apify when configured and mock data otherwise."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.mock_file = data_dir / "mock_successful_ads.json"
        self.output_file = data_dir / "working_ads.json"
        self.raw_output_file = data_dir / "apify_raw_ads.json"
        self.apify = ApifyMetaAdsClient()

    def run(
        self,
        product_url: str,
        niche: str,
        days: int = 30,
        limit: int = 5,
        force_mock: bool = False,
    ) -> dict:
        raw_ads = [] if force_mock else self.apify.search_ads(product_url, niche, days, limit)
        source = "apify" if raw_ads else "mock"
        ads = self._normalize_ads(raw_ads) if raw_ads else self._load_mock_ads()
        selected_ads = self._select_best_recent_ads(ads, days=days, limit=limit)
        self._save_json(selected_ads)
        if raw_ads:
            self._save_raw_json(raw_ads)

        return {
            "source": source,
            "apify": self.apify.status(),
            "used_mock_fallback": source == "mock",
            "selected_ads": selected_ads,
            "saved_to": str(self.output_file),
            "raw_saved_to": str(self.raw_output_file) if raw_ads else "",
        }

    def _normalize_ads(self, items: list[dict]) -> list[dict]:
        normalized_ads = []
        for item in items:
            if not isinstance(item, dict):
                continue
            search_results = item.get("organicResults") or item.get("paidResults") or item.get("results")
            if isinstance(search_results, list):
                normalized_ads.extend(
                    self._normalize_apify_item(result)
                    for result in search_results
                    if isinstance(result, dict)
                )
            else:
                normalized_ads.append(self._normalize_apify_item(item))
        return normalized_ads

    def _normalize_apify_item(self, item: dict) -> dict:
        snapshot = item.get("snapshot") or {}
        page = item.get("page") or {}
        creative = item.get("creative") or {}
        metrics = item.get("metrics") or item.get("performance") or {}
        snapshot_body = snapshot.get("body")
        snapshot_body_text = snapshot_body.get("text") if isinstance(snapshot_body, dict) else snapshot_body

        text = (
            item.get("adText")
            or item.get("text")
            or item.get("body")
            or item.get("ad_creative_body")
            or item.get("description")
            or item.get("snippet")
            or snapshot_body_text
            or snapshot.get("caption")
            or ""
        )
        started_at = (
            item.get("startDate")
            or item.get("startedAt")
            or item.get("createdAt")
            or item.get("ad_delivery_start_time")
            or item.get("start_date")
            or date.today().isoformat()
        )

        return {
            "brand": (
                item.get("pageName")
                or item.get("page_name")
                or item.get("brand")
                or page.get("name")
                or self._domain_from_url(item.get("url"))
                or "Unknown advertiser"
            ),
            "ad_text": text,
            "hook": item.get("headline") or item.get("title") or creative.get("title") or snapshot.get("title") or text[:90],
            "cta": item.get("cta") or item.get("callToAction") or item.get("cta_text") or "Learn More",
            "started_at": started_at[:10],
            "spend": self._metric_value(metrics.get("spend") or item.get("spend")),
            "engagement": self._metric_value(metrics.get("engagement") or item.get("engagement")),
            "impressions": self._metric_value(metrics.get("impressions") or item.get("impressions")),
            "platform": "Meta Ads",
            "url": item.get("url") or item.get("adArchiveUrl") or item.get("ad_snapshot_url") or "",
            "apify_ad_id": str(item.get("adArchiveId") or item.get("ad_id") or item.get("id") or ""),
        }

    def _domain_from_url(self, url: str | None) -> str:
        if not url:
            return ""
        return urlparse(url).netloc.removeprefix("www.")

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

    def _metric_value(self, value) -> float:
        if isinstance(value, dict):
            values = [self._safe_number(item) for item in value.values()]
            return max(values) if values else 0
        if isinstance(value, list):
            values = [self._safe_number(item) for item in value]
            return max(values) if values else 0
        return self._safe_number(value)

    def _save_json(self, ads: list[dict]) -> None:
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with self.output_file.open("w", encoding="utf-8") as file:
            json.dump(ads, file, indent=2)

    def _save_raw_json(self, ads: list[dict]) -> None:
        self.raw_output_file.parent.mkdir(parents=True, exist_ok=True)
        with self.raw_output_file.open("w", encoding="utf-8") as file:
            json.dump(ads, file, indent=2)
