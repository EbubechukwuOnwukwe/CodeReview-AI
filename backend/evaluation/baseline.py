import re


class BaselineReviewer:
    """
    A simple rule-based code reviewer.

    This is not intended to replace the AI reviewer.
    It provides a basic baseline for evaluation.
    """

    def review(self, code: str):
        findings = []

        # Hardcoded password / secret
        secret_pattern = re.compile(
            r"(password|passwd|secret|api_key|apikey)"
            r"\s*=\s*['\"][^'\"]+['\"]",
            re.IGNORECASE,
        )

        if secret_pattern.search(code):
            findings.append(
                {
                    "issue_id": "HARDCODED_SECRET",
                    "category": "security",
                    "severity": "high",
                    "title": "Possible hardcoded secret",
                }
            )

        # Use of eval()
        if re.search(r"\beval\s*\(", code):
            findings.append(
                {
                    "issue_id": "UNSAFE_EVAL",
                    "category": "security",
                    "severity": "high",
                    "title": "Use of eval()",
                }
            )

        # Bare except
        if re.search(r"except\s*:", code):
            findings.append(
                {
                    "issue_id": "BARE_EXCEPT",
                    "category": "quality",
                    "severity": "medium",
                    "title": "Bare except clause",
                }
            )

        return findings