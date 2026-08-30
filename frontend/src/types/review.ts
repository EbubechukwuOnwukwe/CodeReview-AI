export type Severity = "critical" | "high" | "medium" | "low" | "info";
export type VerificationStatus = "pending" | "verified" | "rejected";
export type ReviewStatus = "pending" | "running" | "completed" | "failed";

export interface Finding {
  id: number;
  title: string;
  severity: Severity;
  file_path: string;
  line_number: number | null;
  evidence: string;
  explanation: string;
  suggested_fix: string;
  confidence: number | null;
  verification_status: VerificationStatus;
  verification_reason: string | null;
  created_at: string;
}

export interface AgentTrajectory {
  id: number;
  agent_name: string;
  step: number;
  input_data: Record<string, any>;
  output_data: Record<string, any>;
  status: "started" | "completed" | "failed";
  started_at: string;
  completed_at: string | null;
  error_message: string | null;
}

export interface SeveritySummary {
  critical?: number;
  high?: number;
  medium?: number;
  low?: number;
  info?: number;
}

export interface FinalReport {
  overall_summary?: string;
  risk_level?: string;
  priority_actions?: string[];
  severity_summary?: SeveritySummary;
  recommendations?: string[];
}

export interface Review {
  id: number;
  repository_url: string | null;
  code: string;
  requirements: string;
  language: string;
  status: ReviewStatus;
  final_report: FinalReport | null;
  error_message: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  findings: Finding[];
  trajectories: AgentTrajectory[];
}

export interface CreateReviewPayload {
  repository_url?: string;
  code?: string;
  requirements?: string;
  language?: string;
}
