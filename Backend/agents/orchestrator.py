class ArchiVerseOrchestrator:

    def __init__(self, layout_agent, cost_agent):
        self.layout_agent = layout_agent
        self.cost_agent = cost_agent

    async def run_pipeline(self, user_input, db):

        # 🔹 Layout (function-style agent)
        layout = await self.layout_agent(user_input)

        enriched_input = {
            **user_input,
            "layout": layout,
            "interior_choices": user_input.get("interior_choices", []),
            "exterior_style": user_input.get("exterior_style")
        }

        # 🔹 Cost
        cost = await self.cost_agent.estimate_cost(enriched_input, db)

        return {
            "layout": layout,
            "cost": cost
        }