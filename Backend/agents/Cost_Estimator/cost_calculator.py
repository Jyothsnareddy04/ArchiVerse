INTERIOR_COST_MAP = {
    "modular_kitchen": 200000,
    "premium_dining": 80000,
    "wardrobe": 150000
}

EXTERIOR_STYLE_MULTIPLIER = {
    "urban_sophisticate": 1.1,
    "minimalist": 0.9,
    "organic": 1.05,
    "bold": 1.15
}


def calculate_cost(area, config, data):
    construction = area * config["construction_per_sqft"]

    # 🔥 Apply city multiplier
    construction *= config.get("city_multiplier", 1)

    material_cost = construction * config["material_percentage"]
    labor_cost = construction * config["labor_percentage"]

    interior = area * config["interior_per_sqft"]

    # 🔥 Add UI-based interior cost
    extra_interior = sum(
        INTERIOR_COST_MAP.get(item, 0)
        for item in data.get("interior_choices", [])
    )
    interior += extra_interior

    exterior = construction * config["exterior_percentage"]

    # 🔥 Apply exterior style multiplier
    exterior *= EXTERIOR_STYLE_MULTIPLIER.get(
        data.get("exterior_style"), 1
    )

    total = construction + interior + exterior

    return {
        "total": total,
        "construction": construction,
        "interior": interior,
        "exterior": exterior,
        "material_cost": material_cost,
        "labor_cost": labor_cost
    }


def apply_budget_constraints(cost_data, budget, area):
    adjustments = []

    if cost_data["total"] > budget:
        cost_data["interior"] *= 0.8
        adjustments.append("Reduced interior cost")

    if cost_data["total"] > budget:
        cost_data["exterior"] *= 0.85
        adjustments.append("Reduced exterior cost")

    if cost_data["total"] > budget:
        area *= 0.9
        adjustments.append("Reduced built-up area")

    total = cost_data["construction"] + cost_data["interior"] + cost_data["exterior"]
    cost_data["total"] = total

    return cost_data, adjustments, area