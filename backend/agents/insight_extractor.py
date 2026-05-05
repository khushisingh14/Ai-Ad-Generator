from collections import Counter


class MarketingInsightAgent:
    """Extracts pain points, marketing angles, and concepts from winning ads."""

    pain_keywords = {
        "miss": "Fear of missing profitable moves",
        "late": "Acting too late on trading signals",
        "confus": "Confusion from noisy market information",
        "risk": "Fear of losing money without a plan",
        "guess": "Guessing instead of following a tested process",
        "time": "Not having time to analyze markets manually",
        "overwhelm": "Feeling overwhelmed by charts and news",
    }

    angle_keywords = {
        "signal": "Clear trade signals",
        "daily": "Daily market guidance",
        "expert": "Expert-backed trading research",
        "simple": "Simpler trading decisions",
        "community": "Wisdom from a trading community",
        "confidence": "More confident decision-making",
        "alerts": "Timely alerts before opportunities move",
    }

    def run(self, ads: list[dict]) -> dict:
        text_blocks = [self._combined_text(ad) for ad in ads]
        pain_points = self._extract_from_keywords(text_blocks, self.pain_keywords)
        marketing_angles = self._extract_from_keywords(text_blocks, self.angle_keywords)
        concepts = self._extract_concepts(ads, marketing_angles)

        return {
            "pain_points": pain_points[:5],
            "marketing_angles": marketing_angles[:5],
            "concepts": concepts[:4],
        }

    def _combined_text(self, ad: dict) -> str:
        return " ".join(
            [
                str(ad.get("hook", "")),
                str(ad.get("ad_text", "")),
                str(ad.get("cta", "")),
            ]
        ).lower()

    def _extract_from_keywords(self, text_blocks: list[str], keyword_map: dict[str, str]) -> list[str]:
        matches = []
        for text in text_blocks:
            for keyword, insight in keyword_map.items():
                if keyword in text:
                    matches.append(insight)

        if not matches:
            return ["Audience wants a clearer, faster path to better trading decisions"]

        counts = Counter(matches)
        return [item for item, _count in counts.most_common()]

    def _extract_concepts(self, ads: list[dict], marketing_angles: list[str]) -> list[str]:
        concepts = []
        for ad in ads:
            hook = ad.get("hook") or ad.get("ad_text", "")[:80]
            concepts.append(f"Open with: {hook}")

        concepts.extend(f"Frame around: {angle}" for angle in marketing_angles)
        return list(dict.fromkeys(concepts))
