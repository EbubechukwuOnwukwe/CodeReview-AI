from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# ============================================================
# REQUIREMENTS
# ============================================================

class SecurityRequirement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity: str
    vulnerability: str
    evidence: str


class RequirementItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requirement: str
    priority: str


class RequirementsSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str

    functional_requirements: list[str]

    security_requirements: list[SecurityRequirement]

    constraints: list[str]

    acceptance_criteria: list[str]


# ============================================================
# CODE REVIEW
# ============================================================

class FindingSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity: str
    category: str
    message: str
    line: Optional[int]
    suggestion: str

    title: Optional[str]
    file_path: Optional[str]
    evidence: Optional[str]
    explanation: Optional[str]
    suggested_fix: Optional[str]
    confidence: Optional[float]


class ReviewerSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    findings: list[FindingSchema]


# ============================================================
# VERIFICATION
# ============================================================

class VerifierSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    verification_status: str
    confidence: float
    reason: str
    corrected_severity: Optional[str]
    recommendation: Optional[str]


# ============================================================
# SUMMARY
# ============================================================

class SeveritySummarySchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    critical: int
    high: int
    medium: int
    low: int
    info: int


class RecommendationSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: Optional[int]
    action: str
    priority: Optional[str]
    reason: Optional[str]


class SummarySchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    overall_summary: str

    risk_level: str

    priority_actions: list[str]

    severity_summary: SeveritySummarySchema

    recommendations: list[RecommendationSchema]