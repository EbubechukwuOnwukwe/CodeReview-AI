from typing import Optional, Any

from pydantic import BaseModel, Field


# ============================================================
# REQUIREMENTS
# ============================================================

class SecurityRequirement(BaseModel):
    severity: str = "medium"
    vulnerability: str = ""
    evidence: str = ""


class RequirementItem(BaseModel):
    requirement: str = ""
    priority: Optional[str] = "medium"


class RequirementsSchema(BaseModel):
    summary: str = ""

    functional_requirements: list[str] = Field(
        default_factory=list
    )

    security_requirements: list[SecurityRequirement] = Field(
        default_factory=list
    )

    constraints: list[str] = Field(
        default_factory=list
    )

    acceptance_criteria: list[str] = Field(
        default_factory=list
    )


# ============================================================
# CODE REVIEW
# ============================================================

class FindingSchema(BaseModel):
    severity: str = "medium"
    category: str = "code_quality"
    message: str = ""
    line: Optional[int] = None
    suggestion: str = ""

    title: Optional[str] = None
    file_path: Optional[str] = ""
    evidence: Optional[str] = ""
    explanation: Optional[str] = None
    suggested_fix: Optional[str] = None
    confidence: Optional[float] = 1.0


class ReviewerSchema(BaseModel):
    findings: list[FindingSchema] = Field(
        default_factory=list
    )


# ============================================================
# VERIFICATION
# ============================================================

class VerifierSchema(BaseModel):
    verification_status: str = "rejected"
    confidence: float = 0.0
    reason: str = ""
    corrected_severity: Optional[str] = None
    recommendation: Optional[str] = ""


# ============================================================
# SUMMARY
# ============================================================

class SeveritySummarySchema(BaseModel):
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0


class RecommendationSchema(BaseModel):
    id: Optional[int] = None
    action: str = ""
    priority: Optional[str] = "medium"
    reason: Optional[str] = ""


class SummarySchema(BaseModel):
    overall_summary: str = ""

    risk_level: str = "low"

    priority_actions: list[str] = Field(
        default_factory=list
    )

    severity_summary: SeveritySummarySchema = Field(
        default_factory=SeveritySummarySchema
    )

    recommendations: list[RecommendationSchema] = Field(
        default_factory=list
    )