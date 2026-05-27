from schemas.layout_schema import GenericResponse
from agents.Cost_Estimator.cost_agent import cost_agent
import traceback


class CostController:

    @staticmethod
    async def estimate_cost(request_data: dict, db):
        try:
            result = await cost_agent.estimate_cost(request_data, db)

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


cost_controller = CostController()