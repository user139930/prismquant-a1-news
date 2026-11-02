# PrismQuant A1 新聞智能體（News Agent）

把新聞抓下來、去重，再用大模型產生**摘要、情緒（利多／利空／中性）、主題標籤與映射標的**，
輸出結構化的事件卡片，供總前端或 A5 指揮官呼叫。

## 技術棧

- FastAPI + SQLAlchemy + SQLite（零資料庫設定）
- 大模型：OpenRouter（OpenAI 相容介面），預設 `deepseek/deepseek-chat`

## 快速開始

```bash
# 1. 建立虛擬環境並安裝（首次）
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt

# 2. 複製設定檔並填入你的 OpenRouter key
copy .env.example .env
# 編輯 .env，把 PQ_LLM_API_KEY 換成你的 key

# 3. 啟動
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8010
```

Windows 上也可以直接雙擊 `start.cmd`（會用本機 Python 直接啟動）。

## 接口

| 方法 | 路徑 | 說明 |
|---|---|---|
| GET | `/health` | 服務是否活著 |
| GET | `/api/v1/news/events?limit=60` | 讀取已分析的新聞事件 |
| POST | `/api/v1/news/collect?limit=10` | 觸發一次採集＋分析（抓 RSS → 去重 → LLM） |

互動文件：啟動後開 `http://127.0.0.1:8010/docs`。

## 幾點說明

1. **零依賴資料庫**：新聞是簡單的追加型資料，用 SQLite 即可（隊友的 news-main 也用 SQLite），
   不需要 PostgreSQL。
2. **抓不到 RSS 會退回示例**：頁面會標示 `sampled=true`，不會造假。
3. **密鑰安全**：`.env` 已被 `.gitignore` 擋住，不會被 push；`.env.example` 是給別人看的模板。
