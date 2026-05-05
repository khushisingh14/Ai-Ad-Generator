import json
from pathlib import Path

from .ad_search import SuccessfulAdSearchAgent
from .gdrive_data import GDriveDataAgent
from .insight_extractor import MarketingInsightAgent
from .script_writer import AdScriptAgent
from .video_creator import VideoCreativeAgent


def run_ad_agent_flow(
    project_dir: Path,
    product_url: str,
    niche: str,
    days: int = 30,
    limit: int = 5,
    force_mock: bool = False,
) -> dict:
    backend_dir = project_dir / "backend"
    data_dir = backend_dir / "data"
    media_dir = backend_dir / "media"

    search_result = SuccessfulAdSearchAgent(data_dir).run(
        product_url=product_url,
        niche=niche,
        days=days,
        limit=limit,
        force_mock=force_mock,
    )
    insights = MarketingInsightAgent().run(search_result["selected_ads"])
    product_data = GDriveDataAgent(data_dir).run()
    script = AdScriptAgent().run(insights, product_data)
    video_plan = VideoCreativeAgent(media_dir).run(script, insights, product_data)

    result = {
        "product_url": product_url,
        "niche": niche,
        "search_days": days,
        "search_limit": limit,
        "ad_source": search_result["source"],
        "apify": search_result["apify"],
        "used_mock_fallback": search_result["used_mock_fallback"],
        "selected_ads": search_result["selected_ads"],
        "pain_points": insights["pain_points"],
        "marketing_angles": insights["marketing_angles"],
        "concepts": insights["concepts"],
        "ad_script": script,
        "video_plan": video_plan,
        "saved_files": {
            "working_ads": search_result["saved_to"],
            "apify_raw_ads": search_result["raw_saved_to"],
            "campaign": str(data_dir / "generated_campaign.json"),
            "remotion_input": video_plan["remotion_input_file"],
            "subtitles": video_plan["subtitles_file"],
        },
        "flow_steps": [
            "Search successful Meta-style ads through Apify",
            f"Select best working ads active in the last {days} days",
            "Extract pain points, marketing angles, and ad concepts",
            "Fetch product data from Google Drive or local fallback JSON",
            "Create a 60-second ad script",
            "Create a Remotion-ready video plan with voice text and subtitles",
        ],
    }

    campaign_file = data_dir / "generated_campaign.json"
    campaign_file.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
