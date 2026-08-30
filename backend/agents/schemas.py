from typing import Optional
from pydantic import BaseModel, Field


class RequirementsSchema(BaseModel):
    summary: str
    functional_requirements: list[str] = Field(default_factory=list)
    security_requirements: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)


class FindingSchema(BaseModel):
    severity: str
    category: str
    message: str
    line: Optional[int] = None
    suggestion: str
    title: Optional[str] = None
    file_path: Optional[str] = ""
    evidence: Optional[str] = ""
    explanation: Optional[str] = None
    suggested_fix: Optional[str] = None
    confidence: Optional[float] = 1.0


class ReviewerSchema(BaseModel):
    findings: list[FindingSchema] = Field(default_factory=list)



class VerifierSchema(BaseModel):
    verification_status: str
    confidence: float
    reason: str
    corrected_severity: Optional[str] = None
    recommendation: Optional[str] = ""


class SeveritySummarySchema(BaseModel):
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0


class SummarySchema(BaseModel):
    overall_summary: str
    risk_level: str
    priority_actions: list[str] = Field(default_factory=list)
    severity_summary: SeveritySummarySchema
    recommendations: list[str] = Field(default_factory=list)