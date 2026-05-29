# TODO

- [ ] 決定 Demo 形態（純前端靜態頁 / 前後端分離 / 後端模板渲染）
- [ ] 定義核心 User Flow（輸入留言 → 偵測結果 → 一鍵 Detoxify → 對比前後差異 → 送出/複製）

## Frontend（Reddit / PTT 風格）
- [ ] 設計資訊架構
  - [ ] Feed（貼文列表）+ 留言串（thread）
  - [ ] Comment composer（輸入框）+ 即時偵測 badge（toxic labels）
  - [ ] Before/After diff view（高亮修改處）
  - [ ] History（最近處理過的留言）
- [ ] UI 元件草圖（含狀態：loading / fail / no-openai / no-model）
- [ ] 前端技術選型
  - [ ] Option A：FastAPI + Jinja2 + HTMX（最快做出可用 demo）
  - [ ] Option B：FastAPI（API only）+ React/Vue（互動最好但工程量較大）

## Backend（API）
- [ ] 新增 FastAPI service（單一入口）
- [ ] API 設計（先做最小集合）
  - [ ] `POST /api/detect`：回傳 6 類 label 與信心分數/threshold 結果
  - [ ] `POST /api/detoxify`：回傳 revised comment + meta（backend、模型、耗時）
  - [ ] `GET /api/health`：顯示目前 backend（classifier/openai/local_llm）與模型路徑
- [ ] 併發與效能
  - [ ] 模型 lazy-load + 全域單例（避免每 request 重載）
  - [ ] GPU/CPU 裝置策略（device_map / fallback）

## Model / Inference
- [ ] 統一「模型來源」介面（local run dir / HF model id / cache）
- [ ] 本地 LLM detoxify prompt 改成可配置（避免 prompt hardcode）
- [ ] OpenAI toxicity（6 labels）提示詞與 schema 做壓力測試（噪音輸出、非 JSON）
- [ ] 加入可選的「只做 detoxify，不做 detect」模式（例如純改寫 demo）

## Data / Storage
- [ ] 新增簡單資料層（SQLite or JSONL）
  - [ ] 儲存貼文、留言、detoxify 前後、標籤、模型版本、時間戳
  - [ ] 匿名化策略（避免落盤敏感內容，或提供一鍵清除）

## Evaluation / Safety
- [ ] 新增小型 golden set（幾十筆）做回歸測試（detoxify 前後的 toxic label 應下降）
- [ ] 定義指標：toxic label 降幅、語意保留度（LLM judge / embedding 相似度）
- [ ] 加入「拒絕處理」策略（極端內容、個資、違規內容的回應規則）

## Tests
- [ ] 引入測試框架（pytest）
- [ ] 單元測試：`MODEL_PATH` 目錄解析（flat vs `run_dir/model`）
- [ ] 單元測試：local LLM JSON 抽取（含壞格式、前後夾雜文字）
- [ ] 單元測試：OpenAI schema parse（mock response）
- [ ] 端到端 smoke：用 `TOXICITY_BACKEND=classifier` 跑一筆固定輸入，確保流程不崩

## DevX / Ops
- [ ] `.env.example`（OPENAI_API_KEY、backend 選項、模型路徑）
- [ ] 一鍵啟動指令（Makefile / scripts）
- [ ] CI：py_compile + 基本 lint（先輕量）

## Roadmap（比較進階但可能很酷）
- [ ] 多語系支援（依語言自動切換不同 detector / prompt）
- [ ] 多模型 A/B（同一段文字跑兩個 backend，前端做比較）
- [ ] 互動式「回覆建議」：輸入 thread context，產出更像真人的回覆
