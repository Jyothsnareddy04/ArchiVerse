from agents.Cost_Estimator.services.cost_services.room_boq_calculator import (
    generate_room_boq,
    split_area,
    interior_costs,
    exterior_cost
)
from agents.Cost_Estimator.services.cost_services.real_market_fetcher import fetch_real_market_rates
from agents.Cost_Estimator.services.cost_services.llm_optimizer import optimize_cost
from agents.Cost_Estimator.services.cost_services.mep_costs import plumbing_costs, electrical_costs


# 🔹 Quality factor
def get_quality_factor(q):
    return {
        "low": 0.85,
        "standard": 1.0,
        "premium": 1.3
    }.get(q.lower(), 1.0)


# 🔹 Material ratio check
def validate_material_balance(cement, steel, sand):
    total = cement + steel + sand
    if total == 0:
        return {"cement": 0, "steel": 0, "sand": 0}
    return {
        "cement": cement / total,
        "steel": steel / total,
        "sand": sand / total
    }


# 🔹 Adjust BOQ if imbalance
def scale_boq(room_boq_data, factor):
    for room in room_boq_data.values():
        room["sand_ton"] = int(room["sand_ton"] * factor)
    return room_boq_data


def correct_material_balance(cement_cost, steel_cost, sand_cost, room_boq_data):
    ratios = validate_material_balance(cement_cost, steel_cost, sand_cost)

    if ratios["sand"] > 0.30:
        sand_cost *= 0.6
        room_boq_data = scale_boq(room_boq_data, 0.6)

    if ratios["steel"] < 0.30:
        steel_cost *= 1.1

    return int(cement_cost), int(steel_cost), int(sand_cost), room_boq_data


# 🔹 Furniture cost map for interior items
FURNITURE_COST_MAP = {
    "sofa": 45000,
    "beds": 35000,
    "tv-stand": 18000,
    "curtains": 8000,
    "false-ceiling": 65000,
    "lights": 12000,
    "chandeliers": 25000,
    "bookshelves": 22000,
    "lamps": 5000,
    "cupboards": 55000,
    "dressing-table": 18000,
    "mirrors": 8000,
    "dining-table": 35000,
    "kitchen-cupboards": 85000,
    "floor-tiles": 45000,
    "bathroom-tiles": 25000,
    "taps": 6000,
    "washbasin": 12000,
    "shower": 15000,
    "doors": 12000,
    "windows": 10000,
    "office-setup": 35000,
}

# 🔹 Exterior style cost multiplier
EXTERIOR_STYLE_COST = {
    "grey-navy": 1.10,
    "grey-white": 0.95,
    "sage-beige": 1.05,
    "charcoal-blush": 1.15,
    "stone-wood": 1.20,
    "coastal-breeze": 1.05,
    "mediterranean": 1.15,
    "nordic-frost": 1.10,
    "desert-dusk": 1.10,
    "industrial-chic": 1.08,
}


def calculate_furniture_cost(interior_items, quality_factor):
    """Calculate cost based on actual furniture items selected by user."""
    total = 0
    item_breakdown = []

    for item in interior_items:
        category = item.get("category", "")
        base_cost = FURNITURE_COST_MAP.get(category, 15000)  # default 15k
        adjusted = int(base_cost * quality_factor)
        total += adjusted
        item_breakdown.append({
            "room": item.get("room", "Unknown"),
            "category": category,
            "cost": adjusted
        })

    return total, item_breakdown


# 🔥 MAIN FUNCTION
async def estimate_cost(data, db=None):

    city = data["city"]
    quality = data["quality"]
    area = data["built_up_area"]
    floors = data.get("floors", 1)
    budget = data.get("budget")

    # 🔥 Interior preferences
    selections = data.get("interior_preferences", {
        "kitchen": "standard",
        "bathroom": "standard"
    })

    # 🔥 Exterior & Interior items from frontend
    exterior_style = data.get("exterior_style")
    exterior_item_count = data.get("exterior_item_count", 0)
    interior_items = data.get("interior_items", [])
    interior_item_count = data.get("interior_item_count", 0)

    quality_factor = get_quality_factor(quality)

    # 🔹 AREA
    total_area = area * floors
    area_split = split_area(total_area)

    # 🔹 BOQ
    room_boq_data = generate_room_boq(area, floors, quality)

    # 🔹 MARKET
    market = fetch_real_market_rates(city)

    # 🔹 MATERIAL COST
    cement_cost = sum(r["cement_bags"] for r in room_boq_data.values()) * market["cement"]
    steel_cost = sum(r["steel_ton"] for r in room_boq_data.values()) * market["steel"]
    sand_cost = sum(r["sand_ton"] for r in room_boq_data.values()) * market["sand"]

    # 🔹 BALANCE FIX
    cement_cost, steel_cost, sand_cost, room_boq_data = correct_material_balance(
        cement_cost, steel_cost, sand_cost, room_boq_data
    )

    # 🔹 WASTAGE
    WASTAGE = 1.05
    cement_cost *= WASTAGE
    steel_cost *= WASTAGE
    sand_cost *= WASTAGE

    # 🔥 MATERIAL → CONSTRUCTION (CRITICAL)
    material_total = cement_cost + steel_cost + sand_cost
    construction = int(material_total / 0.55)   # materials ≈ 60%

    # 🔹 INTERIORS - Use furniture items count if available
    if interior_items and len(interior_items) > 0:
        # Calculate based on actual user-selected furniture
        furniture_cost, furniture_breakdown = calculate_furniture_cost(
            interior_items, quality_factor
        )
        # Base interior (flooring, painting etc.) + selected furniture
        base_interiors = interior_costs(area_split)
        base_interior_total = int(
            sum(sum(room.values()) for room in base_interiors.values()) * quality_factor * 0.4
        )
        interior_total = base_interior_total + furniture_cost
    else:
        # Fallback: use area-based estimation
        interiors = interior_costs(area_split)
        interior_total = int(
            sum(sum(room.values()) for room in interiors.values()) * quality_factor
        )
        furniture_breakdown = []

    # 🔹 EXTERIOR - Apply style multiplier if selected
    exteriors = exterior_cost(total_area)
    exterior_total = int(sum(exteriors.values()) * quality_factor)

    if exterior_style and exterior_style in EXTERIOR_STYLE_COST:
        exterior_total = int(exterior_total * EXTERIOR_STYLE_COST[exterior_style])

    # 🔹 MEP
    plumbing = plumbing_costs(area_split, selections)
    plumbing_total = sum(plumbing.values())

    electrical = electrical_costs(total_area, quality)
    electrical_total = sum(electrical.values())

    # 🔹 LABOR (for visibility only, already included in construction)
    labor = int(construction * 0.25)

    # 🔥 BASE COST (engineering estimate)
    base_total = (
        construction +
        interior_total +
        exterior_total +
        plumbing_total +
        electrical_total
    )

    # 🔥 COMMERCIAL LAYER
    contractor_margin = int(base_total * 0.12)   # 12%
    contingency = int(base_total * 0.08)         # 8%

    subtotal = base_total + contractor_margin + contingency

    gst = int(subtotal * 0.05)                  # 5% GST

    final_total = subtotal + gst

    # 🔹 RESPONSE COST OBJECT
    cost = {
        "construction_cost": construction,

        "material_breakdown": {
            "cement": int(cement_cost),
            "steel": int(steel_cost),
            "sand": int(sand_cost)
        },

        "material_ratio": validate_material_balance(
            cement_cost, steel_cost, sand_cost
        ),

        "boq": room_boq_data,

        "interior_cost": interior_total,
        "interior_item_count": interior_item_count,
        "furniture_breakdown": furniture_breakdown,

        "exterior_cost": exterior_total,
        "exterior_style": exterior_style,
        "exterior_item_count": exterior_item_count,
        "exterior_breakdown": exteriors,

        "plumbing_cost": plumbing_total,
        "plumbing_breakdown": plumbing,

        "electrical_cost": electrical_total,
        "electrical_breakdown": electrical,

        "labor_cost": labor,

        # 🔥 NEW
        "base_cost": int(base_total),
        "contractor_margin": contractor_margin,
        "contingency": contingency,
        "gst": gst,

        "total_cost": int(final_total)
    }

    response = {
        "status": "within_budget",
        "cost": cost,
        "market_context": market
    }

    # 🔹 Budget check
    if budget and final_total > budget:
        response["status"] = "over_budget"
        response["budget_gap"] = int(final_total - budget)
        response["llm_optimization"] = await optimize_cost(data, cost)

    return response