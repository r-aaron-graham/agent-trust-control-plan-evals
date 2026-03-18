from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.routes.api import router as api_router
from app.services.pipeline import AgentWorkbench

workbench = AgentWorkbench()
app = FastAPI(title=settings.app_name, version=settings.version)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/api")
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


@app.get("/")
def home() -> FileResponse:
    return FileResponse("frontend/index.html")
