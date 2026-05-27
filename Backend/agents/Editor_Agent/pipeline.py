import json

from layout_state import LayoutState
from editor_agent import EditorAgent


with open("input/editable_layout.json", "r") as f:

    layout_data = json.load(f)


state = LayoutState(layout_data)

agent = EditorAgent(state)


success, result = agent.move_room(
    room_id="bedroom_1",
    new_x=12,
    new_y=20
)

print(success)
print(result)


success, result = agent.resize_room(
    room_id="kitchen_1",
    width=14,
    height=10
)

print(success)
print(result)


with open("output/updated_layout.json", "w") as f:

    json.dump(layout_data, f, indent=4)

print("Updated layout saved")