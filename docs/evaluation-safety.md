# 評估與安全守門

本文件定義 Detox.io 的回歸測試口徑與安全策略，避免「改 prompt/換模型」後品質默默退化。

## 1) 評估目標

- Toxicity 降幅：detoxify 後的 toxic labels 應下降（或至少不再觸發）
- 語意保留：改寫後仍應保留原意（避免過度改寫成無關內容）
- 穩健性：LLM 回覆格式不穩時，系統仍應給出可理解的錯誤與 fallback

## 2) 指標（建議）

- Label-level：
  - 每類 label 的 before/after 觸發率
  - detoxify 成功率（after 全部為 0 的比例）
- Sample-level：
  - 平均 rounds（重試次數）
  - invalid_llm_output 比例
- 語意保留（可選，後續落地）：
  - embedding cosine similarity
  - LLM judge（需要固定 prompt + 版本化）

## 3) Golden set（建議）

- 規模：先做數十筆即可（覆蓋不同 label、不同語氣、不同長度）
- 保存方式：
  - 原文不建議直接進 repo（見 data.md 的隱私規範）
  - repo 內可保存 hash + 期望行為（例如：哪些 label 必須下降、哪些字不能出現）

## 4) 拒絕處理策略（草案）

遇到下列情況，系統可選擇拒絕改寫並回傳可理解的理由：

- 含明顯個資（電話、地址、證件號等）
- 含極端暴力/威脅的具體行動指示
- 含違法行為教學或明確仇恨煽動

拒絕回傳需有一致的 error.type，並能被前端呈現（見 docs/api.md）。

## 5) 失敗案例記錄（回歸資產）

每次遇到以下問題，需把「觸發條件」與「最小重現輸入」記錄在此文件或連到受控的案例庫：

- OpenAI 回覆不符合 schema（非 JSON、缺欄位、欄位型別錯）
- local_llm JSON 前後夾雜文字導致 parse 失敗
- detoxify 後毒性不降（或語意嚴重漂移）

