# 維運與部署

本文件定義 Detox.io 在「服務化」後的部署與維運考量（即使目前仍以 CLI demo 為主，也建議先對齊基本原則）。

## 1) 部署形態（建議）

- 最小：本機 CLI demo（python3 main.py）
- 服務化：FastAPI 單一 service（/api/detect、/api/detoxify、/api/health）

## 2) 資源策略（CPU/GPU）

- classifier：
  - CPU 可跑，但延遲較高；若需要吞吐，建議 GPU 或 quantization（後續規劃）
- local_llm：
  - 需要明確的 GPU/VRAM 預算與 batch 策略
  - 建議先以單例 lazy-load，避免每 request 重新載入

## 3) 日誌與敏感資訊

- 不記錄 OPENAI_API_KEY、access token 或任何憑證
- 盡量避免把原始 toxic comment 長期寫入 log（必要時做截斷/hash）
- 建議至少記錄：
  - backend 與模型版本
  - latency（detect/detoxify/total）
  - error.type（便於統計與告警）

## 4) 健康檢查與可用性

- /api/health（或 CLI health mode）應回報：
  - 當前 backend 選擇
  - 本地模型路徑是否可讀
  - OpenAI key 是否存在（不回傳 key 本身）

