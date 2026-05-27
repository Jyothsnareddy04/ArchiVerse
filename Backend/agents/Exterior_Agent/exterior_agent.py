from agents.Cost_Estimator.services.llm_service import llm_service
from typing import Dict, Any

class ExteriorAgent:
    @staticmethod
    async def design_exterior(blueprint_data: Dict[str, Any], facade_prefs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Designs the building facade and exterior landscape.
        """
        system_prompt = """
        You are a World-Class Exterior Architect.
        Design the facade, roof style, and landscape for the building based on the blueprint.
        Return ONLY valid JSON with material choices, window styles, and color palettes.
        """
        
        user_prompt = f"""
        Blueprint: {blueprint_data}
        Facade Preferences: {facade_prefs}
        Design the exterior.
        """
        
        result = await llm_service.generate_json(system_prompt, user_prompt)
        return result

exterior_agent = ExteriorAgent()
