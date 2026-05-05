class AdScriptAgent:
    """Creates a 60-second ad script from insights plus product-specific data."""

    def run(self, insights: dict, product_data: dict) -> str:
        pain_points = insights.get("pain_points", [])
        angles = insights.get("marketing_angles", [])
        product_name = product_data.get("product_name", "Crowd Wisdom Trading")
        offer = product_data.get("offer", "trading research and market guidance")
        proof = product_data.get("proof_point", "built around clear daily insights")
        differentiator = product_data.get("unique_mechanism", "a blend of market research and crowd sentiment")
        cta = product_data.get("cta", "Visit crowdwisdomtrading.com today")

        pain = pain_points[0] if pain_points else "guessing what the market will do next"
        angle = angles[0] if angles else "clear trading guidance"
        second_angle = angles[1] if len(angles) > 1 else "simpler decisions"

        return (
            "HOOK (0-7s): Still making trading decisions from headlines, hype, and guesswork?\n\n"
            f"PROBLEM (7-20s): If you are dealing with {pain.lower()}, it is easy to enter too late, "
            "second-guess strong setups, or miss opportunities completely.\n\n"
            f"SOLUTION (20-42s): {product_name} gives you {offer}. The angle is simple: "
            f"use {differentiator} to create {angle.lower()} and {second_angle.lower()}.\n\n"
            f"PROOF (42-52s): {proof}. Instead of jumping between random opinions, you get a clearer base "
            "for your next move.\n\n"
            f"CTA (52-60s): {cta}. See the latest research before your next trade."
        )
