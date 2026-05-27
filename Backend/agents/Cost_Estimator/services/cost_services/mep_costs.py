def plumbing_costs(area_split, selections):
    """
    selections example:
    {
        "kitchen": "standard",
        "bathroom": "premium"
    }
    """

    kitchen_factor = {
        "basic": 80,
        "standard": 120,
        "premium": 200
    }

    bathroom_factor = {
        "basic": 120,
        "standard": 180,
        "premium": 300
    }

    return {
        "kitchen_plumbing": int(area_split["kitchen"] * kitchen_factor.get(selections.get("kitchen", "standard"), 120)),
        "bathroom_plumbing": int(area_split["bathroom"] * bathroom_factor.get(selections.get("bathroom", "standard"), 180))
    }


def electrical_costs(total_area, quality="standard"):

    factor = {
        "low": 60,
        "standard": 110,
        "premium": 140
    }.get(quality, 120)

    return {
        "wiring": int(total_area * factor * 0.45),
        "switches": int(total_area * factor * 0.25),
        "fixtures": int(total_area * factor * 0.30)
    }