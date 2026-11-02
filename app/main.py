# -*- coding: utf-8 -*-
"""A1 新聞智能體：FastAPI 服務。

接口：
    GET  /health
    GET  /api/v1/news/events?limit=60
    POST /api/v1/news/collect?limit=10
"""
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app import collector, db
from app.config import settings

DEMO_PAGE = (Path(__file__).parent / "demo.html").read_text(encoding="utf-8")

db.init_db()

app = FastAPI(
    title=settings.service_name,
    version="0.1.0",
    description="PrismQuant A1 新聞智能體：抓取 RSS 新聞、去重，並用大模型產生摘要、情緒與主題標籤。",
)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index():
    return DEMO_PAGE


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": settings.service_name,
        "version": app.version,
        "scope": "api_process",
    }


@app.get("/api/v1/news/events")
def list_events(limit: int = Query(60, ge=1, le=200)):
    events = db.latest_events(limit)
    return {
        "agent": "A1 新聞情報",
        "count": len(events),
        "sampled": any(e["sampled"] for e in events),
        "events": events,
    }


@app.post("/api/v1/news/collect")
def collect_news(limit: int = Query(10, ge=1, le=50)):
    try:
        events, sampled = collector.collect(limit)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={"code": "collection_failed", "message": str(exc)},
        )
    db.save_events(events)
    return {"collected": len(events), "sampled": sampled}
