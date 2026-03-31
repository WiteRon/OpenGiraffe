from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 项目根目录（backend 的上一级）
BASE_DIR = Path(__file__).resolve().parent.parent
TRIP_HTML_PATH = BASE_DIR / "mini-trip.html"
TRIP_MOBILE_HTML_PATH = BASE_DIR / "mini-trip-mobile.html"

# 静态资源（供 mini-trip-mobile 的 globe.gl 等用）
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/")
async def root():
    return FileResponse(str(TRIP_HTML_PATH))


@app.get("/desktop")
async def desktop():
    return FileResponse(str(TRIP_HTML_PATH))


@app.get("/mobile")
async def mobile():
    return FileResponse(str(TRIP_MOBILE_HTML_PATH))


@app.get("/api/health")
async def health():
    return {"status": "ok"}
