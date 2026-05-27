def generate_plans(base_area, config):

    def compute(area, interior_factor=1.0, exterior_factor=1.0):
        construction = area * config["construction_per_sqft"]
        interior = area * config["interior_per_sqft"] * interior_factor
        exterior = construction * config["exterior_percentage"] * exterior_factor

        total = construction + interior + exterior

        return {
            "total_cost": int(total),
            "area": int(area),
            "breakdown": {
                "construction": int(construction),
                "interior": int(interior),
                "exterior": int(exterior)
            }
        }

    return {
        "budget_plan": compute(int(base_area * 0.85), 0.7, 0.7),
        "balanced_plan": compute(int(base_area * 0.9), 0.85, 0.85),
        "premium_plan": compute(base_area, 1.1, 1.1)
    }