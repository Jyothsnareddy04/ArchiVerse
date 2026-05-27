from schemas.layout_schema import GenericResponse
from agents.Exterior_Agent.exterior_agent import exterior_agent
import traceback

class ExteriorController:
    @staticmethod
    async def generate_exterior(request_data: dict) -> GenericResponse:
        try:
            blueprint = request_data.get("blueprint", {})
            prefs = request_data.get("preferences", {})
            
            result = await exterior_agent.design_exterior(blueprint, prefs)
            
            return GenericResponse(
                success=True,
                data=result
            )
        except Exception as e:
            traceback.print_exc()
            return GenericResponse(
                success=False,
                error=str(e)
            )

exterior_controller = ExteriorController()
