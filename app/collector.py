# -*- coding: utf-8 -*-
"""A1 採集：抓 RSS → 去重 → 大模型摘要／情緒／主題 → 結構化事件。"""
import re
import urllib.request
import xml.etree.ElementTree as ET

from app.config import settings
from app.llm import chat_json

SYSTEM = (
    "你是嚴謹的金融新聞分析員。分析新聞時："
    "情緒只用「利多 / 利空 / 中性」三者之一；"
    "主題標籤用簡短中文詞（如 關稅、利率、半導體、能源）；"
    "映射標的用常見代碼（如 AAPL、HSI、BTC），沒有把握就給空陣列。"
)

SAMPLE_NEWS = [
    ("示例：美聯儲官員暗示若通脹持續回落將放緩加息節奏", "（示例新聞，非真實事件）", "", ""),
    ("示例：芯片出口新規引發供應鏈擔憂", "（示例新聞，非真實事件）", "", ""),
    ("示例：原油庫存意外下降帶動油價走高", "（示例新聞，非真實事件）", "", ""),
]


def fetch_rss(url: str, timeout: int = 15):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            xml = resp.read()
        root = ET.fromstring(xml)
        items = []
        for it in root.iter("item"):
            def g(tag):
                el = it.find(tag)
                return (el.text or "").strip() if el is not None and el.text else ""
            title = g("title")
            if title:
                items.append((title, g("description"), g("link"), g("pubDate")))
        return items
    except Exception:
        return []


def _norm(s):
    s = (s or "").lower()
    return " ".join(re.sub(r"[^\w\u4e00-\u9fff]+", " ", s).split())


def dedupe(items):
    seen, out = [], []
    for it in items:
        k = _norm(it[0])
        if not k or any(k in sk or sk in k for sk in seen):
            continue
        seen.append(k)
        out.append(it)
    return out


def collect(limit: int = 10):
    """抓取 + 去重 + 大模型分析，回傳 (事件清單, 是否用了示例)。"""
    raw = []
    for src in settings.news_rss_sources:
        raw += fetch_rss(src)
    raw = dedupe(raw)
    sampled = not raw
    if sampled:
        raw = list(SAMPLE_NEWS)
    raw = raw[:limit]

    lines = []
    for i, (title, desc, _u, _d) in enumerate(raw):
        lines.append("[%d] 標題：%s\n摘要：%s" % (i, title, (desc or "")[:300]))
    prompt = (
        "請把下面每條新聞逐條分析，輸出 JSON 陣列，長度等於新聞條數，每條格式：\n"
        '{"summary":"一句中文摘要","sentiment":"利多|利空|中性","topics":["..."],"instruments":["..."],"confidence":0.85}\n\n'
        + "\n\n".join(lines)
    )
    out = chat_json(SYSTEM, prompt)
    if isinstance(out, dict):
        out = out.get("items", out.get("events", [out]))

    events = []
    for i, it in enumerate(raw):
        a = out[i] if isinstance(out, list) and i < len(out) else {}
        if not isinstance(a, dict):
            a = {}
        events.append({
            "title": it[0],
            "summary": a.get("summary", ""),
            "sentiment": a.get("sentiment", "中性"),
            "topics": a.get("topics", []),
            "instruments": a.get("instruments", []),
            "confidence": a.get("confidence"),
            "source": "示例" if sampled else "RSS",
            "url": it[2],
            "published": it[3],
            "sampled": 1 if sampled else 0,
        })
    return events, sampled
