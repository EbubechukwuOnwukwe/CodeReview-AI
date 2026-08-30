from rest_framework import serializers

from .models import AgentTrajectory, Finding, Review


class FindingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Finding
        fields = [
            "id",
            "title",
            "severity",
            "file_path",
            "line_number",
            "evidence",
            "explanation",
            "suggested_fix",
            "confidence",
            "verification_status",
            "verification_reason",
            "created_at",
        ]


class AgentTrajectorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentTrajectory
        fields = [
            "id",
            "agent_name",
            "step",
            "input_data",
            "output_data",
            "status",
            "started_at",
            "completed_at",
            "error_message",
        ]


class ReviewSerializer(serializers.ModelSerializer):
    findings = FindingSerializer(
        many=True,
        read_only=True,
    )

    trajectories = AgentTrajectorySerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Review

        fields = [
            "id",
            "repository_url",
            "code",
            "requirements",
            "language",
            "status",
            "final_report",
            "error_message",
            "created_at",
            "started_at",
            "completed_at",
            "findings",
            "trajectories",
        ]

        read_only_fields = [
            "id",
            "status",
            "final_report",
            "error_message",
            "created_at",
            "started_at",
            "completed_at",
            "findings",
            "trajectories",
        ]

    def validate(self, attrs):
        repository_url = attrs.get("repository_url")
        code = attrs.get("code")

        if not repository_url and not code:
            raise serializers.ValidationError(
                "Either a GitHub repository URL or source code snippet is required."
            )

        return attrs