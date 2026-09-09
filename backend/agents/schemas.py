from typing import Optional

from pydantic import BaseModel, ConfigDict


# =========================================================
# REQUIREMENTS
# =========================================================

class SecurityRequirement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity: str
    vulnerability: str
    evidence: str


class RequirementsSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str

    functional_requirements: list[str]

    security_requirements: list[SecurityRequirement]

    constraints: list[str]

    acceptance_criteria: list[str]


# =========================================================
# CODE REVIEW
# =========================================================

class FindingSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    severity: str
    category: str
    file_path: str
    line_number: int | None
    evidence: str
    explanation: str
    suggested_fix: str
    confidence: float


class ReviewerSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    findings: list[FindingSchema]


# =========================================================
# VERIFICATION
# =========================================================

class VerifierSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    verification_status: str
    confidence: float
    reason: str
    corrected_severity: str | None
    recommendation: str | None


# =========================================================
# SUMMARY
# =========================================================

class SeveritySummarySchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    critical: int
    high: int
    medium: int
    low: int
    info: int


class RecommendationSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int | None
    action: str
    priority: str | None
    reason: str | None


class SummarySchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    overall_summary: str
    risk_level: str
    priority_actions: list[str]
    severity_summary: SeveritySummarySchema
    recommendations: list[RecommendationSchema]