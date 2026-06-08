# Detox.io 文件導覽

本目錄承載 Detox.io（CommentDetoxifier）的「可協作、可落地、可回歸」規格文件。若你是第一次加入專案，建議依序閱讀：

1. README.md（專案定位 + 最小可跑）
2. AGENTS.md（角色分工、協作流程、不可退化規則）
3. docs/doc-map.md（文件索引入口）
4. docs/architecture.md（系統分層與資料流）
5. docs/development.md（本機開發與環境變數）
6. docs/runtime-backends.md（後端切換與限制）

## 文件清單

- doc-map.md：docs/ 內文件索引（單一入口）
- architecture.md：系統架構、模組邊界、資料流、觀測面
- development.md：Quickstart、環境變數、常用指令、除錯
- runtime-backends.md：TOXICITY_BACKEND / DETOXIFY_BACKEND 的契約與測試建議
- api.md：API 契約與版本策略（FastAPI 落地後的單一來源）
- training.md：Sesame（分類器）與 Karen（LLM）訓練工作流與產物約定
- data.md：資料集、欄位、授權/隱私、匿名化策略與落盤規範
- evaluation-safety.md：指標、golden set、回歸與拒絕策略
- operations.md：部署、效能、資源（CPU/GPU）策略、日誌與維運
- dev-notes.md：設計哲學與取捨脈絡
