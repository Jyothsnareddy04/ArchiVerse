GRID_SIZE = 1


def snap(value):

    return round(value / GRID_SIZE) * GRID_SIZE


def snap_room(room):

    room["x"] = snap(room["x"])
    room["y"] = snap(room["y"])

    room["width"] = max(4, snap(room["width"]))
    room["height"] = max(4, snap(room["height"]))

    return room