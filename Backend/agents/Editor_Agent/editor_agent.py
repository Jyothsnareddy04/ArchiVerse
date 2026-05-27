from snap_engine import snap_room
from collision_handler import resolve_collisions
from constraint_engine import validate_layout


class EditorAgent:

    def __init__(self, state):

        self.state = state

    def move_room(self, room_id, new_x, new_y):

        room = self.state.get_room(room_id)

        if not room:
            return False, "Room not found"

        self.state.save_history()

        updated_room = room.copy()

        updated_room["x"] = new_x
        updated_room["y"] = new_y

        updated_room = snap_room(updated_room)

        valid = validate_layout(
            updated_room,
            self.state.layout_data["plot"]
        )

        if not valid:
            return False, "Boundary or size validation failed"

        collision_free = resolve_collisions(
            self.state.rooms,
            updated_room
        )

        if not collision_free:
            return False, "Room overlap detected"

        self.state.update_room(room_id, updated_room)

        return True, updated_room

    def resize_room(self, room_id, width, height):

        room = self.state.get_room(room_id)

        if not room:
            return False, "Room not found"

        self.state.save_history()

        updated_room = room.copy()

        updated_room["width"] = width
        updated_room["height"] = height

        updated_room = snap_room(updated_room)

        valid = validate_layout(
            updated_room,
            self.state.layout_data["plot"]
        )

        if not valid:
            return False, "Invalid resize"

        collision_free = resolve_collisions(
            self.state.rooms,
            updated_room
        )

        if not collision_free:
            return False, "Collision after resize"

        self.state.update_room(room_id, updated_room)

        return True, updated_room