import json
import os
from pathlib import Path
from urllib import request
from urllib.error import URLError


class VideoCreativeAgent:
    """Creates a Remotion-ready video plan with voice and subtitle assets."""

    def __init__(self, media_dir: Path):
        self.media_dir = media_dir
        self.media_dir.mkdir(parents=True, exist_ok=True)

    def run(self, script: str, insights: dict, product_data: dict) -> dict:
        scenes = self._build_scenes(script, insights, product_data)
        subtitles = self._build_subtitles(scenes)
        visual_prompt = self._build_visual_prompt(insights, product_data)

        subtitle_file = self.media_dir / "subtitles.srt"
        remotion_input_file = self.media_dir / "remotion_input.json"

        voice_asset = self._create_voice_asset(script)
        subtitle_file.write_text(subtitles, encoding="utf-8")

        video_plan = {
            "duration_seconds": 60,
            "format": "vertical 9:16",
            "image_provider": "pollinations.ai fallback URL",
            "image_prompt": visual_prompt,
            "image_url": self._pollinations_url(visual_prompt),
            "voice_provider": voice_asset["provider"],
            "voice_file": voice_asset["file"],
            "subtitles_file": str(subtitle_file),
            "remotion_input_file": str(remotion_input_file),
            "scenes": scenes,
            "remotion_command": "npm run render:ad",
        }

        remotion_input_file.write_text(json.dumps(video_plan, indent=2), encoding="utf-8")
        return video_plan

    def _build_scenes(self, script: str, insights: dict, product_data: dict) -> list[dict]:
        product_name = product_data.get("product_name", "Crowd Wisdom Trading")
        pain = (insights.get("pain_points") or ["Guessing market direction"])[0]
        angle = (insights.get("marketing_angles") or ["Clear trading guidance"])[0]

        return [
            {
                "start": 0,
                "end": 7,
                "title": "Hook",
                "visual": "Trader looking at noisy charts and breaking news",
                "caption": "Still trading from hype and guesswork?",
            },
            {
                "start": 7,
                "end": 20,
                "title": "Pain",
                "visual": "Missed entry and late signal shown on a clean chart",
                "caption": pain,
            },
            {
                "start": 20,
                "end": 42,
                "title": "Solution",
                "visual": f"{product_name} dashboard with research, signals, and sentiment",
                "caption": angle,
            },
            {
                "start": 42,
                "end": 52,
                "title": "Proof",
                "visual": "Simple checklist turning market data into a trading plan",
                "caption": "Research before reaction.",
            },
            {
                "start": 52,
                "end": 60,
                "title": "CTA",
                "visual": "Website URL and clear call to action",
                "caption": "Visit crowdwisdomtrading.com",
            },
        ]

    def _build_subtitles(self, scenes: list[dict]) -> str:
        entries = []
        for index, scene in enumerate(scenes, start=1):
            entries.append(
                "\n".join(
                    [
                        str(index),
                        f"00:00:{scene['start']:02d},000 --> 00:00:{scene['end']:02d},000",
                        scene["caption"],
                    ]
                )
            )
        return "\n\n".join(entries)

    def _build_visual_prompt(self, insights: dict, product_data: dict) -> str:
        product_name = product_data.get("product_name", "Crowd Wisdom Trading")
        concepts = ", ".join(insights.get("concepts", [])[:2])
        return (
            f"vertical social video ad frame for {product_name}, clean trading dashboard, "
            f"market research, confident retail trader, modern fintech style, {concepts}"
        )

    def _pollinations_url(self, prompt: str) -> str:
        encoded = prompt.replace(" ", "%20").replace(",", "%2C")
        seed = os.getenv("IMAGE_SEED", "crowdwisdom")
        return f"https://image.pollinations.ai/prompt/{encoded}?seed={seed}&width=1080&height=1920"

    def _create_voice_asset(self, script: str) -> dict:
        api_key = os.getenv("ELEVENLABS_API_KEY")
        voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

        if api_key:
            audio_file = self.media_dir / "voiceover.mp3"
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            payload = json.dumps(
                {
                    "text": script,
                    "model_id": os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2"),
                    "voice_settings": {
                        "stability": 0.45,
                        "similarity_boost": 0.75,
                    },
                }
            ).encode("utf-8")
            req = request.Request(
                url,
                data=payload,
                headers={
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                    "xi-api-key": api_key,
                },
                method="POST",
            )

            try:
                with request.urlopen(req, timeout=45) as response:
                    audio_file.write_bytes(response.read())
                return {"provider": "ElevenLabs", "file": str(audio_file)}
            except (OSError, URLError):
                pass

        text_file = self.media_dir / "voiceover.txt"
        text_file.write_text(script, encoding="utf-8")
        return {"provider": "Text fallback; set ELEVENLABS_API_KEY for MP3 voiceover", "file": str(text_file)}
