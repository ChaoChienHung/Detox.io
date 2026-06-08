# 資料與隱私

本文件描述訓練/評估資料的欄位定義、處理方式與隱私規範。任何「新增資料源」或「引入落盤儲存」的變更，都必須先更新此文件。

## 1) 目錄

- data/：靜態 CSV（訓練/實驗用）
- cache/datasets/：資料處理快取（可刪、不可當作單一來源）
- results/：評估輸出（建議放 aggregate 指標，不放原文）

## 2) CSV 欄位定義（現況）

以 data/train_10k.csv 為例：

- id：樣本識別碼
- comment_text：留言原文（可能包含髒話、仇恨言論或威脅內容）
- toxic / severe_toxic / obscene / threat / insult / identity_hate：0/1 多標籤

## 3) 資料使用風險與防護

- 有害內容暴露：任何人 pull repo 可能直接看到 toxic 內容；建議在 demo/截圖/文件中避免貼出完整原文
- 落盤策略（若啟用 History/Storage）：
  - 預設不落盤原始留言；若必須保存，需提供「一鍵清除」並設定保存期限
  - 優先保存抽象化資訊：labels、耗時、backend、模型版本、統計指標
- 匿名化與個資：
  - 不允許在 logs / database 中長期保存可能含個資的原文
  - 若需要做回歸（golden set），建議以 hash 或脫敏後的片段保存，並把原文存於受控位置（不進 repo）

## 4) 變更守門

- 新增資料欄位或標籤：需同步更新
  - dataset.py（讀取/前處理）
  - docs/evaluation-safety.md（指標與回歸口徑）
  - docs/api.md（若對外暴露 labels/scores）
