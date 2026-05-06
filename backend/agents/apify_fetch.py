import json
import os
from dataclasses import dataclass
from pathlib import Path
from urllib import request


def load_local_env() -> None:
    paths = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parents[2] / ".env",
    ]

    for path in paths:
        if not path.exists():
            continue
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@dataclass
class ApifySettings:
    token: str
    timeout_seconds: int
    max_items: int

    @classmethod
    def from_env(cls) -> "ApifySettings":
        load_local_env()
        return cls(
            token=os.getenv("APIFY_TOKEN", "").strip(),
            timeout_seconds=120,
            max_items=_env_int("APIFY_MAX_ITEMS", 25),
        )

    @property
    def is_configured(self) -> bool:
        return bool(self.token)

    @property
    def target_type(self) -> str:
        return "actor" if self.token else "mock"

    @property
    def target_id(self) -> str:
        return "apify~google-search-scraper" if self.token else ""


class ApifyMetaAdsClient:
    """Runs an Apify Actor or Task and returns dataset items.

    Uses Apify's synchronous dataset-items endpoint so the rest of the app only
    needs one response: the ads returned by the run.
    """

    base_url = "https://api.apify.com/v2"

    def __init__(self, settings: ApifySettings | None = None):
        self.settings = settings or ApifySettings.from_env()
        self.last_error = ""

    def search_ads(self, product_url: str, niche: str, days: int, limit: int) -> list[dict]:
        if not self.settings.is_configured:
            self.last_error = "APIFY_TOKEN is not set."
            return []

        return self._load_from_apify(niche)

    def _load_from_apify(self, niche: str) -> list[dict]:
        url = (
            "https://api.apify.com/v2/acts/"
            f"apify~google-search-scraper/run-sync-get-dataset-items?token={self.settings.token}"
        )
        payload = {
            "queries": [niche],
            "maxPagesPerQuery": 1,
            "resultsPerPage": 5,
        }
        req = request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=120) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            print("APIFY ERROR:", e)
            self.last_error = str(e)
        return []

    def status(self) -> dict:
        return {
            "configured": self.settings.is_configured,
            "target_type": self.settings.target_type,
            "target_id": self._masked_target_id(),
            "max_items": self.settings.max_items,
            "timeout_seconds": self.settings.timeout_seconds,
            "last_error": self.last_error,
        }

    def _masked_target_id(self) -> str:
        target_id = self.settings.target_id
        if not target_id:
            return ""
        if len(target_id) <= 8:
            return target_id
        return f"{target_id[:4]}...{target_id[-4:]}"


def fetch_ads_from_apify(product_url: str, niche: str, days: int = 30, limit: int = 5) -> list[dict]:
    return ApifyMetaAdsClient().search_ads(product_url, niche, days, limit)


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default
