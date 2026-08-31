import json
import re
import os
import threading
import time

from dotenv import load_dotenv
from openai import (
    OpenAI,
    RateLimitError,
    BadRequestError,
)
from pydantic import BaseModel


load_dotenv()


class GroqService:

    MODEL = os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-120b",
    )

    BASE_URL = "https://api.groq.com/openai/v1"

    # =========================================================
    # GROQ RATE LIMIT SETTINGS
    # =========================================================

    TPM_LIMIT = int(
        os.getenv(
            "GROQ_TPM_LIMIT",
            "8000",
        )
    )

    # Keep safety margin below Groq's actual 8,000 TPM.
    SAFE_TPM_LIMIT = int(
        os.getenv(
            "GROQ_SAFE_TPM_LIMIT",
            "6500",
        )
    )

    # Approximate characters per token.
    CHARS_PER_TOKEN = 4

    # Maximum response size.
    MAX_OUTPUT_TOKENS = int(
        os.getenv(
            "GROQ_MAX_OUTPUT_TOKENS",
            "1200",
        )
    )

    # Reserve output capacity when calculating
    # whether the request fits inside the TPM bucket.
    RESERVED_OUTPUT_TOKENS = int(
        os.getenv(
            "GROQ_RESERVED_OUTPUT_TOKENS",
            "1200",
        )
    )

    # Shared by all GroqService instances inside
    # this Django process.
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
    def estimate_tokens(cls, text: str):

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
    # TPM RATE LIMITER
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

                    continue

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
                    f"Used: "
                    f"{used:,}/"
                    f"{cls.SAFE_TPM_LIMIT:,} tokens | "
                    f"Request: "
                    f"{required_tokens:,} tokens | "
                    f"Waiting: "
                    f"{wait_seconds:.0f}s"
                )

            time.sleep(
                wait_seconds
            )

    # =========================================================
    # GROQ RATE LIMIT ERROR PARSER
    # =========================================================

    @staticmethod
    def _extract_retry_seconds(error):

        message = str(error)

        # Example:
        # 12m50.688s

        match = re.search(
            r"(\d+)m([\d.]+)s",
            message,
            re.IGNORECASE,
        )

        if match:

            minutes = int(
                match.group(1)
            )

            seconds = float(
                match.group(2)
            )

            return (
                minutes * 60
                + seconds
            )

        # Example:
        # 50.688s

        match = re.search(
            r"([\d.]+)s",
            message,
            re.IGNORECASE,
        )

        if match:

            return float(
                match.group(1)
            )

        return None

    # =========================================================
    # JSON EXTRACTION
    # =========================================================

    @staticmethod
    def _extract_json(raw_text):

        if not raw_text:
            return None

        raw_text = raw_text.strip()

        # -----------------------------------------------------
        # First attempt:
        # The model followed instructions correctly.
        # -----------------------------------------------------

        try:

            return json.loads(
                raw_text
            )

        except json.JSONDecodeError:
            pass

        # -----------------------------------------------------
        # Remove markdown fences if the model ignored
        # our instruction.
        # -----------------------------------------------------

        cleaned = re.sub(
            r"^```(?:json)?\s*",
            "",
            raw_text,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"\s*```$",
            "",
            cleaned,
        ).strip()

        try:

            return json.loads(
                cleaned
            )

        except json.JSONDecodeError:
            pass

        # -----------------------------------------------------
        # Attempt to locate the JSON object.
        # -----------------------------------------------------

        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if (
            start != -1
            and end != -1
            and end > start
        ):

            candidate = (
                cleaned[
                    start:end + 1
                ]
            )

            try:

                return json.loads(
                    candidate
                )

            except json.JSONDecodeError:
                pass

        return None

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

        # -----------------------------------------------------
        # Base system instruction
        # -----------------------------------------------------

        default_system_instruction = (
            "You are a precise code analysis assistant."
        )

        # -----------------------------------------------------
        # Build a compact schema description.
        # -----------------------------------------------------

        schema_instruction = (
            self._build_schema_instruction(
                response_schema
            )
        )

        if system_instruction:

            final_system_instruction = (
                f"{default_system_instruction}\n\n"
                f"{system_instruction}\n\n"
                f"{schema_instruction}"
            )

        else:

            final_system_instruction = (
                f"{default_system_instruction}\n\n"
                f"{schema_instruction}"
            )

        # -----------------------------------------------------
        # User prompt
        # -----------------------------------------------------

        final_prompt = (
            f"{prompt}\n\n"
            "OUTPUT REQUIREMENTS:\n"
            "Return exactly ONE JSON object.\n"
            "Do not use markdown.\n"
            "Do not use ```json.\n"
            "Do not include any text before or after "
            "the JSON object.\n"
        )

        # -----------------------------------------------------
        # Estimate request size.
        # -----------------------------------------------------

        estimated_tokens = (
            self.estimate_request_tokens(
                final_prompt,
                final_system_instruction,
            )
        )

        print(
            f"[GROQ] Estimated request size: "
            f"{estimated_tokens:,} tokens"
        )

        # -----------------------------------------------------
        # Request cannot fit inside our safe TPM bucket.
        # -----------------------------------------------------

        if estimated_tokens > self.SAFE_TPM_LIMIT:

            raise ValueError(
                "This AI request is too large to send "
                "to Groq in one request. "
                "The analysis must be divided into "
                "smaller chunks."
            )

        # -----------------------------------------------------
        # Reserve TPM capacity.
        # -----------------------------------------------------

        self._wait_for_capacity(
            estimated_tokens
        )

        # =====================================================
        # REQUEST LOOP
        # =====================================================

        for attempt in range(
            max_retries
        ):

            try:

                print(
                    f"[GROQ] Sending request "
                    f"(~{estimated_tokens:,} tokens)"
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
                                "content": final_prompt,
                            },
                        ],

                        response_format={
                            "type": "json_schema",
                            "json_schema": {
                                "name": response_schema.__name__,
                                "schema": response_schema.model_json_schema(),
                                "strict": True,
                            },
                        },

                        max_tokens=self.MAX_OUTPUT_TOKENS,
                    )
                )

                choice = response.choices[0]

                print(
                    f"[GROQ] Finish reason: "
                    f"{choice.finish_reason}"
                )

                print(
                    f"[GROQ] Usage: "
                    f"{response.usage}"
                )

                raw_text = choice.message.content

                # -------------------------------------------------
                # Empty response
                # -------------------------------------------------

                if not raw_text:

                    raise ValueError(
                        "Groq returned an empty response."
                    )

                # -------------------------------------------------
                # Parse JSON
                # -------------------------------------------------

                parsed = (
                    self._extract_json(
                        raw_text
                    )
                )

                if parsed is None:

                    print(
                        "\n"
                        "[GROQ] Model returned "
                        "invalid JSON."
                    )

                    print(
                        "[GROQ] Raw response:"
                    )

                    print(
                        raw_text[:2000]
                    )

                    # Retry the generation.
                    if (
                        attempt
                        < max_retries - 1
                    ):

                        time.sleep(
                            2
                        )

                        continue

                    raise ValueError(
                        "The AI could not produce "
                        "valid JSON after multiple attempts."
                    )

                # -------------------------------------------------
                # Validate against Pydantic schema
                # -------------------------------------------------

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

                    validated = (
                        response_schema(
                            **parsed
                        )
                    )

                    return (
                        validated.model_dump()
                    )

                return parsed

            # =====================================================
            # RATE LIMIT
            # =====================================================

            except RateLimitError as exc:

                retry_seconds = (
                    self._extract_retry_seconds(
                        exc
                    )
                )

                if retry_seconds is not None:

                    wait_seconds = (
                        int(
                            retry_seconds
                        )
                        + 3
                    )

                else:

                    wait_seconds = (
                        (attempt + 1)
                        * 15
                    )

                if (
                    attempt
                    < max_retries - 1
                ):

                    print(
                        "\n"
                        "[GROQ] Rate limit received."
                    )

                    print(
                        "[GROQ] Waiting "
                        f"{wait_seconds}s..."
                    )

                    time.sleep(
                        wait_seconds
                    )

                    continue

                print(
                    "\n"
                    "[GROQ] Rate limit persisted."
                )

                raise

            # =====================================================
            # BAD REQUEST
            # =====================================================

            except BadRequestError as exc:

                print("\n" + "=" * 80)
                print("[GROQ] BAD REQUEST")
                print("=" * 80)

                print(
                    f"Error type: {type(exc).__name__}"
                )

                print(
                    f"Error: {exc}"
                )

                print("=" * 80 + "\n")

                error_message = str(exc).lower()

                # -------------------------------------------------
                # JSON validation error
                # -------------------------------------------------

                if (
                    "json_validate_failed"
                    in error_message
                ):

                    print(
                        "\n"
                        "[GROQ] Groq rejected "
                        "the generated JSON."
                    )

                    # Retry because the model may succeed
                    # on the next generation.

                    if (
                        attempt
                        < max_retries - 1
                    ):

                        print(
                            "[GROQ] Retrying "
                            "JSON generation..."
                        )

                        time.sleep(
                            2
                        )

                        continue

                    raise ValueError(
                        "The AI could not produce "
                        "a valid structured response "
                        "after multiple attempts."
                    ) from exc

                # -------------------------------------------------
                # Other 400 errors
                # -------------------------------------------------

                raise

            # =====================================================
            # OTHER ERRORS
            # =====================================================

            except Exception as exc:

                error_message = (
                    str(exc).lower()
                )

                # -------------------------------------------------
                # Never retry oversized requests.
                # -------------------------------------------------

                if (
                    "413"
                    in error_message
                    or "request too large"
                    in error_message
                ):

                    raise

                # -------------------------------------------------
                # Handle rate-limit-like errors that weren't
                # represented by RateLimitError.
                # -------------------------------------------------

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
                        (attempt + 1)
                        * 15
                    )

                    print(
                        "[GROQ] Rate-limit-like "
                        f"error. Waiting "
                        f"{sleep_time}s..."
                    )

                    time.sleep(
                        sleep_time
                    )

                    continue

                raise

    # =========================================================
    # SCHEMA INSTRUCTION
    # =========================================================

    @staticmethod
    def _build_schema_instruction(
        response_schema
    ):

        try:

            schema = (
                response_schema
                .model_json_schema()
            )

            # Keep schema compact.
            schema_json = json.dumps(
                schema,
                separators=(
                    ",",
                    ":",
                ),
            )

            return (
                "The response MUST be valid JSON "
                "matching this schema:\n"
                f"{schema_json}"
            )

        except Exception:

            return (
                "Return valid JSON matching "
                "the requested response schema."
            )