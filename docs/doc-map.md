# Doc Map

本文件是 Detox.io 的文件索引（docs/ 內的單一入口）。目標是讓團隊在「改功能/改契約/換模型」時，能快速找到應該更新的文件，並維持文件一致性。

## Start Here

1. README.md：專案定位與最小可跑
2. AGENTS.md：協作規範、角色與守門流程
3. docs/doc-map.md：本索引（docs/ 單一入口）

## docs/ Tree

```
docs/
├── doc-map.md
├── index.md
├── architecture.md
├── development.md
├── runtime-backends.md
├── api.md
├── training.md
├── data.md
├── evaluation-safety.md
├── operations.md
└── dev-notes.md
```

## Files

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

