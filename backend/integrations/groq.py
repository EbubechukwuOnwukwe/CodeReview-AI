import json
import os
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

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url=self.BASE_URL,
        )

    def generate_structured(
        self,
        prompt: str,
        response_schema,
        system_instruction: str | None = None,
        max_retries: int = 4,
    ):
        """
        Send a prompt to Groq and validate the
        returned JSON against the supplied Pydantic schema.
        """

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

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": final_system_instruction,
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

                raw_text = (
                    response.choices[0]
                    .message
                    .content
                )

                if not raw_text:
                    raise ValueError(
                        "Groq returned an empty response."
                    )

                parsed = json.loads(raw_text)

                if (
                    isinstance(response_schema, type)
                    and issubclass(
                        response_schema,
                        BaseModel,
                    )
                ):
                    return response_schema(
                        **parsed
                    ).model_dump()

                return parsed

            except RateLimitError:
                if attempt < max_retries - 1:
                    sleep_time = (
                        (attempt + 1) * 7
                    )

                    time.sleep(sleep_time)
                    continue

                raise

            except Exception as exc:
                err_str = str(exc)

                is_rate_limit_error = (
                    "429" in err_str
                    or "rate_limit"
                    in err_str.lower()
                    or "resource_exhausted"
                    in err_str.lower()
                    or "quota"
                    in err_str.lower()
                )

                if (
                    is_rate_limit_error
                    and attempt < max_retries - 1
                ):
                    sleep_time = (
                        (attempt + 1) * 7
                    )

                    time.sleep(sleep_time)
                    continue

                raise