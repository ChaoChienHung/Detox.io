# Detox.io — AGENTS

本文件定義 Detox.io（CommentDetoxifier）專案的角色分工、權責邊界、協作流程與不可退化規則。當專案新增功能、調整架構或引入新團隊成員時，以本文件作為協作與決策的單一來源。

## 0. 文件優先序（SSOT）

1. AGENTS.md：不可退化規則、角色/權責、協作流程、文件地圖
2. docs/：架構、介面、開發、訓練、資料、評估與安全等長文規格
3. README.md：專案定位 + 最小可跑 Quickstart + docs 導覽入口
4. docs/dev-notes.md：設計哲學與取捨（偏動機/脈絡，不作為規格約束）
5. TODO.md：下一步工作清單與交付條件

若內容互相矛盾，依上述順序判定誰是「正確版本」；需要修正時，優先修正上游文件，避免規格漂移。

## 1. 不可退化規則（Non‑negotiables）

- 不在 repo 內提交任何金鑰/Token/敏感資料（含範例中的真實 key）；所有外部憑證一律以環境變數注入
- 文件命名與存放規範
  - Root 僅保留 AGENTS.md / README.md / TODO.md 三份核心文檔，其餘文件一律放入 docs/
  - docs/ 內文檔一律使用 kebab-case 小寫連字符命名
- Runtime 必須維持「可插拔後端」：毒性偵測與改寫後端以環境變數切換，不允許把某一後端寫死成唯一可用路徑
- 介面與 Schema 只能有一份權威定義
  - CLI 輸入/輸出與核心資料結構：以 docs/ 與程式中的 schema（config.py 的 Pydantic model）為準
  - API（FastAPI）啟用後：以 OpenAPI（/docs）與 docs/api.md 的版本化契約為準
- Submodule 邊界清晰
  - third_party/sesame：BERT-family 訓練工具
  - third_party/karen：LLM 訓練/實驗工具
  - 本 repo runtime 不依賴 submodule 的內部 Python API（只依賴其輸出產物的目錄與 from_pretrained 合約）
- 變更「介面/契約」必須同步更新文件與範例
  - 新增/改名環境變數 → 更新 .env.example 與 docs/development.md
  - 調整 API request/response → 更新 docs/api.md（含範例與錯誤碼）
  - 調整輸出字段（detect/detoxify 的 meta）→ 更新 docs/architecture.md 與 docs/api.md

## 2. 系統分層與模組邊界（What lives where）

### 2.1 核心模組

- 推理與編排（Pipeline）：main.py
  - 目標：把「輸入文字 → language detect → toxicity detect → detoxify rewrite」串成可回歸、可觀測、可替換後端的流程
- 設定與 Schema：config.py
  - 目標：集中管理 cache/路徑、backend 選擇、模型/LLM 參數、以及跨後端共用的結構化輸出 schema
- 資料與 tokenization：dataset.py
  - 目標：訓練/評估可重用的資料讀取邏輯與快取策略
- 訓練/評估（Legacy）：train.py / eval.py
  - 目標：保留可用性；推薦的訓練主流程在 submodule CLI（見 docs/training.md）

### 2.2 外部子系統（Submodules）

- Sesame（third_party/sesame）：多標籤分類器訓練/評估工具
- Karen（third_party/karen）：本地 LLM 訓練與 run directory 約定

子系統可以各自演進，但不得反向要求 runtime 依賴其內部實作細節；runtime 只接受「可由 Hugging Face from_pretrained 載入」的產物契約。

## 3. 角色與權責（Who owns what）

### 3.1 角色定義（可由同一人兼任）

- Tech Lead（Owner）
  - 擁有架構決策、介面契約與跨模組協作裁決權
- Backend Engineer（API/Service）
  - 擁有 FastAPI 服務、請求/回應 schema、效能與併發、部署形態
- Frontend Engineer（Demo/UI）
  - 擁有 demo user flow、UI 狀態機、與 API 的整合契約
- ML Engineer（Classifier）
  - 擁有 toxic classifier 的訓練、評估、checkpoint 管理與指標回歸
- LLM Engineer（Detoxify）
  - 擁有 OpenAI prompt/schema、local LLM prompt、以及改寫品質與安全策略
- Data Steward（Data/Privacy）
  - 擁有資料來源、標註/清理、匿名化策略、資料落盤與保存期限
- QA / Safety Reviewer
  - 擁有 golden set、回歸測試、極端內容處理規則與驗收門檻

### 3.2 模組擁有權（Ownership）

- docs/architecture.md：Tech Lead
- docs/api.md：Backend Engineer（與 Frontend Engineer 共同維護）
- docs/runtime-backends.md：Tech Lead（與 ML/LLM Engineer 共同維護）
- docs/training.md：ML Engineer（Sesame）、LLM Engineer（Karen）
- docs/data.md：Data Steward（與 ML Engineer 共同維護）
- docs/evaluation-safety.md：QA / Safety Reviewer（與 ML/LLM Engineer 共同維護）
- .env.example：Backend Engineer（若無 API 則由 Tech Lead 代理）

## 4. 協作流程（How we change things）

### 4.1 變更分類

- A. 介面/契約變更（高風險）
  - 例：新增/改名環境變數、改輸出欄位、改 API schema、改 prompt 的結構化輸出格式
- B. 模型/產物變更（中風險）
  - 例：換 toxic classifier checkpoint、調整 tokenizer、換 local LLM run dir 結構
- C. 內部實作變更（低風險）
  - 例：重構程式碼、效能優化、不影響外部觀察行為

### 4.2 介面/契約變更守門（A 類必做）

- 更新 docs/api.md（若涉及 API）與 docs/development.md（若涉及設定/啟動方式）
- 更新 .env.example（若新增/調整環境變數）
- 更新最小範例（README Quickstart 或 docs 中的 sample payload）
- 補齊回歸項（至少：一筆固定輸入的 detect + detoxify smoke 能跑通）

### 4.3 訓練/資料變更守門（B 類必做）

- 更新 docs/training.md 與 docs/data.md 中的「資料欄位/來源/切分」與「run directory」約定
- 更新或新增一次評估輸出（metrics/混淆/錯誤案例）並記錄在 docs/evaluation-safety.md（或連到實驗追蹤工具）

## 5. 文件地圖（Doc Map）

- docs/doc-map.md：docs/ 內文件索引（單一入口）
- /docs/index.md：文件導覽（新同學閱讀順序）
- /docs/architecture.md：系統分層、模組邊界、資料流、觀測面
- /docs/development.md：本機開發、環境變數、常用指令與除錯
- /docs/runtime-backends.md：Detect/Detoxify 後端契約、切換方式與回歸建議
- /docs/api.md：API 契約與錯誤碼（FastAPI 落地後需與 OpenAPI 同步）
- /docs/training.md：Sesame/Karen 訓練工作流與產物目錄約定
- /docs/data.md：資料欄位、隱私/匿名化、落盤規範與變更守門
- /docs/evaluation-safety.md：指標、golden set、拒絕策略與失敗案例沉澱
- /docs/operations.md：部署/維運、資源策略、日誌與健康檢查
- /docs/dev-notes.md：設計哲學與取捨脈絡（偏背景，不作為契約 SSOT）

## 6. 專屬指令處理模塊（文件更新）

當使用者提出「請協助更新項目的相關文檔」或等價需求時，遵循以下處理流程：

- 先盤點本倉庫內所有文檔狀態（root：AGENTS.md / README.md / TODO.md；docs/：其餘規格文件；skills/：agent skills）
- 依 docs/doc-map.md 的文件屬性與關係，篩選出需要更新的文件並排序優先級
  - 介面/契約相關（api.md、runtime-backends.md、development.md）優先於背景脈絡（dev-notes.md）
  - 若需求涉及「如何協作/如何守門」，優先更新 AGENTS.md 與 docs/doc-map.md
- 允許分階段完成：不要求一次性完成所有文件調整，但每次調整需同步更新相關索引（docs/doc-map.md 與本文件的 Doc Map 段落）
