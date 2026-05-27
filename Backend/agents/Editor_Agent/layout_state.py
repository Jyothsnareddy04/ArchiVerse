import copy


class LayoutState:

    def __init__(self, layout_data):

        self.layout_data = layout_data
        self.rooms = layout_data["rooms"]

        self.selected_room = None
        self.history = []

    def save_history(self):

        self.history.append(copy.deepcopy(self.rooms))

    def update_room(self, room_id, updated_room):

        for room in self.rooms:

            if room["id"] == room_id:

                room.update(updated_room)
                break

    def get_room(self, room_id):

        for room in self.rooms:

            if room["id"] == room_id:
                return room

        return None