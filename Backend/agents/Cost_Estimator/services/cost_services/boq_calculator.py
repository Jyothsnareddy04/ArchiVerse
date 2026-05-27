def calculate_boq(area, floors=1, quality="standard"):

    total_area = area * floors

    quality_factor = {
        "low": 0.9,
        "standard": 1.0,
        "premium": 1.15
    }.get(quality.lower(), 1.0)

    # 🔥 CALIBRATED VALUES
    cement_bags_per_sqft = 0.45 * quality_factor
    steel_kg_per_sqft = 4.0 * quality_factor
    sand_ton_per_sqft = 0.07 * quality_factor
    bricks_per_sqft = 8

    cement_bags = int(total_area * cement_bags_per_sqft)
    steel_ton = round((total_area * steel_kg_per_sqft) / 1000, 2)
    sand_ton = int(total_area * sand_ton_per_sqft)
    bricks = int(total_area * bricks_per_sqft)

    # 🔥 WASTAGE
    WASTAGE = 1.05
    cement_bags = int(cement_bags * WASTAGE)
    steel_ton = round(steel_ton * WASTAGE, 2)
    sand_ton = int(sand_ton * WASTAGE)
    bricks = int(bricks * WASTAGE)

    return {
        "cement_bags": cement_bags,
        "steel_ton": steel_ton,
        "sand_ton": sand_ton,
        "bricks": bricks
    }