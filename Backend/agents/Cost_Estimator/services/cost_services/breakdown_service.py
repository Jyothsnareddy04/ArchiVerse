from sqlalchemy import text

async def get_breakdown(db, total_cost, table_name):

    query = f"SELECT category, percentage FROM {table_name}"
    result = await db.execute(text(query))
    rows = result.fetchall()

    breakdown = {}

    for row in rows:
        breakdown[row[0]] = int(total_cost * row[1])

    return breakdown