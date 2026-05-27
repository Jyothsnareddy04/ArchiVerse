from agents.Cost_Estimator.services.llm_service import llm_service
from typing import Dict, Any

class InteriorAgent:
    @staticmethod
    async def plan_interior(blueprint_data: Dict[str, Any], style_prefs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates interior planning and furniture layout.
        """
        system_prompt = """
        You are a Senior Interior Planner.
        Design a functional furniture layout and interior design specification based on the provided blueprint.
        Return ONLY valid JSON with room-wise furniture placements and material suggestions.
        """
        
        user_prompt = f"""
        Blueprint: {blueprint_data}
        Style Preferences: {style_prefs}
        Plan the interior layout.
        """
        
        result = await llm_service.generate_json(system_prompt, user_prompt)
        return result

interior_agent = InteriorAgent()
