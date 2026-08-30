from .base import BaseAgent
from .schemas import RequirementsSchema

class RequirementsAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Requirements Agent"
        )

    def analyze(self, code, requirements):
        system_instruction = """
You are the Requirements Analysis Agent
for an AI-powered code review system.

Your job is to analyze the user's requirements
and determine what the submitted code is expected
to accomplish.

Do not review the code for bugs yet.

Extract:
1. Functional requirements
2. Security requirements
3. Input/output expectations
4. Important constraints
5. Acceptance criteria

Return ONLY valid JSON.
"""

        prompt = f"""
Analyze the following software requirements.

USER REQUIREMENTS:
{requirements}

SUBMITTED CODE:
```text
{code}
```

Return this JSON structure:

{{
"summary": "Short description of what the code is expected to do.",
"functional_requirements": [],
"security_requirements": [],
"constraints": [],
"acceptance_criteria": []
}}
"""

        return self.run(
            prompt=prompt,
             response_schema=RequirementsSchema,
        )
