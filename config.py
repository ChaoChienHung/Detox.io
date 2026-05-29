import os
import torch
import datetime
from pydantic import BaseModel, Field

# -----------------
# Directories
# -----------------
CACHE_DIR = "cache"
DATA_DIR = "data"
RESULTS_DIR = "results"
MODEL_CACHE = os.path.join(CACHE_DIR, "models")
DATA_CACHE = os.path.join(CACHE_DIR, "datasets")
TOKENIZER_CACHE = os.path.join(CACHE_DIR, "tokenizers")

# -------------------------------
# XLM Roberta Language Detection
# -------------------------------
ROBERTA_CACHE = os.path.join(MODEL_CACHE, "language", "XLM-Roberta")
ROBERTA_TOKENIZER_CACHE = os.path.join(TOKENIZER_CACHE, "language", "XLM-Roberta")

# -------------------------------
# Toxic Model Directories
# -------------------------------
TOXIC_MODEL_CACHE = os.path.join(MODEL_CACHE, "toxic")
TOXIC_TOKENIZER_CACHE = os.path.join(TOKENIZER_CACHE, "toxic")

BERT_CACHE = os.path.join(TOXIC_MODEL_CACHE, "Bert")
BERT_TOKENIZER_CACHE = os.path.join(TOXIC_TOKENIZER_CACHE, "Bert")

LLM_MODEL_CACHE = os.path.join(MODEL_CACHE, "llm")
LLM_TOKENIZER_CACHE = os.path.join(TOKENIZER_CACHE, "llm")

# -----------------
# Model & Tokenizer
# -----------------
MODEL = "bert-base-uncased"
TOKENIZER = "bert-base-uncased"
MODEL_PATH = os.path.join(BERT_CACHE, "20251028-021857", "checkpoints", "checkpoint-35904")  # Best checkpoint folder

DETECTOR = "papluca/xlm-roberta-base-language-detection"

TOXICITY_BACKEND = os.environ.get("TOXICITY_BACKEND", "classifier")
DETOXIFY_BACKEND = os.environ.get("DETOXIFY_BACKEND", "openai")

OPENAI_DETOX_MODEL = os.environ.get("OPENAI_DETOX_MODEL", "gpt-4o-mini")
OPENAI_DETECT_MODEL = os.environ.get("OPENAI_DETECT_MODEL", "gpt-4o-mini")

LOCAL_LLM_RUN_DIR = os.environ.get("LOCAL_LLM_RUN_DIR", "")
LOCAL_LLM_MODEL_DIR = os.environ.get("LOCAL_LLM_MODEL_DIR", "")
LOCAL_LLM_MAX_NEW_TOKENS = int(os.environ.get("LOCAL_LLM_MAX_NEW_TOKENS", "128"))

# -----------------
# Hyperparameters
# -----------------
EPOCHS = 10
THRESHOLD = 0.5
BATCH_SIZE_EVAL = 32
LEARNING_RATE = 2e-6
BATCH_SIZE_TRAIN = 16

# -----------------
# Device
# -----------------
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ----------
# API Key
# ----------
API_KEY: str = os.environ.get("OPENAI_API_KEY")

# -----------------
# Timestamp
# -----------------
CURRENT_TIME = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

# ---------
# Schema
# ---------
class LLMReply(BaseModel):
    success: bool = Field(description="Indicates whether the LLM successfully processed the input.")
    has_meaning: bool = Field(description="Indicates if the original comment contains meaningful content.")
    error_message: str = Field(description="Detailed error message if processing failed; empty if successful.")
    revised_comment: str = Field(description="The revised version of the comment, modified to be socially acceptable.")


class ToxicityReply(BaseModel):
    toxic: int = Field(description="0 or 1")
    severe_toxic: int = Field(description="0 or 1")
    obscene: int = Field(description="0 or 1")
    threat: int = Field(description="0 or 1")
    insult: int = Field(description="0 or 1")
    identity_hate: int = Field(description="0 or 1")
