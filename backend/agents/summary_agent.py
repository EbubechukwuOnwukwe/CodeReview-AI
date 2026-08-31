import json

from .base import BaseAgent
from .schemas import SummarySchema


class SummaryAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            name="Summary Agent"
        )

    def summarize(
        self,
        requirements_analysis,
        verified_findings,
    ):

        system_instruction = """
You are the Summary Agent in an AI-powered
code review system.

Create a concise, useful final code review report.

Only use verified findings.

Do not invent additional issues.

The report should help a developer understand:
- overall code quality
- the most important problems
- severity distribution
- what should be fixed first

Return ONLY valid JSON.
"""

        schema_example = {
            "overall_summary": (
                "Concise assessment of the code."
            ),

            "risk_level": (
                "critical|high|medium|low"
            ),

            "priority_actions": [
                "Action that should be addressed first"
            ],

            "severity_summary": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0,
            },

            "recommendations": [
                {
                    "id": 1,
                    "action": (
                        "Specific recommended improvement"
                    ),
                    "priority": (
                        "high|medium|low"
                    ),
                    "reason": (
                        "Why this improvement matters"
                    ),
                }
            ],
        }

        schema_json = json.dumps(
            schema_example,
            indent=2,
        )

        prompt = f"""
Create the final code review report.

REQUIREMENTS ANALYSIS:
{requirements_analysis}

VERIFIED FINDINGS:
{verified_findings}

Return ONLY valid JSON matching this structure:

{schema_json}
"""

        return self.run(
            prompt=prompt,
            response_schema=SummarySchema,
            system_instruction=system_instruction,
        )