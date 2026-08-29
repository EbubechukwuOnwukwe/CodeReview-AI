import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


class GeminiService:
    MODEL = "gemini-2.5-flash"

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=api_key
        )

    def generate_structured(
        self,
        prompt: str,
        response_schema,
    ):
        response = self.client.models.generate_content(
            model=self.MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
            ),
        )

        if response.parsed is not None:
            return response.parsed

        raise ValueError(
            "Gemini returned an invalid structured response."
        )