from .base import BaseAgent
from .schemas import ReviewerSchema


class ReviewerAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Code Reviewer Agent"
        )

    def review(
        self,
        code,
        requirements_analysis,
        chunk_label="Submitted Code",
    ):

        system_instruction = """
You are the Code Reviewer Agent in an
AI-powered software code review system.

Your job is to identify real, actionable problems
in the supplied code segment.

Look for:

- Security vulnerabilities
- Logic errors
- Functional bugs
- Requirement violations
- Poor error handling
- Unsafe input handling
- Authentication/authorization problems
- Data validation problems
- Dangerous coding practices
- Important edge cases
- Performance problems

Do not invent vulnerabilities.

Only report a finding when there is evidence
in the supplied code.

For every finding provide:
- title
- severity
- file_path if known
- line_number if known
- evidence
- explanation
- suggested_fix
- confidence

Return ONLY valid JSON.
"""

        prompt = f"""
Review this code segment.

CODE LOCATION:
{chunk_label}

REQUIREMENTS ANALYSIS:
{requirements_analysis}

CODE:
```text
{code}

Return:

{{
"findings": [
{{
"title": "",
"severity": "critical|high|medium|low|info",
"file_path": "",
"line_number": null,
"evidence": "",
"explanation": "",
"suggested_fix": "",
"confidence": 0.0,
"category": "security|logic|bug|error_handling|performance|style",
"message": "Clear explanation of the finding",
"line": null,
"suggestion": "Suggested fix or improvement"
}}
]
}}

If there are no legitimate findings, return:

{{
"findings": []
}}
"""

        return self.run(
            prompt=prompt,
            response_schema=ReviewerSchema,
            system_instruction=system_instruction,
        )