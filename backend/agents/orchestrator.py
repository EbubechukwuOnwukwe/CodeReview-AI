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


class ReviewOrchestrator:

    def __init__(self):
        self.requirements_agent = RequirementsAgent()
        self.reviewer_agent = ReviewerAgent()
        self.verifier_agent = VerificationAgent()
        self.summary_agent = SummaryAgent()

    def run(self, review_id):
        review = Review.objects.get(
            id=review_id
        )

        # Clear previous trajectories and findings if retrying/re-running
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
            requirements_analysis = (
                self._run_requirements_agent(review)
            )

            reviewer_result = (
                self._run_reviewer_agent(
                    review,
                    requirements_analysis,
                )
            )

            verified_findings, next_step = (
                self._run_verification(
                    review,
                    requirements_analysis,
                    reviewer_result,
                    start_step=3,
                )
            )

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
            review.save(
                update_fields=[
                    "final_report",
                    "status",
                    "completed_at",
                ]
            )

            return final_report

        except Exception as exc:
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


    def _run_requirements_agent(self, review):
        step = 1

        trajectory = AgentTrajectory.objects.create(
            review=review,
            agent_name="Requirements Agent",
            step=step,
            input_data={
                "code": review.code,
                "requirements": review.requirements,
            },
            output_data={},
            status="started",
        )

        try:
            result = self.requirements_agent.analyze(
                code=review.code,
                requirements=review.requirements,
            )

            trajectory.output_data = result
            trajectory.status = "completed"
            trajectory.completed_at = timezone.now()
            trajectory.save()

            return result

        except Exception as exc:
            trajectory.status = "failed"
            trajectory.error_message = (
                "This agent could not complete its analysis."
            )
            trajectory.completed_at = timezone.now()
            trajectory.save()

            raise

    def _run_reviewer_agent(
        self,
        review,
        requirements_analysis,
    ):
        step = 2

        trajectory = AgentTrajectory.objects.create(
            review=review,
            agent_name="Code Reviewer Agent",
            step=step,
            input_data={
                "code": review.code,
                "requirements_analysis": (
                    requirements_analysis
                ),
            },
            output_data={},
            status="started",
        )

        try:
            result = self.reviewer_agent.review(
                code=review.code,
                requirements_analysis=(
                    requirements_analysis
                ),
            )

            trajectory.output_data = result
            trajectory.status = "completed"
            trajectory.completed_at = timezone.now()
            trajectory.save()

            return result

        except Exception as exc:
            trajectory.status = "failed"

            trajectory.error_message = (
                "The Code Reviewer Agent could not complete its analysis."
            )

            trajectory.completed_at = timezone.now()
            trajectory.save()

            raise

    def _run_verification(
        self,
        review,
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
                verification = self.verifier_agent.verify(
                    code=review.code,
                    requirements=requirements_analysis,
                    finding=finding_data,
                )

                trajectory.output_data = verification
                trajectory.status = "completed"
                trajectory.completed_at = timezone.now()
                trajectory.save()

                # -------------------------------------------------
                # Safely extract finding values.
                # AI responses can contain null values.
                # -------------------------------------------------

                finding_title = (
                    finding_data.get("message")
                    or finding_data.get("title")
                    or "Code Finding"
                )

                finding_title = str(finding_title)

                if len(finding_title) > 255:
                    finding_title = (
                        finding_title[:252] + "..."
                    )

                severity = (
                    verification.get("corrected_severity")
                    or finding_data.get("severity")
                    or "medium"
                )

                evidence = (
                    finding_data.get("evidence")
                    or finding_data.get("message")
                    or ""
                )

                explanation = (
                    finding_data.get("explanation")
                    or finding_data.get("message")
                    or ""
                )

                suggested_fix = (
                    finding_data.get("suggestion")
                    or finding_data.get("suggested_fix")
                    or ""
                )

                file_path = (
                    finding_data.get("file_path")
                    or ""
                )

                line_number = (
                    finding_data.get("line")
                )

                if line_number is None:
                    line_number = finding_data.get(
                        "line_number"
                    )

                confidence = (
                    verification.get("confidence")
                    if verification.get("confidence") is not None
                    else finding_data.get("confidence")
                )

                verification_status = (
                    verification.get(
                        "verification_status"
                    )
                    or "rejected"
                )

                verification_reason = (
                    verification.get("reason")
                    or ""
                )

                # -------------------------------------------------
                # Create Finding
                # -------------------------------------------------

                finding = Finding.objects.create(
                    review=review,
                    title=finding_title,
                    severity=severity,
                    file_path=file_path,
                    line_number=line_number,
                    evidence=str(evidence),
                    explanation=str(explanation),
                    suggested_fix=str(suggested_fix),
                    confidence=confidence,
                    verification_status=verification_status,
                    verification_reason=str(
                        verification_reason
                    ),
                )

                # -------------------------------------------------
                # Only pass verified findings to Summary Agent
                # -------------------------------------------------

                if verification_status == "verified":
                    verified_findings.append(
                        {
                            "id": finding.id,
                            **finding_data,
                            "verification": verification,
                        }
                    )

            except Exception as exc:
                trajectory.status = "failed"
                trajectory.error_message = (
                    "The Verification Agent could not complete its analysis."
                )
                trajectory.completed_at = timezone.now()
                trajectory.save()

                raise

        return verified_findings, next_step
        
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
            result = self.summary_agent.summarize(
                requirements_analysis=(
                    requirements_analysis
                ),
                verified_findings=(
                    verified_findings
                ),
            )

            trajectory.output_data = result
            trajectory.status = "completed"
            trajectory.completed_at = timezone.now()
            trajectory.save()

            return result

        except Exception as exc:
            trajectory.status = "failed"
            trajectory.error_message = (
                "The Summary Agent could not complete its analysis."
            )
            trajectory.completed_at = timezone.now()
            trajectory.save()

            raise