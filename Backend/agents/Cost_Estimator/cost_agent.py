from agents.Cost_Estimator.services.cost_services.cost_service import estimate_cost


class CostAgent:

    async def estimate_cost(self, data, db):
        return await estimate_cost(data, db)


cost_agent = CostAgent()