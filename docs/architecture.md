# 架構總覽

Detox.io 的目標是把「有害留言偵測」與「可接受語氣改寫」做成一條可回歸、可觀測、可替換後端的 pipeline，後續可落地成 CLI demo 或 API service。

## 核心概念

- Detect：對輸入文字輸出 6 類毒性標籤（toxic / severe_toxic / obscene / threat / insult / identity_hate），可含信心分數與 threshold 判定
- Detoxify：在盡量保留語意前提下，產出「社會可接受」版本的 revised comment，並附上處理 meta（使用的 backend、模型、耗時等）
- Backend 可插拔：Detect 與 Detoxify 各自可選不同後端實作，透過環境變數切換

## 系統分層

### 1) Orchestration（編排層）

- 入口：main.py
- 職責：
  - 讀取設定（config.py 的預設 + 環境變數覆蓋）
  - 串接 language detect、toxicity detect、detoxify rewrite
  - 以「最多重試 N 次」確保 detoxify 後的 toxic label 下降（或至少不再觸發）
  - 提供一致的 log 與錯誤回傳（未來 API/前端要靠這些狀態做 UI）

### 2) Contract（契約層）

- config.py
  - 環境變數：TOXICITY_BACKEND / DETOXIFY_BACKEND / OPENAI_* / LOCAL_LLM_*
  - Schema：LLMReply、ToxicityReply（以結構化輸出避免各後端語意漂移）
  - 路徑與 cache：約定所有產物落在 cache/，避免污染 repo

### 3) Backends（能力層）

毒性偵測（TOXICITY_BACKEND）：

- classifier：本地 Hugging Face 多標籤分類器（最穩、延遲低）
- openai：使用 OpenAI 以結構化格式回覆 6 類標籤
- local_llm：本地 CausalLM 用 prompt 產出 JSON 再抽取標籤

改寫（DETOXIFY_BACKEND）：

- openai：以 JSON schema 回覆 revised comment（品質佳、但外部依賴）
- local_llm：本地模型直接改寫（全本地、但品質/資源依賴較高）

各後端細節與限制見 runtime-backends.md。

### 4) Training Toolkits（子系統）

- third_party/sesame：分類器訓練/評估 CLI 與 run directory 約定
- third_party/karen：LLM 訓練/實驗工具與 run directory 約定

本 repo runtime 僅依賴其輸出產物的 on-disk layout + from_pretrained 合約，不依賴其內部 API。

## 資料流（Data Flow）

1. 使用者輸入 comment（CLI 或 API request）
2. language detect（可選）判斷語言，用於路由不同 detector/prompt（Roadmap）
3. toxicity detect → ToxicityReply（6 labels，必要時含分數）
4. 若有 toxic label：
   - detoxify rewrite → revised_comment
   - 重新跑一次 toxicity detect 驗證（最多重試 N 次）
5. 回傳結果（revised_comment、labels、meta、耗時、backend、模型資訊）

## 可觀測性（Observability）

建議保留以下訊息，供前端與回歸測試使用：

- backend 選擇與模型/版本資訊（classifier checkpoint、openai model、local llm model dir）
- 每步耗時（detect/detoxify/total）
- 狀態類型（ok / no_openai_key / model_not_found / invalid_llm_output / retry_exceeded）

如果要落盤（例如 SQLite/JSONL），需先對齊 data.md 的匿名化策略與保存期限。
