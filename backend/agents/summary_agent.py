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
    MAX_SUMMARIES_PER_BATCH = 2

    # =========================================================
    # MAIN SUMMARY
    # =========================================================

    def summarize(
        self,
        requirements_analysis,
        verified_findings,
    ):
        """
        Produce the final human-readable summary.

        Verified findings are processed in small batches so that
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

    # =========================================================
    # SUMMARIZE FINDING BATCH
    # =========================================================

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

Analyze ONLY the supplied VERIFIED code-review findings.

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

Create a concise final summary of these verified findings.

Focus on:

- Overall code quality
- Most important issues
- Security concerns
- Performance concerns
- Maintainability concerns
- Recommended improvements

Use only information supported by the findings.

Prioritize the most severe and important issues.

Do not repeat the same issue.
"""

        return self.run(
            prompt=prompt,
            response_schema=SummarySchema,
            system_instruction=system_instruction,
        )

    # =========================================================
    # COMBINE SUMMARIES
    # =========================================================

    def _combine_summaries(
        self,
        requirements_analysis,
        summaries,
    ):
        """
        Combine intermediate summaries in small groups.
        """

        if not summaries:
            return self._empty_summary()

        if len(summaries) == 1:
            return summaries[0]

        batches = self._create_batches(
            summaries,
            self.MAX_SUMMARIES_PER_BATCH,
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

Remove duplicate findings.

Preserve important security, correctness,
performance, maintainability, and code-quality issues.

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
Do not repeat the same issue.
"""

            result = self.run(
                prompt=prompt,
                response_schema=SummarySchema,
                system_instruction=system_instruction,
            )

            combined.append(result)

        # Recursively combine until only one remains.
        if len(combined) == 1:
            return combined[0]

        return self._combine_summaries(
            requirements_analysis=requirements_analysis,
            summaries=combined,
        )

    # =========================================================
    # BATCHING
    # =========================================================

    @staticmethod
    def _create_batches(
        items,
        batch_size,
    ):
        return [
            items[index:index + batch_size]
            for index in range(
                0,
                len(items),
                batch_size,
            )
        ]

    # =========================================================
    # FORMAT VERIFIED FINDINGS
    # =========================================================

    @staticmethod
    def _format_reviewer_results(
        results
    ):

        formatted = []

        for index, result in enumerate(
            results,
            start=1,
        ):

            if hasattr(
                result,
                "model_dump",
            ):

                data = result.model_dump()

            elif isinstance(
                result,
                dict,
            ):

                data = result

            else:

                data = {
                    "result": str(result)
                }

            verification = data.get(
                "verification",
                {},
            )

            if not isinstance(
                verification,
                dict,
            ):

                verification = {}

            title = (
                data.get("title")
                or data.get("message")
                or "Code Finding"
            )

            severity = (
                data.get("severity")
                or "medium"
            )

            file_path = (
                data.get("file_path")
                or "Unknown"
            )

            line_number = (
                data.get("line_number")
                if data.get("line_number") is not None
                else data.get("line")
            )

            evidence = (
                data.get("evidence")
                or ""
            )

            explanation = (
                data.get("explanation")
                or data.get("message")
                or ""
            )

            suggested_fix = (
                data.get("suggested_fix")
                or data.get("suggestion")
                or ""
            )

            confidence = (
                data.get("confidence")
            )

            verification_status = (
                data.get("verification_status")
                or verification.get(
                    "verification_status"
                )
                or "verified"
            )

            verification_reason = (
                data.get("verification_reason")
                or verification.get("reason")
                or ""
            )

            formatted.append(
                f"""
--- VERIFIED FINDING {index} ---

Title: {title}
Severity: {severity}
File: {file_path}
Line: {line_number}

Evidence:
{evidence}

Explanation:
{explanation}

Suggested Fix:
{suggested_fix}

Confidence:
{confidence}

Verification Status:
{verification_status}

Verification Reason:
{verification_reason}
"""
            )

        return "\n".join(formatted)

    # =========================================================
    # FORMAT SUMMARIES
    # =========================================================

    @staticmethod
    def _format_summaries(
        summaries
    ):

        formatted = []

        for index, summary in enumerate(
            summaries,
            start=1,
        ):

            if hasattr(
                summary,
                "model_dump",
            ):

                data = summary.model_dump()

            elif isinstance(
                summary,
                dict,
            ):

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

    # =========================================================
    # EMPTY SUMMARY
    # =========================================================

    @staticmethod
    def _empty_summary():

        return SummarySchema(
            overall_summary=(
                "No verified review findings "
                "were generated."
            ),
            risk_level="low",
            priority_actions=[],
            severity_summary={
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0,
            },
            recommendations=[],
        )