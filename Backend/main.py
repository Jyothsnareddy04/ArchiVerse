from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import traceback

# Import routers
from routes.layout import router as layout_router
from routes.blueprint import router as blueprint_router
from routes.interior import router as interior_router
from routes.exterior import router as exterior_router
from routes.cost_routes import router as cost_router
from routes.validation import router as validation_router
from routes.project import router as project_router
from auth.auth_routes import router as auth_router

from database.db import engine, Base

app = FastAPI(
    title="ArchiVerse Backend",
    description="AI-based architectural automation system",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc)
        }
    )

# Routers
app.include_router(layout_router)
app.include_router(blueprint_router)
app.include_router(interior_router)
app.include_router(exterior_router)
app.include_router(cost_router)
app.include_router(validation_router)
app.include_router(project_router)
app.include_router(auth_router)

# Startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Root
@app.get("/")
async def root():
    return {
        "message": "ArchiVerse Backend Running",
        "status": "online",
        "cost_api": "/api/cost/estimate"
    }

# Run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)