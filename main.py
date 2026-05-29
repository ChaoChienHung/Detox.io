import os
import json
import time
import torch
import logging
import getpass
from typing import Literal

from config import *
from openai import OpenAI
from transformers import AutoModelForCausalLM, AutoModelForSequenceClassification, AutoTokenizer

# -----------------
# OpenAI Agent
# -----------------
logger = logging.getLogger(__name__)


class Agent:
    """
    Agent for converting toxic comments to socially acceptable comments
    using OpenAI's LLM. If OpenAI API is unavailable, falls back gracefully.
    """

    def __init__(self, model: str = OPENAI_DETOX_MODEL, max_retries: int = 3):
        """
        Initialize the Agent.

        Args:
            model: Name of the OpenAI model to use.
            max_retries: Number of retries if request to OpenAI fails.
        """
        self.client: OpenAI | None = None
        self.model: str = model
        self.max_retries: int = max_retries
        self.logger = logging.getLogger(__name__)
        self._create_secure_openai_client()

    def _create_secure_openai_client(self):
        """
        Create a secure OpenAI client using the API key from environment variables.
        Logs warning if no key is found.
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.logger.warning(
                "No OPENAI_API_KEY found. "
                "Set it using 'export OPENAI_API_KEY=your_key' (Linux/Mac) "
                "or 'setx OPENAI_API_KEY your_key' (Windows)."
            )
            return
        try:
            self.client = OpenAI(api_key=api_key)
            self.client.models.list()  # Test connection
            self.logger.info("OpenAI client created and tested successfully.")
        except Exception as e:
            self.logger.error(f"Failed to create OpenAI client: {e}")

    def detoxify(self, comment: str) -> LLMReply:
        """
        Convert a toxic comment to a socially acceptable version using OpenAI.
        Falls back to naive method if client unavailable.

        Args:
            comment: The input comment string.

        Returns:
            LLMReply object with revised comment and status.
        """
        if not self.client:
            self.logger.warning("No OpenAI client detected. Using naive fallback.")
            return LLMReply(
                success=False,
                has_meaning=False,
                error_message="No OpenAI client detected. Using naive fallback.",
                revised_comment=comment
            )

        if not isinstance(comment, str):
            raise TypeError(f"Expected comment as string, got {type(comment)}")

        # Define JSON schema for response validation
        schema = LLMReply.model_json_schema()
        schema["additionalProperties"] = False
        response_format_schema = {"name": "llm_reply", "schema": schema, "strict": True}

        # Retry loop in case OpenAI API call fails
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Convert hateful/toxic comments into socially acceptable comments "
                                "while preserving meaning."
                            )
                        },
                        {"role": "user", "content": comment}
                    ],
                    response_format={"type": "json_schema", "json_schema": response_format_schema}
                )

                try:
                    # Validate and return the response as LLMReply
                    return LLMReply.model_validate_json(response.choices[0].message.content)
                except Exception as e:
                    self.logger.error(f"Validation failed: {e}")
                    return LLMReply(success=False, has_meaning=False, error_message=str(e), revised_comment=comment)

            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
                if attempt == self.max_retries - 1:
                    self.logger.error("All retries failed. Using fallback.")
                    return LLMReply(success=False, has_meaning=False, error_message=str(e), revised_comment=comment)


class OpenAIToxicityDetector:
    def __init__(self, model: str = OPENAI_DETECT_MODEL, max_retries: int = 3):
        self.client: OpenAI | None = None
        self.model: str = model
        self.max_retries: int = max_retries
        self.logger = logging.getLogger(__name__)
        self._create_secure_openai_client()

    def _create_secure_openai_client(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.logger.warning("No OPENAI_API_KEY found.")
            return
        try:
            self.client = OpenAI(api_key=api_key)
            self.client.models.list()
        except Exception as e:
            self.logger.error(f"Failed to create OpenAI client: {e}")

    @staticmethod
    def _to_preds(reply: ToxicityReply):
        vals = [reply.toxic, reply.severe_toxic, reply.obscene, reply.threat, reply.insult, reply.identity_hate]
        return torch.tensor(vals, dtype=torch.int64).unsqueeze(0).cpu().numpy()

    def predict(self, comment: str):
        if not self.client:
            return torch.zeros((1, 6), dtype=torch.int64).cpu().numpy()

        schema = ToxicityReply.model_json_schema()
        schema["additionalProperties"] = False
        response_format_schema = {"name": "toxicity_reply", "schema": schema, "strict": True}

        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Classify the user text into 6 toxicity labels. "
                                "Return 0 or 1 for each label."
                            ),
                        },
                        {"role": "user", "content": comment},
                    ],
                    response_format={"type": "json_schema", "json_schema": response_format_schema},
                )
                parsed = ToxicityReply.model_validate_json(response.choices[0].message.content)
                return self._to_preds(parsed)
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(2 ** attempt)
                if attempt == self.max_retries - 1:
                    return torch.zeros((1, 6), dtype=torch.int64).cpu().numpy()


class LocalLLMBackend:
    def __init__(self, *, run_dir: str, model_dir: str, max_new_tokens: int):
        self.run_dir = run_dir
        self.model_dir = model_dir
        self.max_new_tokens = max_new_tokens
        self.logger = logging.getLogger(__name__)

        if not self.model_dir and self.run_dir:
            if os.path.isdir(self.run_dir) and os.path.exists(os.path.join(self.run_dir, "model")):
                self.model_dir = os.path.join(self.run_dir, "model")
            else:
                self.model_dir = self.run_dir

        tokenizer_dir = self.run_dir or self.model_dir
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_dir, cache_dir=LLM_TOKENIZER_CACHE)

        if torch.cuda.is_available():
            self.model = AutoModelForCausalLM.from_pretrained(self.model_dir, device_map="auto", cache_dir=LLM_MODEL_CACHE)
        else:
            self.model = AutoModelForCausalLM.from_pretrained(self.model_dir, cache_dir=LLM_MODEL_CACHE).to(DEVICE)
        self.model.eval()

    def _generate(self, prompt: str) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt")
        if hasattr(self.model, "device"):
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        else:
            inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

        with torch.no_grad():
            out = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
            )
        text = self.tokenizer.decode(out[0], skip_special_tokens=True)
        return text[len(prompt):].strip()

    @staticmethod
    def _extract_json(text: str) -> dict:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("No JSON object found")
        return json.loads(text[start : end + 1])

    def predict_toxicity(self, comment: str):
        prompt = (
            "Return strict JSON with keys: toxic, severe_toxic, obscene, threat, insult, identity_hate. "
            "Each value must be 0 or 1.\n\n"
            f"Text:\n{comment}\n\nJSON:\n"
        )
        raw = self._generate(prompt)
        try:
            data = self._extract_json(raw)
            parsed = ToxicityReply.model_validate(data)
            vals = [parsed.toxic, parsed.severe_toxic, parsed.obscene, parsed.threat, parsed.insult, parsed.identity_hate]
            return torch.tensor(vals, dtype=torch.int64).unsqueeze(0).cpu().numpy()
        except Exception as e:
            self.logger.error(f"Local LLM toxicity parsing failed: {e}")
            return torch.zeros((1, 6), dtype=torch.int64).cpu().numpy()

    def detoxify(self, comment: str) -> LLMReply:
        prompt = (
            "Rewrite the following text to be socially acceptable while preserving meaning. "
            "Return only the rewritten text.\n\n"
            f"Text:\n{comment}\n\nRewritten:\n"
        )
        revised = self._generate(prompt)
        return LLMReply(success=True, has_meaning=True, error_message="", revised_comment=revised or comment)


# -----------------
# Main
# -----------------
if __name__ == "__main__":

    # -----------------
    # Logger setup
    # -----------------
    logging.basicConfig(
        filename='app.log',
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    toxicity_backend = str(TOXICITY_BACKEND).lower()
    detoxify_backend = str(DETOXIFY_BACKEND).lower()

    needs_openai = toxicity_backend == "openai" or detoxify_backend == "openai"
    if needs_openai and not os.environ.get("OPENAI_API_KEY"):
        api_key = getpass.getpass("Enter your OpenAI API key (will not be shown as you type): ")
        os.environ["OPENAI_API_KEY"] = api_key

    local_llm = None
    if toxicity_backend == "local_llm" or detoxify_backend == "local_llm":
        if not LOCAL_LLM_RUN_DIR and not LOCAL_LLM_MODEL_DIR:
            raise ValueError("LOCAL_LLM_RUN_DIR or LOCAL_LLM_MODEL_DIR must be set for local_llm backend")
        local_llm = LocalLLMBackend(
            run_dir=LOCAL_LLM_RUN_DIR,
            model_dir=LOCAL_LLM_MODEL_DIR,
            max_new_tokens=LOCAL_LLM_MAX_NEW_TOKENS,
        )

    tokenizer = None
    model = None
    openai_detector = None

    if toxicity_backend == "classifier":
        if os.path.exists(MODEL_PATH):
            if os.path.isdir(MODEL_PATH) and os.path.exists(os.path.join(MODEL_PATH, "model")):
                tokenizer_dir = MODEL_PATH
                model_dir = os.path.join(MODEL_PATH, "model")
            else:
                tokenizer_dir = MODEL_PATH
                model_dir = MODEL_PATH

            tokenizer = AutoTokenizer.from_pretrained(tokenizer_dir)
            model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        else:
            tokenizer = AutoTokenizer.from_pretrained(TOKENIZER, cache_dir=TOXIC_TOKENIZER_CACHE)
            model = AutoModelForSequenceClassification.from_pretrained(
                MODEL,
                num_labels=6,
                problem_type="multi_label_classification",
                cache_dir=TOXIC_MODEL_CACHE,
            )

        model.to(DEVICE)
        model.eval()
    elif toxicity_backend == "openai":
        openai_detector = OpenAIToxicityDetector()
    elif toxicity_backend == "local_llm":
        pass
    else:
        raise ValueError(f"Unsupported TOXICITY_BACKEND: {TOXICITY_BACKEND}")

    detoxifier = None
    if detoxify_backend == "openai":
        detoxifier = Agent()
    elif detoxify_backend == "local_llm":
        detoxifier = local_llm
    else:
        raise ValueError(f"Unsupported DETOXIFY_BACKEND: {DETOXIFY_BACKEND}")

    # Prompt user for input comment
    comment: str = input("Please input the comment: ")

    # -------------------
    # Language Detection
    # -------------------
    detector_tokenizer = AutoTokenizer.from_pretrained(DETECTOR, cache_dir=ROBERTA_TOKENIZER_CACHE)
    detector = AutoModelForSequenceClassification.from_pretrained(DETECTOR, cache_dir=ROBERTA_CACHE)

    inputs = detector_tokenizer(comment, padding=True, truncation=True, return_tensors="pt")

    with torch.no_grad():
        logits = detector(**inputs).logits

    preds = torch.softmax(logits, dim=-1)
    
    # Map raw predictions to languages
    id2lang = detector.config.id2label
    vals, idxs = torch.max(preds, dim=1)
    language_score = {id2lang[k.item()]: v.item() for k, v in zip(idxs, vals)}
    comment = f'[{list(language_score.keys())[0]}] ' + comment
    
    # -----------------
    # Inference Loop
    # -----------------
    counter: int = 0  # Track number of failed attempts
    shouldDetect: bool = True
    llm_reply: LLMReply = LLMReply(success=True, has_meaning=True, error_message="", revised_comment=comment)

    while shouldDetect:
        # -----------------
        # Detect toxicity
        # -----------------
        if toxicity_backend == "classifier":
            with torch.no_grad():
                encodings = tokenizer(comment, truncation=True, padding="max_length", return_tensors="pt")
                input_ids = encodings["input_ids"].to(DEVICE)
                attention_mask = encodings["attention_mask"].to(DEVICE)

                outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                probs = torch.sigmoid(outputs.logits).cpu().numpy()
                preds = (probs > THRESHOLD).astype(int)
        elif toxicity_backend == "openai":
            preds = openai_detector.predict(comment)
        else:
            preds = local_llm.predict_toxicity(comment)

        # If no toxic labels detected, stop the loop
        if not preds.any():
            logger.info("The comment is socially acceptable.")
            break

        logger.info(f"The comment: \"{comment}\" is detected to be toxic.")

        # -----------------
        # Detoxify
        # -----------------
        llm_reply = detoxifier.detoxify(comment)

        if llm_reply.success:
            logger.info(f"Original Comment: \"{comment}\"")
            logger.info(f"Revised Comment: \"{llm_reply.revised_comment}\"")
            comment = llm_reply.revised_comment

        else:
            logger.error(llm_reply.error_message)
            counter += 1

        # Stop after 3 failed attempts
        if counter == 3:
            break

    # -----------------
    # Final output
    # -----------------
    if llm_reply.success:
        if llm_reply.has_meaning:
            logger.info(f"Comment: {comment}")
            print(f"Comment: {comment}")

        else:
            logger.info("This comment doesn't contain any meaningful content.")
            print("This comment doesn't contain any meaningful content.")
            
    else:
        logger.error(f"Model's error: {llm_reply.error_message}")
        print(f"Model's error: {llm_reply.error_message}")
