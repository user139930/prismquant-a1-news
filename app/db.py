# -*- coding: utf-8 -*-
"""SQLite 資料庫：新聞事件表與存取函式。"""
import datetime

from sqlalchemy import Column, DateTime, Float, Integer, JSON, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

Base = declarative_base()


class NewsEvent(Base):
    __tablename__ = "news_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=False)
    summary = Column(Text, default="")
    sentiment = Column(String(10), default="中性")
    topics = Column(JSON, default=list)
    instruments = Column(JSON, default=list)
    confidence = Column(Float, nullable=True)
    source = Column(String(255), default="")
    url = Column(Text, default="")
    published = Column(String(100), default="")
    sampled = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.summary or "",
            "sentiment": self.sentiment or "中性",
            "topics": self.topics or [],
            "instruments": self.instruments or [],
            "confidence": self.confidence,
            "source": self.source or "",
            "url": self.url or "",
            "published": self.published or "",
            "sampled": bool(self.sampled),
        }


engine = create_engine(
    f"sqlite:///{settings.db_path}",
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db():
    Base.metadata.create_all(engine)


def save_events(events: list[dict]):
    with SessionLocal() as s:
        for e in events:
            s.add(NewsEvent(**e))
        s.commit()


def latest_events(limit: int = 60):
    with SessionLocal() as s:
        rows = s.query(NewsEvent).order_by(NewsEvent.id.desc()).limit(limit).all()
        return [r.to_dict() for r in rows]
