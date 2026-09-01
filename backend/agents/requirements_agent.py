from .base import BaseAgent
from .schemas import RequirementsSchema


class RequirementsAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Requirements Agent"
        )

    def analyze(
        self,
        code,
        requirements,
        chunk_label="Project Requirements",
    ):

        system_instruction = """
    You are the Requirements Analysis Agent
    for an AI-powered code review system.

    Your job is to analyze the USER REQUIREMENTS
    and convert them into a concise structured specification
    that another AI agent can use when reviewing code.

    Do NOT review the implementation.

    Do NOT invent requirements.

    Extract only requirements explicitly supported
    by the user's requirements.

    If the user did not provide a particular type of
    requirement, return an empty array for that field.

    Return ONLY valid JSON matching the supplied schema.
    """

        prompt = f"""
    Analyze the following software requirements.

    USER REQUIREMENTS:
    {requirements}

    Extract:

    1. Functional requirements
    2. Security requirements
    3. Constraints
    4. Acceptance criteria

    If a category is not specified by the user,
    return an empty array.

    Keep each item concise.

    Return the required JSON object.
    """

        return self.run(
            prompt=prompt,
            response_schema=RequirementsSchema,
            system_instruction=system_instruction,
            max_retries=2,
        )