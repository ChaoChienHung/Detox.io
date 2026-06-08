# API 契約（草案）

本文件定義 Detox.io 的最小 API 集合，供前端與後端協作。當 FastAPI 落地後，本文件需與 OpenAPI（/docs）一致，並作為版本化契約維護。

## 通用約定

- Base path：`/api`
- 編碼：UTF-8
- 時間單位：毫秒（ms）
- 版本策略：
  - v0：不保證向後相容（目前階段）
  - v1 起：對 request/response 做向後相容策略（新增欄位優先、避免改名/移除）

## 1) POST /api/detect

### Request

```json
{
  "text": "you are an idiot"
}
```

### Response（建議）

```json
{
  "labels": {
    "toxic": 1,
    "severe_toxic": 0,
    "obscene": 0,
    "threat": 0,
    "insult": 1,
    "identity_hate": 0
  },
  "scores": {
    "toxic": 0.97,
    "severe_toxic": 0.02,
    "obscene": 0.05,
    "threat": 0.01,
    "insult": 0.92,
    "identity_hate": 0.01
  },
  "threshold": 0.5,
  "meta": {
    "backend": "classifier",
    "model": "cache/models/toxic/toxic_bert_v1",
    "latency_ms": 32
  }
}
```

## 2) POST /api/detoxify

### Request

```json
{
  "text": "you are an idiot",
  "options": {
    "max_rounds": 3,
    "verify_with_detect": true
  }
}
```

### Response（建議）

```json
{
  "original_text": "you are an idiot",
  "revised_text": "I disagree with your point, but I'm open to hearing more details.",
  "detect": {
    "before": {
      "labels": {
        "toxic": 1,
        "severe_toxic": 0,
        "obscene": 0,
        "threat": 0,
        "insult": 1,
        "identity_hate": 0
      }
    },
    "after": {
      "labels": {
        "toxic": 0,
        "severe_toxic": 0,
        "obscene": 0,
        "threat": 0,
        "insult": 0,
        "identity_hate": 0
      }
    }
  },
  "meta": {
    "toxicity_backend": "classifier",
    "detoxify_backend": "openai",
    "openai_model": "gpt-4o-mini",
    "latency_ms": 412,
    "rounds": 2
  }
}
```

## 3) GET /api/health

### Response（建議）

```json
{
  "status": "ok",
  "backend": {
    "toxicity": "classifier",
    "detoxify": "openai"
  },
  "model": {
    "toxicity_model_path": "cache/models/toxic/toxic_bert_v1",
    "local_llm_run_dir": "",
    "local_llm_model_dir": ""
  }
}
```

## 錯誤回應（建議）

### 格式

```json
{
  "error": {
    "type": "no_openai_key",
    "message": "OPENAI_API_KEY is missing"
  }
}
```

### 常見 error.type

- no_openai_key：需要 OpenAI 但未提供 OPENAI_API_KEY
- model_not_found：本地模型路徑不存在或不可讀
- invalid_llm_output：LLM 回覆無法解析成預期格式
- retry_exceeded：重試次數用盡仍無法得到可接受輸出

