from django.utils import timezone

from reviews.models import (
    AgentTrajectory,
    Finding,
    Review,
)

from .requirements_agent import RequirementsAgent
from .reviewer_agent import ReviewerAgent
from .verifier_agent import VerificationAgent
from .summary_agent import SummaryAgent
from .code_chunker import CodeChunker


class ReviewOrchestrator:

    def __init__(self):

        self.requirements_agent = (
            RequirementsAgent()
        )

        self.reviewer_agent = (
            ReviewerAgent()
        )

        self.verifier_agent = (
            VerificationAgent()
        )

        self.summary_agent = (
            SummaryAgent()
        )

        self.chunker = CodeChunker()

    # =========================================================
    # MAIN PIPELINE
    # =========================================================

    def run(self, review_id):

        review = Review.objects.get(
            id=review_id
        )

        # Clear previous analysis when retrying.
        review.trajectories.all().delete()
        review.findings.all().delete()

        review.status = Review.Status.RUNNING
        review.started_at = timezone.now()

        review.save(
            update_fields=[
                "status",
                "started_at",
            ]
        )

        try:

            # -------------------------------------------------
            # STEP 0
            # Split the submitted code.
            # -------------------------------------------------

            chunks = self.chunker.chunk(
                review.code
            )

            if not chunks:

                raise ValueError(
                    "No reviewable code was found."
                )

            print(
                "\n"
                + "=" * 80
            )

            print(
                f"CODE REVIEW: "
                f"{len(chunks)} analysis chunk(s)"
            )

            print(
                "=" * 80
            )

            for chunk in chunks:

                print(
                    f"Chunk {chunk.index}: "
                    f"{len(chunk.content):,} characters "
                    f"| {chunk.label}"
                )

            print(
                "=" * 80
                + "\n"
            )

            # -------------------------------------------------
            # STEP 1
            # Requirements analysis
            # -------------------------------------------------

            requirements_analysis = (
                self._run_requirements_agent(
                    review,
                    chunks,
                )
            )

            # -------------------------------------------------
            # STEP 2
            # Review each chunk
            # -------------------------------------------------

            reviewer_result = (
                self._run_reviewer_agent(
                    review,
                    chunks,
                    requirements_analysis,
                )
            )

            # -------------------------------------------------
            # STEP 3+
            # Verify each finding using ONLY the relevant
            # chunk rather than the entire repository.
            # -------------------------------------------------

            verified_findings, next_step = (
                self._run_verification(
                    review,
                    chunks,
                    requirements_analysis,
                    reviewer_result,
                    start_step=3,
                )
            )

            # -------------------------------------------------
            # FINAL STEP
            # Summary receives only compact analysis results.
            # -------------------------------------------------

            final_report = (
                self._run_summary_agent(
                    review,
                    requirements_analysis,
                    verified_findings,
                    step=next_step,
                )
            )

            review.final_report = final_report
            review.status = Review.Status.COMPLETED
            review.completed_at = timezone.now()
            review.error_message = None

            review.save(
                update_fields=[
                    "final_report",
                    "status",
                    "completed_at",
                    "error_message",
                ]
            )

            return final_report

        except Exception:

            review.status = Review.Status.FAILED

            review.error_message = (
                "We couldn't complete this code review right now. "
                "Please try again in a moment."
            )

            review.completed_at = timezone.now()

            review.save(
                update_fields=[
                    "status",
                    "error_message",
                    "completed_at",
                ]
            )

            raise

    # =========================================================
    # REQUIREMENTS AGENT
    # =========================================================

    def _run_requirements_agent(
        self,
        review,
        chunks,
    ):

        trajectory = AgentTrajectory.objects.create(
            review=review,
            agent_name="Requirements Agent",
            step=1,
            input_data={
                "chunk_count": len(chunks),
                "requirements": review.requirements,
            },
            output_data={},
            status="started",
        )

        try:

            # Requirements are project-level.
            # Analyze them ONCE instead of once per code chunk.
            result = self.requirements_agent.analyze(
                code="",
                requirements=review.requirements,
                chunk_label="Project Requirements",
            )

            trajectory.output_data = result
            trajectory.status = "completed"
            trajectory.completed_at = timezone.now()

            trajectory.save()

            return result

        except Exception:

            trajectory.status = "failed"

            trajectory.error_message = (
                "The Requirements Agent could not "
                "complete its analysis."
            )

            trajectory.completed_at = timezone.now()

            trajectory.save()

            raise
    # =========================================================
    # REVIEWER AGENT
    # =========================================================

    def _run_reviewer_agent(
        self,
        review,
        chunks,
        requirements_analysis,
    ):

        trajectory = AgentTrajectory.objects.create(
            review=review,
            agent_name="Code Reviewer Agent",
            step=2,
            input_data={
                "chunk_count": len(chunks),
                "requirements_analysis": (
                    requirements_analysis
                ),
            },
            output_data={},
            status="started",
        )

        try:

            all_findings = []

            for chunk in chunks:

                print(
                    f"[REVIEWER] "
                    f"Analyzing chunk "
                    f"{chunk.index}/{len(chunks)}..."
                )

                result = (
                    self.reviewer_agent.review(
                        code=chunk.content,
                        requirements_analysis=(
                            requirements_analysis
                        ),
                        chunk_label=chunk.label,
                    )
                )

                findings = result.get(
                    "findings",
                    [],
                )

                # Store which chunk produced the finding.
                for finding in findings:

                    finding["_chunk_index"] = (
                        chunk.index
                    )

                    finding["_chunk_content"] = (
                        chunk.content
                    )

                    finding["_chunk_label"] = (
                        chunk.label
                    )

                all_findings.extend(
                    findings
                )

            result = {
                "findings": all_findings
            }

            trajectory.output_data = result
            trajectory.status = "completed"
            trajectory.completed_at = timezone.now()

            trajectory.save()

            return result

        except Exception:

            trajectory.status = "failed"

            trajectory.error_message = (
                "The Code Reviewer Agent could not "
                "complete its analysis."
            )

            trajectory.completed_at = timezone.now()

            trajectory.save()

            raise

    # =========================================================
    # VERIFICATION
    # =========================================================

    def _run_verification(
        self,
        review,
        chunks,
        requirements_analysis,
        reviewer_result,
        start_step=3,
    ):

        verified_findings = []

        findings = reviewer_result.get(
            "findings",
            [],
        )

        next_step = start_step

        for finding_data in findings:

            trajectory = AgentTrajectory.objects.create(
                review=review,
                agent_name="Verification Agent",
                step=next_step,
                input_data={
                    "finding": finding_data,
                },
                output_data={},
                status="started",
            )

            next_step += 1

            try:

                chunk_content = (
                    finding_data.get(
                        "_chunk_content"
                    )
                    or review.code
                )

                chunk_label = (
                    finding_data.get(
                        "_chunk_label"
                    )
                    or "Relevant Code"
                )

                # Remove internal fields before sending
                # the finding to the AI.
                clean_finding = {
                    key: value
                    for key, value
                    in finding_data.items()
                    if not key.startswith("_")
                }

                verification = (
                    self.verifier_agent.verify(
                        code=chunk_content,
                        requirements=(
                            requirements_analysis
                        ),
                        finding=clean_finding,
                        chunk_label=chunk_label,
                    )
                )

                trajectory.output_data = verification
                trajectory.status = "completed"
                trajectory.completed_at = timezone.now()

                trajectory.save()

                # -------------------------------------------------
                # Extract finding data safely.
                # -------------------------------------------------

                finding_title = (
                    finding_data.get("title")
                    or "Code Finding"
                )

                finding_title = str(
                    finding_title
                )

                if len(finding_title) > 255:

                    finding_title = (
                        finding_title[:252]
                        + "..."
                    )

                severity = (
                    verification.get(
                        "corrected_severity"
                    )
                    or finding_data.get(
                        "severity"
                    )
                    or "medium"
                )

                evidence = (
                    finding_data.get(
                        "evidence"
                    )
                    or finding_data.get(
                        "message"
                    )
                    or ""
                )

                explanation = (
                    finding_data.get(
                        "explanation"
                    )
                    or ""
                )

                suggested_fix = (
                    finding_data.get(
                        "suggested_fix"
                    )
                    or ""
                )

                file_path = (
                    finding_data.get(
                        "file_path"
                    )
                    or ""
                )

                line_number = (
                    finding_data.get(
                        "line_number"
                    )
                )

                confidence = (
                    verification.get(
                        "confidence"
                    )
                    if verification.get(
                        "confidence"
                    ) is not None
                    else finding_data.get(
                        "confidence"
                    )
                )

                verification_status = (
                    verification.get(
                        "verification_status"
                    )
                    or "rejected"
                )

                verification_reason = (
                    verification.get(
                        "reason"
                    )
                    or ""
                )

                finding = Finding.objects.create(
                    review=review,
                    title=finding_title,
                    severity=severity,
                    file_path=file_path,
                    line_number=line_number,
                    evidence=str(evidence),
                    explanation=str(explanation),
                    suggested_fix=str(
                        suggested_fix
                    ),
                    confidence=confidence,
                    verification_status=(
                        verification_status
                    ),
                    verification_reason=str(
                        verification_reason
                    ),
                )

                if (
                    verification_status
                    == "verified"
                ):

                    verified_findings.append(
                        {
                            "id": finding.id,
                            **{
                                key: value
                                for key, value
                                in finding_data.items()
                                if not key.startswith("_")
                            },
                            "verification": (
                                verification
                            ),
                        }
                    )

            except Exception:

                trajectory.status = "failed"

                trajectory.error_message = (
                    "The Verification Agent could "
                    "not complete its analysis."
                )

                trajectory.completed_at = (
                    timezone.now()
                )

                trajectory.save()

                raise

        return (
            verified_findings,
            next_step,
        )

    # =========================================================
    # SUMMARY
    # =========================================================

    def _run_summary_agent(
        self,
        review,
        requirements_analysis,
        verified_findings,
        step,
    ):

        trajectory = AgentTrajectory.objects.create(
            review=review,
            agent_name="Summary Agent",
            step=step,
            input_data={
                "requirements_analysis": (
                    requirements_analysis
                ),
                "verified_findings": (
                    verified_findings
                ),
            },
            output_data={},
            status="started",
        )

        try:

            result = (
                self.summary_agent.summarize(
                    requirements_analysis=(
                        requirements_analysis
                    ),
                    verified_findings=(
                        verified_findings
                    ),
                )
            )

            trajectory.output_data = result
            trajectory.status = "completed"
            trajectory.completed_at = timezone.now()

            trajectory.save()

            return result

        except Exception:

            trajectory.status = "failed"

            trajectory.error_message = (
                "The Summary Agent could not "
                "complete its analysis."
            )

            trajectory.completed_at = timezone.now()

            trajectory.save()

            raise

    # =========================================================
    # REQUIREMENTS MERGING
    # =========================================================

    @staticmethod
    def _merge_requirements(
        analyses
    ):

        if not analyses:

            return {
                "summary": "",
                "functional_requirements": [],
                "security_requirements": [],
                "constraints": [],
                "acceptance_criteria": [],
            }

        summaries = []
        functional = []
        security = []
        constraints = []
        acceptance = []

        for analysis in analyses:

            summary = analysis.get(
                "summary"
            )

            if summary:
                summaries.append(
                    str(summary)
                )

            functional.extend(
                analysis.get(
                    "functional_requirements",
                    [],
                )
                or []
            )

            security.extend(
                analysis.get(
                    "security_requirements",
                    [],
                )
                or []
            )

            constraints.extend(
                analysis.get(
                    "constraints",
                    [],
                )
                or []
            )

            acceptance.extend(
                analysis.get(
                    "acceptance_criteria",
                    [],
                )
                or []
            )

        return {
            "summary": " ".join(
                dict.fromkeys(
                    summaries
                )
            ),

            "functional_requirements": (
                ReviewOrchestrator
                ._deduplicate_list(
                    functional
                )
            ),

            "security_requirements": (
                ReviewOrchestrator
                ._deduplicate_dicts(
                    security
                )
            ),

            "constraints": (
                ReviewOrchestrator
                ._deduplicate_list(
                    constraints
                )
            ),

            "acceptance_criteria": (
                ReviewOrchestrator
                ._deduplicate_list(
                    acceptance
                )
            ),
        }

    @staticmethod
    def _deduplicate_list(
        values
    ):

        result = []
        seen = set()

        for value in values:

            value = str(value).strip()

            if not value:
                continue

            key = value.lower()

            if key in seen:
                continue

            seen.add(key)

            result.append(value)

        return result

    @staticmethod
    def _deduplicate_dicts(
        values
    ):

        result = []
        seen = set()

        for value in values:

            if not isinstance(
                value,
                dict,
            ):
                continue

            key = str(
                value
            ).lower()

            if key in seen:
                continue

            seen.add(key)

            result.append(value)

        return result