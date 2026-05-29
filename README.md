# CommentDetoxifier

**CommentDetoxifier** is a system designed to detect and neutralize harmful online comments. It identifies hateful, abusive, or threatening speech and transforms it into socially acceptable language — preserving the original context and intent.

## Project Structure
```bash
CommentDetoxifier/
├── config.py               # Project constants, hyperparameters, paths, device setup
├── dataset.py              # Custom PyTorch Dataset for multi-label toxicity detection
├── train.py                # Legacy: train a multi-label classifier (AutoModel*), prefer Sesame CLI
├── eval.py                 # Legacy: evaluate a trained model (AutoModel*), prefer Sesame CLI
├── main.py                 # Main inference & detoxification pipeline
├── third_party/sesame/      # Git submodule: Sesame (BERT-family training framework)
├── third_party/karen/       # Git submodule: Karen (LLM training framework)
├── requirements.txt        # Python dependencies
├── DevNotes.md             # Design notes, philosophy, tradeoffs
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

## Sesame Integration (Recommended Training Workflow)

This repo uses Hugging Face Transformers for inference and keeps a clean fallback contract:

- If `MODEL_PATH` exists, load your locally trained model first.
- Otherwise, fall back to Hugging Face pretrained weights (`MODEL` / `TOKENIZER` in `config.py`).

To make training and model swapping easier, this repo includes [Sesame](https://github.com/ChaoChienHung/Sesame.git) as a git submodule under `third_party/sesame/`. Sesame provides a unified CLI to train BERT-family models (BERT/RoBERTa/...) with a consistent output layout.

### 1) Initialize submodule

```bash
git submodule update --init --recursive
python3 -m pip install -e third_party/sesame
```

### 2) Train with Sesame and write outputs into this repo’s cache

Example: multi-label classification for Detox.io schema, outputs to `cache/models/toxic/<run_name>/`.

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

Sesame’s trainer engine saves:

- model weights to `cache/models/toxic/<run_name>/model/`
- tokenizer to `cache/models/toxic/<run_name>/`

### 3) Point inference to the trained model

Set `MODEL_PATH` in `config.py` to the run directory:

- `MODEL_PATH = os.path.join(TOXIC_MODEL_CACHE, "toxic_bert_v1")`

`main.py` will automatically detect whether the directory contains a `model/` subfolder (Sesame layout) and load accordingly.

## Karen Integration (Optional LLM Workflow)

This repo also includes Karen as a git submodule under `third_party/karen/`. Karen provides a unified CLI for fine-tuning / experimenting with LLMs.

Initialize:

```bash
git submodule update --init --recursive
python3 -m pip install -e third_party/karen
```

If you want to use a locally fine-tuned LLM at runtime, `main.py` supports the `local_llm` backend. Set:

- `DETOXIFY_BACKEND=local_llm`
- `LOCAL_LLM_RUN_DIR=<path to a Karen run dir>` (contains tokenizer files and a `model/` subfolder), or `LOCAL_LLM_MODEL_DIR=<path to a HF model dir>`

## Runtime Backends

`main.py` supports pluggable backends via environment variables:

- `TOXICITY_BACKEND`: `classifier` (default), `openai`, `local_llm`
- `DETOXIFY_BACKEND`: `openai` (default), `local_llm`

Local LLM settings:

- `LOCAL_LLM_RUN_DIR`, `LOCAL_LLM_MODEL_DIR`, `LOCAL_LLM_MAX_NEW_TOKENS`

For design rationale and tradeoffs, see [DevNotes.md](DevNotes.md).

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
