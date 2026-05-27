from typing import Dict, Any, List
import math
import datetime

class AutofixService:
    @staticmethod
    def snap_to_grid(value: float, grid_size: float = 0.5) -> float:
        """Snaps a numeric value to the nearest grid step."""
        return round(value / grid_size) * grid_size

    @staticmethod
    def resolve_room_overlaps(rooms: List[Dict[str, Any]]):
        """Resolves overlaps by pushing the neighboring room."""
        for i in range(len(rooms)):
            r1 = rooms[i]
            for j in range(i + 1, len(rooms)):
                r2 = rooms[j]
                
                # Bounding box overlapping logic
                overlap_x = min(r1["x"] + r1["width"], r2["x"] + r2["width"]) - max(r1["x"], r2["x"])
                overlap_y = min(r1["y"] + r1["height"], r2["y"] + r2["height"]) - max(r1["y"], r2["y"])
                
                if overlap_x > 0 and overlap_y > 0:
                    # Resolve overlap by pushing r2 along the axis of least overlap
                    if overlap_x < overlap_y:
                        if r1["x"] < r2["x"]:
                            r2["x"] += overlap_x
                        else:
                            r2["x"] -= overlap_x
                    else:
                        if r1["y"] < r2["y"]:
                            r2["y"] += overlap_y
                        else:
                            r2["y"] -= overlap_y

    @staticmethod
    async def fix_blueprint(blueprint_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applies fixes to the CAD-grade blueprint:
        1. Snaps all coordinates to grid.
        2. Fixes overlaps by pushing.
        """
        fixed_data = blueprint_data.copy()
        
        # 1. Snap & Gather Rooms / Corridors
        for category in ["rooms", "corridors"]:
            items = fixed_data.get(category, [])
            for item in items:
                item["x"] = AutofixService.snap_to_grid(float(item.get("x", 0)))
                item["y"] = AutofixService.snap_to_grid(float(item.get("y", 0)))
                item["width"] = AutofixService.snap_to_grid(float(item.get("width", 0)))
                item["height"] = AutofixService.snap_to_grid(float(item.get("height", 0)))

        # 2. Resolve Overlaps (Push neighbors)
        rooms_and_corridors = fixed_data.get("rooms", []) + fixed_data.get("corridors", [])
        AutofixService.resolve_room_overlaps(rooms_and_corridors)
        
        # Snap again in case pushing mis-aligned
        for item in rooms_and_corridors:
            item["x"] = AutofixService.snap_to_grid(item["x"])
            item["y"] = AutofixService.snap_to_grid(item["y"])

        # 3. Snap walls, doors, windows
        for category in ["walls", "doors", "windows"]:
            items = fixed_data.get(category, [])
            for item in items:
                if "x" in item: item["x"] = AutofixService.snap_to_grid(float(item["x"]))
                if "y" in item: item["y"] = AutofixService.snap_to_grid(float(item["y"]))
                
                # Walls might use start_x/y and end_x/y
                if "start_x" in item: item["start_x"] = AutofixService.snap_to_grid(float(item["start_x"]))
                if "start_y" in item: item["start_y"] = AutofixService.snap_to_grid(float(item["start_y"]))
                if "end_x" in item: item["end_x"] = AutofixService.snap_to_grid(float(item["end_x"]))
                if "end_y" in item: item["end_y"] = AutofixService.snap_to_grid(float(item["end_y"]))

        fixed_data["meta"] = fixed_data.get("meta", {})
        fixed_data["meta"]["valid"] = True
        fixed_data["meta"]["fixed_at"] = datetime.datetime.now().isoformat()
        
        return fixed_data

autofix_service = AutofixService()
