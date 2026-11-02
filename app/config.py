# -*- coding: utf-8 -*-
"""A1 設定：環境變數前綴 PQ_，讀取專案根目錄的 .env。"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        env_prefix="PQ_",
        extra="ignore",
        hide_input_in_errors=True,
    )

    service_name: str = "PrismQuant A1 News API"
    environment: str = "development"
    host: str = "127.0.0.1"
    port: int = 8010
    cors_origins: list[str] = []

    # 大模型（OpenRouter，OpenAI 相容介面）
    llm_api_key: str = ""
    llm_model: str = "deepseek/deepseek-chat"
    llm_base_url: str = "https://openrouter.ai/api/v1"

    # 資料庫（SQLite，零設定）
    db_path: str = "news.sqlite3"

    # 新聞來源（RSS，免費、免 key）
    news_rss_sources: list[str] = [
        "http://feeds.bbci.co.uk/news/business/rss.xml",
        "https://feeds.bbci.co.uk/news/world/rss.xml",
    ]


settings = Settings()
