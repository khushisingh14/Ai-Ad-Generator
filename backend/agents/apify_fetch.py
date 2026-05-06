import json
import os
from dataclasses import dataclass
from pathlib import Path
from urllib import parse, request
from urllib.error import HTTPError, URLError


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
    actor_id: str
    task_id: str
    timeout_seconds: int
    max_items: int

    @classmethod
    def from_env(cls) -> "ApifySettings":
        load_local_env()
        return cls(
            token=os.getenv("APIFY_TOKEN", "").strip(),
            actor_id=os.getenv("APIFY_META_ADS_ACTOR_ID", "").strip(),
            task_id=os.getenv("APIFY_META_ADS_TASK_ID", "").strip(),
            timeout_seconds=_env_int("APIFY_TIMEOUT_SECONDS", 120),
            max_items=_env_int("APIFY_MAX_ITEMS", 25),
        )

    @property
    def is_configured(self) -> bool:
        return bool(self.token and (self.actor_id or self.task_id))

    @property
    def target_type(self) -> str:
        if self.task_id:
            return "task"
        if self.actor_id:
            return "actor"
        return "mock"

    @property
    def target_id(self) -> str:
        return self.task_id or self.actor_id


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
            self.last_error = "APIFY_TOKEN and APIFY_META_ADS_ACTOR_ID or APIFY_META_ADS_TASK_ID are not set."
            return []

        endpoint = self._endpoint(limit)
        payload = self._build_input(product_url, niche, days, limit)
        req = self._request(endpoint, payload)

        try:
            with request.urlopen(req, timeout=self.settings.timeout_seconds + 15) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            self.last_error = f"Apify HTTP {exc.code}: {exc.reason}"
        except (OSError, URLError) as exc:
            self.last_error = f"Apify request failed: {exc}"
        except json.JSONDecodeError:
            self.last_error = "Apify returned invalid JSON."

        return []

    def _request(self, endpoint: str, payload: dict) -> request.Request:
        headers = {"Authorization": f"Bearer {self.settings.token}"}
        if self.settings.task_id:
            return request.Request(endpoint, headers=headers, method="GET")

        headers["Content-Type"] = "application/json"
        return request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

    def status(self) -> dict:
        return {
            "configured": self.settings.is_configured,
            "target_type": self.settings.target_type,
            "target_id": self._masked_target_id(),
            "max_items": self.settings.max_items,
            "timeout_seconds": self.settings.timeout_seconds,
            "last_error": self.last_error,
        }

    def _endpoint(self, limit: int) -> str:
        target_id = parse.quote(self.settings.target_id, safe="~")
        params = parse.urlencode(
            {
                "format": "json",
                "clean": "true",
                "limit": min(limit, self.settings.max_items),
                "timeout": self.settings.timeout_seconds,
                "maxItems": min(limit, self.settings.max_items),
            }
        )

        if self.settings.task_id:
            return f"{self.base_url}/actor-tasks/{target_id}/run-sync-get-dataset-items?{params}"

        return f"{self.base_url}/acts/{target_id}/run-sync-get-dataset-items?{params}"

    def _build_input(self, product_url: str, niche: str, days: int, limit: int) -> dict:
        return {
            "queries": [niche],
            "maxPagesPerQuery": 1,
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
