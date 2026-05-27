from schemas.layout_schema import BlueprintRequest, BlueprintResponse
from agents.Blueprint_Agent.blueprint_agent import blueprint_agent
from agents.Cost_Estimator.services.autofix_service import autofix_service
from agents.Cost_Estimator.services.validation_service import validation_service
import traceback

# Safe import - visualizer may not exist
try:
    from agents.Layout_Agent.rendering.visualizer import render_base64
except ImportError:
    def render_base64(*args, **kwargs):
        return None


class BlueprintController:
    @staticmethod
    async def generate_blueprint(request: BlueprintRequest) -> BlueprintResponse:
        try:
            # Get the ORIGINAL layout data (with rects, doors from layout generator)
            original_layout = request.layout_data

            # Generate technical blueprint (walls, corridors, windows)
            blueprint = await blueprint_agent.generate_blueprint(request.layout_data, request.requirements)
            
            # Validation & auto-fix
            fixed_blueprint = await autofix_service.fix_blueprint(blueprint)
            val_result = await validation_service.validate_all(fixed_blueprint)
            
            # ═══ RENDER HIGH-QUALITY IMAGE ═══
            # Use the ORIGINAL layout rooms (which have proper rects geometry)
            # merged with the blueprint engine's doors data
            try:
                # Get plot dimensions from original layout or request
                pw = (original_layout.get("plot_width") 
                      or original_layout.get("plotWidth")
                      or original_layout.get("area", 2000) ** 0.5)
                ph = (original_layout.get("plot_depth")
                      or original_layout.get("plotDepth") 
                      or original_layout.get("area", 2000) ** 0.5)
                
                # Try to get from fixed blueprint meta
                if fixed_blueprint.get("meta", {}).get("plot_boundary"):
                    pb = fixed_blueprint["meta"]["plot_boundary"]
                    pw, ph = pb[2], pb[3]
                
                plot_info = {"plot_w": float(pw), "plot_h": float(ph)}
                
                # Build the render layout: original rooms + blueprint doors
                render_layout = {
                    "rooms": original_layout.get("rooms", []),
                    "doors": fixed_blueprint.get("doors", []),
                }
                
                title = original_layout.get("name", "Architectural Blueprint")
                image = render_base64(render_layout, plot_info, title=title)
                fixed_blueprint["image"] = image
                print(f"[BLUEPRINT] Image rendered successfully ({len(image)} chars)")
            except Exception as e:
                print(f"[BLUEPRINT] Image generation failed: {e}")
                traceback.print_exc()
                fixed_blueprint["image"] = None

            return BlueprintResponse(
                success=True,
                data=fixed_blueprint,
                error=None if val_result["is_valid"] else "Validation warnings persist."
            )
        except Exception as e:
            traceback.print_exc()
            return BlueprintResponse(
                success=False,
                error=str(e)
            )

blueprint_controller = BlueprintController()
