from schemas.layout_schema import GenericResponse
from agents.Interior_Agent.interior_agent import interior_agent
from fastapi import Request
import traceback

class InteriorController:
    @staticmethod
    async def generate_interior(request_data: dict) -> GenericResponse:
        try:
            blueprint = request_data.get("blueprint", {})
            prefs = request_data.get("preferences", {})
            
            result = await interior_agent.plan_interior(blueprint, prefs)
            
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

interior_controller = InteriorController()
