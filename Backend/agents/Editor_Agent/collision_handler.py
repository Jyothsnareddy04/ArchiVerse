def check_overlap(room1, room2):

    return not (
        room1["x"] + room1["width"] <= room2["x"] or
        room2["x"] + room2["width"] <= room1["x"] or
        room1["y"] + room1["height"] <= room2["y"] or
        room2["y"] + room2["height"] <= room1["y"]
    )


def resolve_collisions(rooms, current_room):

    for room in rooms:

        if room["id"] == current_room["id"]:
            continue

        if check_overlap(room, current_room):

            return False

    return True