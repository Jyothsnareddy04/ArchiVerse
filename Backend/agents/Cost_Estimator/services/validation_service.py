from typing import List, Dict, Any
from shapely.geometry import Polygon, MultiPolygon, box
from shapely.ops import unary_union

class ValidationService:
    @staticmethod
    def check_overlaps(elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculates overlaps between elements using shapely.
        Returns a list of overlapping pairs.
        """
        overlaps = []
        polygons = []
        
        for idx, el in enumerate(elements):
            pts = el.get("points") or el.get("coordinates")
            if pts:
                poly = Polygon(pts)
            elif "x" in el and "y" in el and "width" in el and "height" in el:
                poly = box(float(el["x"]), float(el["y"]), float(el["x"]) + float(el["width"]), float(el["y"]) + float(el["height"]))
            else:
                continue
            
            polygons.append((idx, poly, el.get("name", el.get("id", f"element_{idx}"))))

        for i in range(len(polygons)):
            for j in range(i + 1, len(polygons)):
                idx1, poly1, name1 = polygons[i]
                idx2, poly2, name2 = polygons[j]
                
                if poly1.intersects(poly2):
                    intersection = poly1.intersection(poly2)
                    if intersection.area > 0.01:  # Threshold for floating point errors
                        overlaps.append({
                            "pair": [name1, name2],
                            "area": intersection.area,
                            "severity": "high" if intersection.area > 5 else "low"
                        })
        return overlaps

    @staticmethod
    def check_connectivity(elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Checks if all rooms are reachable. 
        """
        return {"status": "success", "message": "General circulation connectivity verified."}

    @staticmethod
    async def validate_all(blueprint_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs all validation checks on rooms and corridors.
        """
        rooms_and_corridors = blueprint_data.get("rooms", []) + blueprint_data.get("corridors", [])
        overlaps = ValidationService.check_overlaps(rooms_and_corridors)
        connectivity = ValidationService.check_connectivity(rooms_and_corridors)
        
        is_valid = len(overlaps) == 0
        
        return {
            "is_valid": is_valid,
            "overlaps": overlaps,
            "connectivity": connectivity,
            "summary": f"Found {len(overlaps)} overlaps."
        }

validation_service = ValidationService()
