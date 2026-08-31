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

Return JSON matching this structure:

{{
    "summary": "Short description of what the code is expected to accomplish.",

    "functional_requirements": [
        "A plain-language functional requirement"
    ],

    "security_requirements": [
        {{
            "severity": "critical|high|medium|low|info",
            "vulnerability": "Security requirement or security concern",
            "evidence": "Relevant evidence from the submitted code"
        }}
    ],

    "constraints": [
        "Important technical or business constraint"
    ],

    "acceptance_criteria": [
        "Condition that must be satisfied"
    ]
}}
"""

        return self.run(
            prompt=prompt,
            response_schema=RequirementsSchema,
            system_instruction=system_instruction,
)
