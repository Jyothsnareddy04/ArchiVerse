from agents.Cost_Estimator.services.cost_services.boq_calculator import calculate_boq


def split_area(area):
    return {
        "living": area * 0.25,
        "bedroom": area * 0.35,
        "kitchen": area * 0.15,
        "bathroom": area * 0.10,
        "circulation": area * 0.15
    }


# 🔥 CORE FIX → TOTAL BOQ FIRST
def generate_room_boq(area, floors=1, quality="standard"):

    total_area = area * floors

    # ✅ Step 1: Get correct total BOQ
    total_boq = calculate_boq(area, floors, quality)

    # ✅ Step 2: Split area
    area_split = split_area(total_area)

    room_boq = {}

    for room, a in area_split.items():
        ratio = a / total_area

        room_boq[room] = {
            "cement_bags": int(total_boq["cement_bags"] * ratio),
            "steel_ton": round(total_boq["steel_ton"] * ratio, 2),
            "sand_ton": int(total_boq["sand_ton"] * ratio),
            "tiles_sqft": int(a * 1.1)
        }

    return room_boq


# 🔥 INTERIOR COST (UNCHANGED - GOOD)
def interior_costs(area_split):

    return {
        "living": {
            "flooring": int(area_split["living"] * 120),
            "false_ceiling": int(area_split["living"] * 80),
            "painting": int(area_split["living"] * 40)
        },
        "bedroom": {
            "flooring": int(area_split["bedroom"] * 110),
            "wardrobes": int(area_split["bedroom"] * 250),
            "painting": int(area_split["bedroom"] * 35)
        },
        "kitchen": {
            "modular_kitchen": int(area_split["kitchen"] * 700),
            "tiles": int(area_split["kitchen"] * 120),
            "plumbing": int(area_split["kitchen"] * 80)
        },
        "bathroom": {
            "wall_tiles": int(area_split["bathroom"] * 150),
            "fixtures": int(area_split["bathroom"] * 200),
            "waterproofing": int(area_split["bathroom"] * 90)
        }
    }


# 🔥 EXTERIOR COST (UNCHANGED - GOOD)
def exterior_cost(area):
    return {
        "plaster": int(area * 40),
        "paint": int(area * 25),
        "elevation": int(area * 60),
        "compound_wall": int(area * 35)
    }