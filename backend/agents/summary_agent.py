from agents.base import BaseAgent
from agents.schemas import SummarySchema


class SummaryAgent(BaseAgent):

    def __init__(self):
        super().__init__("summary")

    """
    Produces the final human-readable summary of a code review.

    Large reviews are processed in batches so that the final
    summary request never becomes too large for the LLM.
    """

    MAX_FINDINGS_PER_BATCH = 4

    def summarize(
        self,
        requirements_analysis,
        verified_findings,
    ):
        """
        Produce the final human-readable summary.

        Large reviews are processed in small batches so that
        no single Groq request becomes too large.
        """

        if not verified_findings:
            return self._empty_summary()

        batches = self._create_batches(
            verified_findings,
            self.MAX_FINDINGS_PER_BATCH,
        )

        print(
            f"[SUMMARY] Processing "
            f"{len(verified_findings)} verified finding(s) "
            f"in {len(batches)} batch(es)"
        )

        batch_summaries = []

        for index, batch in enumerate(
            batches,
            start=1,
        ):

            print(
                f"[SUMMARY] Processing batch "
                f"{index}/{len(batches)}..."
            )

            batch_result = self._summarize_batch(
                requirements_analysis=requirements_analysis,
                verified_findings=batch,
            )

            batch_summaries.append(
                batch_result
            )

        # Only one request was necessary.
        if len(batch_summaries) == 1:
            return batch_summaries[0]

        print(
            f"[SUMMARY] Combining "
            f"{len(batch_summaries)} batch summaries..."
        )

        return self._combine_summaries(
            requirements_analysis=requirements_analysis,
            summaries=batch_summaries,
        )

    def _summarize_batch(
        self,
        requirements_analysis,
        verified_findings,
    ):
        findings_text = self._format_reviewer_results(
            verified_findings
        )

        system_instruction = """
    You are the final code review summary agent.

    Analyze the supplied VERIFIED code-review findings.

    Do not invent findings.

    Only discuss issues supported by the supplied findings.

    Return valid JSON matching the supplied schema.

    Keep the response concise.
    """

        prompt = f"""
    PROJECT REQUIREMENTS:

    {requirements_analysis}


    VERIFIED REVIEW FINDINGS:

    {findings_text}


    TASK:

    Create a concise summary of these verified findings.

    Cover:

    1. Overall code quality
    2. Most important issues
    3. Security concerns
    4. Performance concerns
    5. Maintainability concerns
    6. Recommended improvements

    Only include information supported by the findings.
    Prioritize important issues.
    Do not repeat the same issue multiple times.
    """

        return self.run(
            prompt=prompt,
            response_schema=SummarySchema,
            system_instruction=system_instruction,
        )

    def _combine_summaries(
        self,
        requirements_analysis,
        summaries,
    ):
        """
        Combine intermediate summaries in small groups
        so the final request never becomes unnecessarily large.
        """

        if not summaries:
            return self._empty_summary()

        if len(summaries) == 1:
            return summaries[0]

        batches = self._create_batches(
            summaries,
            2,
        )

        combined = []

        for index, batch in enumerate(
            batches,
            start=1,
        ):

            print(
                f"[SUMMARY] Combining summary batch "
                f"{index}/{len(batches)}..."
            )

            summaries_text = self._format_summaries(
                batch
            )

            system_instruction = """
    You are a code review report editor.

    Combine the supplied intermediate summaries.

    Do not invent issues.

    Remove duplicates.

    Preserve important security, correctness,
    performance, and maintainability issues.

    Return valid JSON matching the supplied schema.

    Keep the response concise.
    """

            prompt = f"""
    PROJECT REQUIREMENTS:

    {requirements_analysis}


    INTERMEDIATE SUMMARIES:

    {summaries_text}


    TASK:

    Combine these summaries into one concise
    code review summary.

    Prioritize:

    1. Security
    2. Functional correctness
    3. Performance
    4. Maintainability
    5. Code quality

    Only include information supported by the summaries.
    """

            result = self.run(
                prompt=prompt,
                response_schema=SummarySchema,
                system_instruction=system_instruction,
            )

            combined.append(
                result
            )

        # Recursively combine until only one remains.
        if len(combined) == 1:
            return combined[0]

        return self._combine_summaries(
            requirements_analysis=requirements_analysis,
            summaries=combined,
        )

    @staticmethod
    def _create_batches(items, batch_size):
        return [
            items[index:index + batch_size]
            for index in range(
                0,
                len(items),
                batch_size,
            )
        ]

@staticmethod
def _format_reviewer_results(results):

    formatted = []

    for index, result in enumerate(
        results,
        start=1,
    ):

        if hasattr(result, "model_dump"):
            data = result.model_dump()

        elif isinstance(result, dict):
            data = result

        else:
            data = {
                "result": str(result)
            }

        compact = {
            "title": data.get(
                "title"
            ) or data.get(
                "message"
            ),

            "severity": data.get(
                "severity"
            ),

            "file_path": data.get(
                "file_path"
            ),

            "line_number": data.get(
                "line_number"
            ) or data.get(
                "line"
            ),

            "evidence": data.get(
                "evidence"
            ),

            "explanation": data.get(
                "explanation"
            ),

            "suggested_fix": data.get(
                "suggested_fix"
            ) or data.get(
                "suggestion"
            ),

            "confidence": data.get(
                "confidence"
            ),

            "verification_status": data.get(
                "verification_status"
            ) or (
                data.get(
                    "verification",
                    {}
                ).get(
                    "verification_status"
                )
                if isinstance(
                    data.get("verification"),
                    dict,
                )
                else None
            ),

            "verification_reason": data.get(
                "verification_reason"
            ) or (
                data.get(
                    "verification",
                    {}
                ).get(
                    "reason"
                )
                if isinstance(
                    data.get("verification"),
                    dict,
                )
                else None
            ),
        }

        formatted.append(
            f"""
--- VERIFIED FINDING {index} ---

Title: {compact["title"]}
Severity: {compact["severity"]}
File: {compact["file_path"]}
Line: {compact["line_number"]}

Evidence:
{compact["evidence"]}

Explanation:
{compact["explanation"]}

Suggested Fix:
{compact["suggested_fix"]}

Confidence:
{compact["confidence"]}

Verification:
{compact["verification_status"]}

Verification Reason:
{compact["verification_reason"]}
"""
        )

    return "\n".join(formatted)

    @staticmethod
    def _format_summaries(summaries):

        formatted = []

        for index, summary in enumerate(
            summaries,
            start=1,
        ):

            if hasattr(summary, "model_dump"):
                data = summary.model_dump()

            elif isinstance(summary, dict):
                data = summary

            else:
                data = {
                    "summary": str(summary)
                }

            formatted.append(
                f"""
--- INTERMEDIATE SUMMARY {index} ---

{data}
"""
            )

        return "\n".join(formatted)

    @staticmethod
    def _empty_summary():

        return SummarySchema(
            summary="No review findings were generated.",
            recommendations=[],
        )