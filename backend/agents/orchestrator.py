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
            review.error_message = str(exc)
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
            trajectory.error_message = str(exc)
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
            trajectory.error_message = str(exc)
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
                verification = (
                    self.verifier_agent.verify(
                        code=review.code,
                        requirements=(
                            requirements_analysis
                        ),
                        finding=finding_data,
                    )
                )

                trajectory.output_data = verification
                trajectory.status = "completed"
                trajectory.completed_at = timezone.now()
                trajectory.save()

                finding = Finding.objects.create(
                    review=review,
                    title=finding_data["title"],
                    severity=(
                        verification.get(
                            "corrected_severity",
                            finding_data["severity"],
                        )
                    ),
                    file_path=finding_data.get(
                        "file_path",
                        "",
                    ),
                    line_number=finding_data.get(
                        "line_number"
                    ),
                    evidence=finding_data[
                        "evidence"
                    ],
                    explanation=finding_data[
                        "explanation"
                    ],
                    suggested_fix=finding_data[
                        "suggested_fix"
                    ],
                    confidence=verification.get(
                        "confidence",
                        finding_data.get(
                            "confidence"
                        ),
                    ),
                    verification_status=(
                        verification[
                            "verification_status"
                        ]
                    ),
                    verification_reason=(
                        verification.get(
                            "reason",
                            "",
                        )
                    ),
                )

                if (
                    verification[
                        "verification_status"
                    ]
                    == "verified"
                ):
                    verified_findings.append(
                        {
                            "id": finding.id,
                            **finding_data,
                            "verification": verification,
                        }
                    )

            except Exception as exc:
                trajectory.status = "failed"
                trajectory.error_message = str(exc)
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
            trajectory.error_message = str(exc)
            trajectory.completed_at = timezone.now()
            trajectory.save()

            raise