"""
仅移动端 3D 地球 + 静态资源（最小可运行集合）。
不包含 mini-trip.html、frontend/ 等。

启动（在项目根目录）：
  uvicorn backend.server_mobile_minimal:app --host 0.0.0.0 --port 8000

访问：http://服务器IP:8000/mobile  或  http://服务器IP:8000/
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
TRIP_MOBILE_HTML_PATH = BASE_DIR / "mini-trip-mobile.html"

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/")
async def root():
    """根路径直接打开移动端页，手机少输 /mobile。"""
    return FileResponse(str(TRIP_MOBILE_HTML_PATH))


@app.get("/mobile")
async def mobile():
    return FileResponse(str(TRIP_MOBILE_HTML_PATH))


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/points/earth")
async def points_earth():
    """3D Earth page at /points/earth"""
    return FileResponse(str(TRIP_MOBILE_HTML_PATH))
