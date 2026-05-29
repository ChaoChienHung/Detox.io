# Dev Notes
This document captures the design philosophy, constraints, and tradeoffs of this repo, especially around model training and inference.

## Goals
- Keep inference simple and stable.
- Make model architecture swaps cheap (BERT ↔ RoBERTa ↔ DeBERTa…).
- Separate “training framework” evolution from “application logic” evolution.
- Prefer reproducible outputs with a predictable on-disk layout.

## Core Design
### 1) Stable inference contract (`from_pretrained`)
Inference is built around a single contract: provide a directory (or Hugging Face model id) that can be loaded by:

- `AutoTokenizer.from_pretrained(...)`
- `AutoModelForSequenceClassification.from_pretrained(...)`

This avoids hard-binding to `BertTokenizer` / `BertForSequenceClassification`, which would require code edits when switching architectures.

### 2) Local-first, HuggingFace fallback
Inference follows:

- If `MODEL_PATH` exists, load local model artifacts first.
- Otherwise, fall back to pretrained weights using `MODEL` / `TOKENIZER`.

This enables:
- offline-friendly runs once a model is trained and cached
- zero-setup onboarding (pretrained path works out of the box)

### 3) Training delegated to Sesame
Training is delegated to Sesame (git submodule under `third_party/sesame/`) to reduce coupling:

- Detox.io focuses on the end-to-end detoxification application flow.
- Sesame focuses on training/evaluation utilities and BERT-family training conventions.

We treat Sesame as a “training toolkit” rather than part of the app runtime logic.

### 4) Output layout compatibility
Sesame’s trainer engine saves:
- tokenizer to `<run_dir>/`
- model weights to `<run_dir>/model/`

Detox.io inference supports both:
- “flat” Hugging Face directories (model + tokenizer in same folder)
- Sesame layout (`model/` subfolder)

This is why `main.py` / `eval.py` detect whether `MODEL_PATH/model/` exists.

## Why git submodule (vs copying code)
### Benefits
- Version pinning: this repo can lock Sesame to a known-good commit.
- Cleaner boundaries: training toolkit can evolve independently.
- Easier upgrades: bumping Sesame is a controlled change (update submodule pointer).

### Costs / tradeoffs
- Extra setup step: contributors must run `git submodule update --init --recursive`.
- Tooling friction: some IDEs and CI need explicit submodule handling.
- Update discipline: upgrading Sesame is deliberate (not automatic).

## Cache conventions
We keep caches under `cache/` to avoid mixing source code with artifacts:
- `cache/models/` for downloaded HF models and trained runs
- `cache/tokenizers/` for tokenizer cache
- `cache/datasets/` for dataset cache

Names like `TOXIC_MODEL_CACHE` are intentionally model-agnostic; older `BERT_*` constants remain for compatibility and migration.

## “Legacy scripts” stance
This repo still contains `train.py` / `eval.py` for convenience, but the preferred workflow is:
- use Sesame CLI for training/evaluation
- use this repo’s `main.py` for inference + OpenAI detoxification

This keeps the application stable while letting the training surface iterate faster.

