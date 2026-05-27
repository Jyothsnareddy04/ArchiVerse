from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from agents.Cost_Estimator.services.cost_services.cost_service import estimate_cost
from database.db import get_db
import traceback

router = APIRouter(prefix="/api/cost")


@router.post("/estimate")
async def estimate(request: Request, db=Depends(get_db)):
    try:
        body = await request.json()
        result = await estimate_cost(body, db)
        return result
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )