from schemas.blueprint_schema import ValidationRequest, ValidationFixResponse
from agents.Cost_Estimator.services.validation_service import validation_service
from agents.Cost_Estimator.services.autofix_service import autofix_service
import traceback

class ValidationController:
    @staticmethod
    async def validate_and_fix(request: ValidationRequest) -> ValidationFixResponse:
        try:
            blueprint = request.blueprint_json
            
            # 1. Validate
            val_result = await validation_service.validate_all(blueprint)
            
            # 2. Fix
            fixed_blueprint = await autofix_service.fix_blueprint(blueprint)
            
            return ValidationFixResponse(
                success=True,
                data=fixed_blueprint,
                original_errors=val_result.get("overlaps", [])
            )
        except Exception as e:
            traceback.print_exc()
            return ValidationFixResponse(
                success=False,
                error=str(e)
            )

validation_controller = ValidationController()
