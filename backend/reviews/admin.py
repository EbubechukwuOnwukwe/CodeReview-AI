from django.contrib import admin

from .models import AgentTrajectory, Finding, Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "language",
        "status",
        "created_at",
        "completed_at",
    )

    list_filter = (
        "status",
        "language",
    )

    search_fields = (
        "code",
        "requirements",
        "repository_url",
    )

    readonly_fields = (
        "created_at",
        "started_at",
        "completed_at",
    )


@admin.register(Finding)
class FindingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "review",
        "severity",
        "verification_status",
        "confidence",
        "created_at",
    )

    list_filter = (
        "severity",
        "verification_status",
    )

    search_fields = (
        "title",
        "evidence",
        "explanation",
        "suggested_fix",
    )

    readonly_fields = (
        "created_at",
    )


@admin.register(AgentTrajectory)
class AgentTrajectoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "review",
        "agent_name",
        "step",
        "status",
        "started_at",
        "completed_at",
    )

    list_filter = (
        "agent_name",
        "status",
    )

    search_fields = (
        "agent_name",
        "error_message",
    )

    readonly_fields = (
        "started_at",
        "completed_at",
    )

    ordering = (
        "review",
        "step",
    )