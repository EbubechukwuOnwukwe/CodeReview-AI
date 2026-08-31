from integrations.llm import LLMService


class BaseAgent:

    def __init__(self, name):
        self.name = name
        self.llm = LLMService()

    def run(
        self,
        prompt: str,
        response_schema,
        system_instruction: str | None = None,
    ):
        return self.llm.generate_structured(
            prompt=prompt,
            response_schema=response_schema,
            system_instruction=system_instruction,
        )