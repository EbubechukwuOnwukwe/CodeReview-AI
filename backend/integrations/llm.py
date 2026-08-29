from .gemini import GeminiService


class LLMService:
    """
    Application-level interface for interacting
    with the language model.
    """

    def __init__(self):
        self.provider = GeminiService()

    def generate_structured(
        self,
        prompt: str,
        response_schema,
    ):
        return self.provider.generate_structured(
            prompt=prompt,
            response_schema=response_schema,
        )