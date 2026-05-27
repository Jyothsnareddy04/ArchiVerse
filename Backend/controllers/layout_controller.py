from schemas.layout_schema import LayoutRequest, LayoutResponse
import traceback
import sys
import os

# Add Layout_Agent to path so its internal imports work
LAYOUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agents", "Layout_Agent")
if LAYOUT_DIR not in sys.path:
    sys.path.insert(0, LAYOUT_DIR)

try:
    from agents.Layout_Agent.pipeline import run_pipeline
except ImportError:
    run_pipeline = None


class LayoutController:
    @staticmethod
    async def generate_layout(request: LayoutRequest) -> LayoutResponse:
        """
        Validates request and calls Layout Agent pipeline.
        """
        try:
            if run_pipeline is None:
                return LayoutResponse(
                    success=False,
                    error="Layout pipeline not available"
                )

            # Map schema request to agent input format
            user_input = {
                "plot_width": request.plot_width,
                "plot_height": request.plot_depth,
                "plot": [request.plot_width, request.plot_depth],
                "house_type": request.preferences.get("house_type", "individual"),
                "bedrooms": request.preferences.get("bedrooms", 3),
                "facing": request.preferences.get("facing", "north"),
                "unit": "feet",
                "parking": True,
                "lawn": True,
                "plants": request.preferences.get("plant_sides", False),
                "optional_rooms": [],
                **{k: v for k, v in request.preferences.items() if k not in ("bedrooms", "facing", "house_type", "plant_sides")}
            }

            # Build optional_rooms list from preferences
            if request.preferences.get("has_store"):
                user_input["optional_rooms"].append("store")
            if request.preferences.get("has_backyard"):
                user_input["optional_rooms"].append("backyard")
            if request.preferences.get("has_dining"):
                user_input["optional_rooms"].append("dining")

            # Call pipeline
            variants = run_pipeline(user_input, render=False)

            # Transform variants to JSON-friendly format
            layouts = {}
            for idx, state in enumerate(variants):
                rooms = []
                for s in state.spaces:
                    rooms.append({
                        "id": f"room-{idx}-{s.name}",
                        "name": s.name,
                        "x": getattr(s, "x", 0),
                        "y": getattr(s, "y", 0),
                        "w": getattr(s, "width", 10),
                        "h": getattr(s, "height", 10),
                        "area": getattr(s, "area", 0),
                        "rects": getattr(s, "rects", []),
                    })
                
                layouts[f"variant_{idx + 1}"] = {
                    "id": f"layout-{idx + 1}",
                    "name": f"Variant {idx + 1}",
                    "area": request.plot_width * request.plot_depth,
                    "rooms": rooms,
                    "plot_width": request.plot_width,
                    "plot_depth": request.plot_depth,
                }

            return LayoutResponse(
                success=True,
                data={"layouts": layouts}
            )
        except Exception as e:
            traceback.print_exc()
            return LayoutResponse(
                success=False,
                error=str(e)
            )

layout_controller = LayoutController()
