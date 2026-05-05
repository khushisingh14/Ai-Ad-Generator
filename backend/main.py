from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.agents import run_ad_agent_flow


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
FRONTEND_DIR = PROJECT_DIR / "frontend"
FRONTEND_DIST = FRONTEND_DIR / "dist"

app = FastAPI(title="AI Ad Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if (FRONTEND_DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")


class GenerateAdRequest(BaseModel):
    product_url: str = "https://crowdwisdomtrading.com"
    niche: str = "trading research and market signals"


@app.get("/")
def index():
    index_file = FRONTEND_DIST / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Backend is running. Start the React frontend with npm run dev in /frontend."}


@app.post("/generate-ad")
def generate_ad(payload: GenerateAdRequest | None = None):
    request_data = payload or GenerateAdRequest()
    return run_ad_agent_flow(
        PROJECT_DIR,
        product_url=request_data.product_url,
        niche=request_data.niche,
    )


@app.get("/health")
def health():
    return {"status": "ok"}
