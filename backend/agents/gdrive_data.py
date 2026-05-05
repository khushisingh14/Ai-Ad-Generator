import json
import os
from pathlib import Path
from urllib import request
from urllib.error import URLError


class GDriveDataAgent:
    """Fetches unique product data from Google Drive when configured, otherwise local JSON."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.local_file = data_dir / "unique_product_data.json"

    def run(self) -> dict:
        data = self._fetch_public_drive_json() or self._load_local_data()
        return data

    def _fetch_public_drive_json(self) -> dict:
        direct_url = os.getenv("GDRIVE_DATA_URL")
        file_id = os.getenv("GOOGLE_DRIVE_FILE_ID")
        url = direct_url
        if not url and file_id:
            url = f"https://drive.google.com/uc?export=download&id={file_id}"

        if not url:
            return {}

        try:
            with request.urlopen(url, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except (OSError, URLError, json.JSONDecodeError):
            return {}

    def _load_local_data(self) -> dict:
        with self.local_file.open("r", encoding="utf-8") as file:
            return json.load(file)
