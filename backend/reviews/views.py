from agents import reviewer_agent
from collections import Counter

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from agents.orchestrator import ReviewOrchestrator

from integrations.github import GitHubService
from .models import Review
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().order_by("-created_at")
    serializer_class = ReviewSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        repository_url = serializer.validated_data.get(
            "repository_url"
        )
        code = serializer.validated_data.get(
            "code"
        )
        requirements = serializer.validated_data.get(
            "requirements"
        )
        language = serializer.validated_data.get(
            "language"
        ) or "JavaScript"

        if not requirements:
            requirements = (
                "Review this code for bugs, "
                "security vulnerabilities, code quality "
                "issues, maintainability problems, and "
                "deviations from good software engineering "
                "practices."
            )

        review = Review.objects.create(
            repository_url=repository_url or "",
            code=code or "",
            requirements=requirements,
            language=language,
            status=Review.Status.PENDING,
        )

        try:
            if repository_url:
                github = GitHubService()

                files = github.get_repository_files(
                    repository_url
                )

                if not files:
                    raise ValueError(
                        "No reviewable source-code files "
                        "were found in the repository."
                    )

                codebase_parts = []
                total_size = 0
                extension_counts = Counter()

                for file in files:
                    file_path = file["path"]

                    content = github.get_file_content(
                        repository_url,
                        file_path,
                    )

                    if not content.strip():
                        continue

                    if len(content) > github.MAX_FILE_SIZE:
                        content = content[
                            :github.MAX_FILE_SIZE
                        ]

                    remaining_size = (
                        github.MAX_TOTAL_CODE_SIZE
                        - total_size
                    )

                    if remaining_size <= 0:
                        break

                    content = content[:remaining_size]

                    codebase_parts.append(
                        f"\n"
                        f"{'=' * 80}\n"
                        f"FILE: {file_path}\n"
                        f"{'=' * 80}\n"
                        f"{content}\n"
                    )

                    total_size += len(content)

                    extension = (
                        "."
                        + file_path.rsplit(".", 1)[-1].lower()
                    )

                    extension_counts[extension] += 1

                if not codebase_parts:
                    raise ValueError(
                        "The repository contains no "
                        "readable source-code files."
                    )

                codebase = "".join(codebase_parts)

                detected_lang = self._detect_language(
                    extension_counts
                )

                review.code = codebase
                review.language = detected_lang
                review.save(
                    update_fields=[
                        "code",
                        "language",
                    ]
                )
            elif not review.code:
                raise ValueError("Neither a repository URL nor source code was provided.")

            orchestrator = ReviewOrchestrator()

            orchestrator.run(
                review.id
            )

            review.refresh_from_db()

            return Response(
                self.get_serializer(review).data,
                status=status.HTTP_201_CREATED,
            )

        except Exception as exc:
            import traceback

            print("\n" + "=" * 80)
            print("REVIEW CREATION FAILED")
            print("=" * 80)

            # Keep the real technical error in the backend console/logs.
            traceback.print_exc()

            print("=" * 80 + "\n")

            review.status = Review.Status.FAILED

            review.error_message = (
                "We couldn't complete this code review right now. "
                "Please try again in a moment."
            )

            review.save(
                update_fields=[
                    "status",
                    "error_message",
                ]
            )

            return Response(
                self.get_serializer(review).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    @action(detail=True, methods=["post"])
    def retry(self, request, pk=None):
        review = self.get_object()
        review.status = Review.Status.PENDING
        review.error_message = None
        review.save(update_fields=["status", "error_message"])

        try:
            orchestrator = ReviewOrchestrator()
            orchestrator.run(review.id)

            review.refresh_from_db()
            return Response(
                self.get_serializer(review).data,
                status=status.HTTP_200_OK,
            )
        except Exception as exc:
            import traceback

            print("\n" + "=" * 80)
            print("REVIEW RETRY FAILED")
            print("=" * 80)

            traceback.print_exc()

            print("=" * 80 + "\n")

            review.status = Review.Status.FAILED

            review.error_message = (
                "We couldn't complete this code review right now. "
                "Please try again in a moment."
            )

            review.save(
                update_fields=[
                    "status",
                    "error_message",
                ]
            )

            return Response(
                self.get_serializer(review).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


    
    @staticmethod
    def _detect_language(extension_counts):
        if not extension_counts:
            return "Unknown"

        language_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".jsx": "JavaScript",
            ".ts": "TypeScript",
            ".tsx": "TypeScript",
            ".java": "Java",
            ".php": "PHP",
            ".go": "Go",
            ".rs": "Rust",
            ".c": "C",
            ".cpp": "C++",
            ".h": "C",
            ".hpp": "C++",
            ".cs": "C#",
            ".rb": "Ruby",
            ".swift": "Swift",
            ".kt": "Kotlin",
            ".kts": "Kotlin",
            ".dart": "Dart",
            ".sql": "SQL",
        }

        extension, _ = extension_counts.most_common(1)[0]

        return language_map.get(
            extension,
            "Unknown",
        )