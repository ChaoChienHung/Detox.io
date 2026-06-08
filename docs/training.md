# 訓練工作流

本專案將「訓練」與「推理/應用」解耦：Detox.io runtime 只依賴 Hugging Face `from_pretrained` 可載入的產物與固定的目錄約定；訓練細節由子系統（Sesame/Karen）負責。

## 1) Toxicity classifier（Sesame，推薦）

### 1.1 安裝

```bash
git submodule update --init --recursive
python3 -m pip install -e third_party/sesame
```

### 1.2 訓練（範例）

```bash
python3 -m bert.train \
  --task multilabel_classification \
  --arch bert \
  --engine trainer \
  --train_file data/train_10k.csv \
  --output_dir cache/models/toxic \
  --dataset_cache_dir cache/datasets \
  --tokenizer_cache_dir cache/tokenizers/toxic \
  --model_cache_dir cache/models/hf \
  --run_name toxic_bert_v1
```

### 1.3 產物約定（run directory）

- `cache/models/toxic/<run_name>/`
  - tokenizer 檔案（tokenizer.json、tokenizer_config.json、vocab 等）
  - `model/`：模型權重資料夾（Sesame layout）

Detox.io runtime 需能支援：

- 「flat layout」：model 與 tokenizer 在同一層資料夾
- 「Sesame layout」：model 權重在 `<run_dir>/model/`

## 2) Local LLM（Karen，可選）

### 2.1 安裝

```bash
git submodule update --init --recursive
python3 -m pip install -e third_party/karen
```

### 2.2 產物約定

Karen 的 run directory 通常包含：

- tokenizer 檔案在 run dir 根目錄
- `model/` 子資料夾放權重

runtime 可透過：

- `LOCAL_LLM_RUN_DIR=<karen_run_dir>`，或
- `LOCAL_LLM_MODEL_DIR=<hf_model_dir>`

## 3) 版本與回歸建議

- 模型版本命名：以 `<task>_<arch>_<date_or_semver>`，並在 README / docs/evaluation-safety.md 記錄「何時換了什麼、為何換」
- 每次換 checkpoint 或 prompt：
  - 至少跑一次 golden set（或最小 smoke）
  - 保存失敗案例（尤其是 parse error、語意漂移、毒性未下降）
