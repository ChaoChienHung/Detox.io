# CommentDetoxifier

**CommentDetoxifier** is a system designed to detect and neutralize harmful online comments. It identifies hateful, abusive, or threatening speech and transforms it into socially acceptable language — preserving the original context and intent.

## Quickstart（最小可跑）

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
cp .env.example .env
python3 main.py
```

若你需要訓練工具（推薦），再初始化 submodules：

```bash
git submodule update --init --recursive
python3 -m pip install -e third_party/sesame
python3 -m pip install -e third_party/karen
```

## Documentation

- 協作規範與角色分工：AGENTS.md
- 文件索引入口：docs/doc-map.md
- 架構：docs/architecture.md
- 開發與環境變數：docs/development.md
- Runtime 後端：docs/runtime-backends.md
- API 契約（草案）：docs/api.md
- 訓練流程：docs/training.md
- 資料與隱私：docs/data.md
- 評估與安全：docs/evaluation-safety.md
- 維運：docs/operations.md
- 設計脈絡：docs/dev-notes.md
- Agent skills 存放位置：skills/

## Project Structure
```bash
CommentDetoxifier/
├── AGENTS.md               # Team roles, ownership, collaboration rules
├── docs/                   # Architecture / API / Dev / Training / Safety docs
├── skills/                 # Agent skills (for scaling agent workflows)
├── .env.example            # Environment variables template
├── config.py               # Project constants, hyperparameters, paths, device setup
├── dataset.py              # Custom PyTorch Dataset for multi-label toxicity detection
├── train.py                # Legacy: train a multi-label classifier (AutoModel*), prefer Sesame CLI
├── eval.py                 # Legacy: evaluate a trained model (AutoModel*), prefer Sesame CLI
├── main.py                 # Main inference & detoxification pipeline
├── third_party/sesame/      # Git submodule: Sesame (BERT-family training framework)
├── third_party/karen/       # Git submodule: Karen (LLM training framework)
├── requirements.txt        # Python dependencies
└── README.md               # Project overview and usage instructions
```

- **`config.py`**  
  Centralized configuration for the project. Defines constants, hyperparameters, directory paths, device setup, and data schemas, ensuring consistency and easy maintenance across scripts.

- **`dataset.py`**  
  Defines a custom PyTorch `CommentDataset` class for multi-label comment toxicity classification. Integrates Hugging Face tokenizers and provides optional caching for faster repeated usage.

- **`eval.py`**  
  Performs inference and evaluation on a pre-trained multi-label classifier. Uses `AutoTokenizer` / `AutoModelForSequenceClassification` so model architecture can be swapped without code changes.

- **`main.py`**  
  Orchestrates the complete detoxification pipeline. Combines a Transformer-based toxicity detector with an OpenAI LLM to automatically transform toxic comments into acceptable language. Includes model loading, tokenization, toxicity inference, LLM-based detoxification, logging, and robust retry mechanisms.

- **`model.py`**  
  Legacy module kept for reference. The current runtime uses Hugging Face `AutoModel*` loaders.

- **`train.py`**  
  Trains a multi-label classifier across six categories: `toxic`, `severe_toxic`, `obscene`, `threat`, `insult`, and `identity_hate`. Uses Hugging Face’s `Trainer` API and integrates with W&B for experiment tracking and logging.

## Runtime Backends

`main.py` supports pluggable backends via environment variables:

- `TOXICITY_BACKEND`: `classifier` (default), `openai`, `local_llm`
- `DETOXIFY_BACKEND`: `openai` (default), `local_llm`

Local LLM settings:

- `LOCAL_LLM_RUN_DIR`, `LOCAL_LLM_MODEL_DIR`, `LOCAL_LLM_MAX_NEW_TOKENS`

Training workflows (Sesame / Karen) are documented in docs/training.md.

For design rationale and tradeoffs, see docs/dev-notes.md.

## Key Improvements
1. Model Swappability
   - Uses `AutoTokenizer` / `AutoModelForSequenceClassification` to avoid hard-binding to a specific Transformer architecture.
2. Training Decoupling
   - Delegates training/eval to Sesame CLI while keeping inference logic in this repo.
3. Retry & Fallback Logic
   - Retries OpenAI calls with exponential backoff and falls back gracefully when OpenAI is unavailable.
4. Logging
   - Logs key events, including toxic detection and revised comments, to `app.log`.
5. User-Friendly
   - API key prompt hidden with `getpass`.
   - Clear feedback for socially acceptable vs detoxified comments.
