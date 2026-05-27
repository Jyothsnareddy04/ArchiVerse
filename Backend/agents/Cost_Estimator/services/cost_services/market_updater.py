from sqlalchemy import text
from agents.Cost_Estimator.services.cost_services.real_market_fetcher import fetch_real_market_rates


async def update_market_rates(db):

    data = fetch_real_market_rates("Hyderabad")

    print("SCRAPED:", data)

    await db.execute(text("""
        INSERT INTO market_rates (
            city, cement_price_per_bag, steel_price_per_ton,
            sand_price_per_unit, labor_daily_min, labor_daily_max
        )
        VALUES (:city, :cement, :steel, :sand, :min, :max)
    """), {
        "city": "Hyderabad",
        "cement": data["cement"],
        "steel": data["steel"],
        "sand": data["sand"],
        "min": data["labor_min"],
        "max": data["labor_max"]
    })