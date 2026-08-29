from .base import BaseAgent


class VerificationAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Verification Agent"
        )

    def verify(
        self,
        code,
        requirements,
        finding,
    ):
        system_instruction = """
You are the Verification Agent for an
AI-powered code review system.

Your job is to independently verify a finding
produced by another code-review agent.

Do not automatically agree with the reviewer.

Determine:

1. Whether the finding is actually present.
2. Whether the supplied evidence supports it.
3. Whether the severity is appropriate.
4. Whether the suggested fix addresses the issue.

Reject findings that are unsupported,
incorrect, or based on assumptions.

Return ONLY valid JSON.
"""

        prompt = f"""
Verify this code-review finding.

REQUIREMENTS:
{requirements}

CODE:
```text
{code}
```

FINDING:
{finding}

Return:

{{
"verification_status": "verified|rejected",
"confidence": 0.0,
"reason": "",
"corrected_severity": "critical|high|medium|low|info",
"recommendation": ""
}}
"""

        return self.run(
            prompt=prompt,
             response_schema=RequirementsSchema,
        )
