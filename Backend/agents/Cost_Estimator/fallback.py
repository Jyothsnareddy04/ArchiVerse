from .query_builder import build_query

def fetch_with_fallback(cursor, filters):

    # Try full match
    query, params = build_query(filters)
    cursor.execute(query, params)
    result = cursor.fetchone()

    if result:
        return result

    # Remove floors
    filters.pop("floors", None)

    query, params = build_query(filters)
    cursor.execute(query, params)
    result = cursor.fetchone()

    if result:
        return result

    # Remove house_type
    filters.pop("house_type", None)

    query, params = build_query(filters)
    cursor.execute(query, params)
    result = cursor.fetchone()

    if result:
        return result

    # Final fallback
    minimal = {
        "city": filters["city"],
        "quality": filters["quality"]
    }

    query, params = build_query(minimal)
    cursor.execute(query, params)

    return cursor.fetchone()