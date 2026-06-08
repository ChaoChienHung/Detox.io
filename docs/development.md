# 開發指南

本文件描述本機開發、常用指令與環境變數。若你只想快速跑起來，先看 README 的 Quickstart。

## 1) 安裝與初始化

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

若需要訓練工具（推薦）：

```bash
git submodule update --init --recursive
python3 -m pip install -e third_party/sesame
python3 -m pip install -e third_party/karen
```

## 2) 環境變數

以 `.env.example` 為範本複製一份 `.env`（不要提交 `.env`）：

```bash
cp .env.example .env
```

### 2.1 Backend 選擇

- TOXICITY_BACKEND：classifier | openai | local_llm（預設 classifier）
- DETOXIFY_BACKEND：openai | local_llm（預設 openai）

### 2.2 OpenAI

- OPENAI_API_KEY：必填（使用 openai backend 時）
- OPENAI_DETECT_MODEL：預設 gpt-4o-mini
- OPENAI_DETOX_MODEL：預設 gpt-4o-mini

### 2.3 Local LLM

- LOCAL_LLM_RUN_DIR：指向 Karen 的 run dir（含 tokenizer 檔案與 model/ 子資料夾）
- LOCAL_LLM_MODEL_DIR：或直接指向 Hugging Face 可載入的模型目錄
- LOCAL_LLM_MAX_NEW_TOKENS：預設 128

## 3) 常用指令

### 3.1 CLI demo（互動式）

```bash
python3 main.py
```

### 3.2 指定後端跑一筆（範例）

```bash
TOXICITY_BACKEND=classifier DETOXIFY_BACKEND=openai python3 main.py
```

```bash
TOXICITY_BACKEND=local_llm DETOXIFY_BACKEND=local_llm LOCAL_LLM_MODEL_DIR=/path/to/model python3 main.py
```

## 4) 除錯建議（Debug)

- 若遇到模型載入問題，優先確認：
  - config.py 的 MODEL_PATH 是否存在
  - 或者改用 Hugging Face model id（讓 from_pretrained 自行下載到 cache/）
- 若 openai 回覆非 JSON（或 schema 不符），需把案例記錄到 docs/evaluation-safety.md 的「失敗案例」區，避免之後回歸時重複踩坑
