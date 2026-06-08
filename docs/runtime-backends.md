# Runtime Backends

本文件整理 Detox.io 的後端契約（detect/detoxify），目標是讓團隊可以「換 backend 不改 UI、不改 API、盡量不改 pipeline」，並能用一致方式做回歸。

## 1) Toxicity Detect（TOXICITY_BACKEND）

### classifier（預設）

- 適用：常態 demo / API；延遲低、可離線
- 依賴：本地分類器 checkpoint（可由 Sesame 訓練）
- 契約：
  - 輸入：單句 comment（文字）
  - 輸出：6 labels（建議同時提供 raw score 與 threshold 判定，避免 UI/產品誤解）
- 常見失敗：
  - MODEL_PATH 不存在 / tokenizer 不一致
  - 裝置問題（CPU/GPU）

### openai

- 適用：快速 demo（不想管理分類器）、多語系探索
- 依賴：OPENAI_API_KEY
- 契約：
  - 必須以「結構化輸出」回傳 6 labels，避免自由文字造成 parse 漂移
  - 錯誤時需回傳可辨識的 error type，供 UI 呈現（例如 no_openai_key）

### local_llm

- 適用：全本地、無外網環境
- 依賴：LOCAL_LLM_RUN_DIR 或 LOCAL_LLM_MODEL_DIR
- 契約：
  - prompt 必須要求輸出可解析 JSON
  - parser 必須能容忍模型在 JSON 前後多吐文字的情況

## 2) Detoxify Rewrite（DETOXIFY_BACKEND）

### openai（預設）

- 適用：品質最好、上手最快
- 依賴：OPENAI_API_KEY
- 契約：
  - 輸出至少包含 revised_comment
  - 建議同時回傳 success/has_meaning/error_message（對齊 config.py 的 LLMReply），供 UI 做狀態呈現

### local_llm

- 適用：全本地、成本可控
- 依賴：LOCAL_LLM_RUN_DIR 或 LOCAL_LLM_MODEL_DIR
- 契約：
  - 輸出可用「純文字」或「JSON」，但需在 docs/api.md 與 pipeline 中固定一種，避免前端/後端各自假設不同格式

## 3) 回歸建議（Regression）

- 最小 smoke：
  - 任一固定輸入能完成 detect
  - 若輸入為 toxic，至少能完成一次 detoxify 並回傳 revised_comment
- Golden set（建議）：
  - detoxify 後再跑一次 detect，toxic labels 應下降（或至少不再觸發）
  - 失敗案例需要保存（避免「修好又壞」）

