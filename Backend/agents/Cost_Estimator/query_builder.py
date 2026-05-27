def get_area_range(area):
    if area < 1200:
        return "small"
    elif area < 2500:
        return "medium"
    return "large"


def build_query(filters: dict):
    query = "SELECT * FROM cost_config WHERE 1=1"
    params = []

    if filters.get("city"):
        query += " AND city = %s"
        params.append(filters["city"])

    if filters.get("quality"):
        query += " AND quality = %s"
        params.append(filters["quality"])

    if filters.get("house_type"):
        query += " AND house_type = %s"
        params.append(filters["house_type"])

    if filters.get("floors"):
        query += " AND floors = %s"
        params.append(filters["floors"])

    if filters.get("area_range"):
        query += " AND area_range = %s"
        params.append(filters["area_range"])

    return query, params