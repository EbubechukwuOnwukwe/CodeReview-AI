from .groq import GroqService


class LLMService:
    """
    Application-level interface for interacting
    with the language model.
    """

    def __init__(self):
        self.provider = GroqService()

    def generate_structured(
        self,
        prompt: str,
        response_schema,
        system_instruction: str | None = None,
    ):
        return self.provider.generate_structured(
            prompt=prompt,
            response_schema=response_schema,
            system_instruction=system_instruction,
        )