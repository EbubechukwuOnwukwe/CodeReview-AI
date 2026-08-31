import json
import os
import threading
import time

from dotenv import load_dotenv
from openai import OpenAI, RateLimitError
from pydantic import BaseModel


load_dotenv()


class GroqService:

    MODEL = os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-120b",
    )

    BASE_URL = "https://api.groq.com/openai/v1"

    # ---------------------------------------------------------
    # GROQ FREE-TIER SAFETY SETTINGS
    # ---------------------------------------------------------

    # Your current Groq limit is 8,000 TPM.
    TPM_LIMIT = int(
        os.getenv(
            "GROQ_TPM_LIMIT",
            "8000",
        )
    )

    # Do NOT attempt to consume the entire 8,000.
    #
    # This leaves room for:
    # - system instructions
    # - prompt overhead
    # - response tokens
    # - estimation inaccuracies
    SAFE_TPM_LIMIT = int(
        os.getenv(
            "GROQ_SAFE_TPM_LIMIT",
            "7000",
        )
    )

    # Approximate characters per token.
    CHARS_PER_TOKEN = 4

    # Reserve room for the model's response.
    RESERVED_OUTPUT_TOKENS = 700

    # Shared between GroqService instances in this Django process.
    _usage_lock = threading.Lock()
    _usage_window = []

    def __init__(self):

        api_key = os.getenv(
            "GROQ_API_KEY"
        )

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url=self.BASE_URL,
        )

    # =========================================================
    # TOKEN ESTIMATION
    # =========================================================

    @classmethod
    def estimate_tokens(
        cls,
        text: str,
    ):
        if not text:
            return 0

        return max(
            1,
            len(text) // cls.CHARS_PER_TOKEN,
        )

    def estimate_request_tokens(
        self,
        prompt,
        system_instruction,
    ):
        prompt_tokens = (
            self.estimate_tokens(prompt)
        )

        system_tokens = (
            self.estimate_tokens(
                system_instruction or ""
            )
        )

        return (
            prompt_tokens
            + system_tokens
            + self.RESERVED_OUTPUT_TOKENS
        )

    # =========================================================
    # RATE LIMITER
    # =========================================================

    @classmethod
    def _cleanup_usage_window(cls):
        now = time.monotonic()

        cls._usage_window = [
            entry
            for entry in cls._usage_window
            if now - entry["time"] < 60
        ]

    @classmethod
    def _tokens_used_in_window(cls):
        return sum(
            entry["tokens"]
            for entry in cls._usage_window
        )

    @classmethod
    def _wait_for_capacity(
        cls,
        required_tokens,
    ):
        """
        Wait until enough estimated token capacity
        exists inside the rolling 60-second window.
        """

        while True:

            with cls._usage_lock:

                cls._cleanup_usage_window()

                used = (
                    cls._tokens_used_in_window()
                )

                available = (
                    cls.SAFE_TPM_LIMIT
                    - used
                )

                if required_tokens <= available:

                    cls._usage_window.append(
                        {
                            "time": time.monotonic(),
                            "tokens": required_tokens,
                        }
                    )

                    print(
                        f"[GROQ RATE LIMITER] "
                        f"Capacity available: "
                        f"{available:,} tokens | "
                        f"Request: "
                        f"{required_tokens:,} tokens"
                    )

                    return

                if not cls._usage_window:

                    return

                oldest = min(
                    cls._usage_window,
                    key=lambda item: item["time"],
                )

                elapsed = (
                    time.monotonic()
                    - oldest["time"]
                )

                wait_seconds = max(
                    1,
                    60 - elapsed + 1,
                )

                print(
                    f"[GROQ RATE LIMITER] "
                    f"Used: {used:,}/"
                    f"{cls.SAFE_TPM_LIMIT:,} tokens | "
                    f"Request: {required_tokens:,} tokens | "
                    f"Waiting: {wait_seconds:.0f}s"
                )

            time.sleep(
                wait_seconds
            )

    # =========================================================
    # STRUCTURED GENERATION
    # =========================================================

    def generate_structured(
        self,
        prompt: str,
        response_schema,
        system_instruction: str | None = None,
        max_retries: int = 4,
    ):

        default_system_instruction = (
            "You are a precise code analysis assistant. "
            "Always respond with valid JSON matching "
            "the requested schema exactly."
        )

        if system_instruction:

            final_system_instruction = (
                f"{default_system_instruction}\n\n"
                f"{system_instruction}"
            )

        else:

            final_system_instruction = (
                default_system_instruction
            )

        estimated_tokens = (
            self.estimate_request_tokens(
                prompt,
                final_system_instruction,
            )
        )

        # -----------------------------------------------------
        # Fail early if a request somehow reaches this layer
        # that is larger than our safe per-request budget.
        # -----------------------------------------------------

        if estimated_tokens > self.SAFE_TPM_LIMIT:

            raise ValueError(
                "This AI request is too large to send "
                "to Groq in one request. The code should "
                "be divided into smaller analysis chunks."
            )

        # -----------------------------------------------------
        # Wait until Groq has enough TPM capacity.
        # -----------------------------------------------------

        self._wait_for_capacity(
            estimated_tokens
        )

        for attempt in range(max_retries):

            try:

                print(
                    f"[GROQ] Sending request "
                    f"(~{estimated_tokens} tokens)"
                )

                response = (
                    self.client
                    .chat
                    .completions
                    .create(
                        model=self.MODEL,

                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    final_system_instruction
                                ),
                            },
                            {
                                "role": "user",
                                "content": prompt,
                            },
                        ],

                        response_format={
                            "type": "json_object"
                        },
                    )
                )

                raw_text = (
                    response
                    .choices[0]
                    .message
                    .content
                )

                if not raw_text:

                    raise ValueError(
                        "Groq returned an empty response."
                    )

                parsed = json.loads(
                    raw_text
                )

                if (
                    isinstance(
                        response_schema,
                        type,
                    )
                    and issubclass(
                        response_schema,
                        BaseModel,
                    )
                ):

                    return (
                        response_schema(
                            **parsed
                        )
                        .model_dump()
                    )

                return parsed

            except RateLimitError:

                if (
                    attempt
                    < max_retries - 1
                ):

                    sleep_time = (
                        (attempt + 1) * 10
                    )

                    print(
                        "[GROQ] Rate limit received. "
                        f"Waiting {sleep_time}s..."
                    )

                    time.sleep(
                        sleep_time
                    )

                    continue

                raise

            except Exception as exc:

                error_message = (
                    str(exc).lower()
                )

                # -------------------------------------------------
                # NEVER retry a request that is too large.
                # Retrying the same request will never make it
                # smaller.
                # -------------------------------------------------

                if (
                    "413" in error_message
                    or "request too large"
                    in error_message
                ):

                    raise

                is_rate_limit_error = (
                    "429"
                    in error_message
                    or "rate_limit"
                    in error_message
                    or "resource_exhausted"
                    in error_message
                    or "quota"
                    in error_message
                )

                if (
                    is_rate_limit_error
                    and attempt
                    < max_retries - 1
                ):

                    sleep_time = (
                        (attempt + 1) * 10
                    )

                    time.sleep(
                        sleep_time
                    )

                    continue

                raise