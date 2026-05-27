MIN_ROOM_SIZE = 4


def validate_boundaries(room, plot):

    if room["x"] < 0 or room["y"] < 0:
        return False

    if room["x"] + room["width"] > plot["width"]:
        return False

    if room["y"] + room["height"] > plot["height"]:
        return False

    return True


def validate_room_size(room):

    if room["width"] < MIN_ROOM_SIZE:
        return False

    if room["height"] < MIN_ROOM_SIZE:
        return False

    return True


def validate_layout(room, plot):

    if not validate_boundaries(room, plot):
        return False

    if not validate_room_size(room):
        return False

    return True