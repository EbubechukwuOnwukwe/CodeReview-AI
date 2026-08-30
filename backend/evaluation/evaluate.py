import json
from pathlib import Path

from .baseline import BaselineReviewer
from .metrics import calculate_metrics


CASES_DIR = Path(__file__).parent / "cases"


def load_cases():
    cases = []

    for file_path in CASES_DIR.glob("*.json"):
        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as file:
            cases.append(json.load(file))

    return cases


def get_finding_keys(findings):
    """
    Extract stable identifiers from findings.

    Evaluation is based on issue_id rather than
    the natural-language title.
    """

    return {
        finding["issue_id"]
        for finding in findings
        if finding.get("issue_id")
    }


def evaluate_baseline(case):
    reviewer = BaselineReviewer()

    actual_findings = reviewer.review(
        case["code"]
    )

    expected = get_finding_keys(
        case["expected_findings"]
    )

    actual = get_finding_keys(
        actual_findings
    )

    true_positives = len(
        expected & actual
    )

    false_positives = len(
        actual - expected
    )

    false_negatives = len(
        expected - actual
    )

    return calculate_metrics(
        true_positives=true_positives,
        false_positives=false_positives,
        false_negatives=false_negatives,
    )


def main():
    cases = load_cases()

    print("\nCodeReview AI Evaluation")
    print("=" * 40)

    for case in cases:
        metrics = evaluate_baseline(case)

        print(f"\nCase: {case['name']}")

        print(
            f"True Positives: "
            f"{metrics['true_positives']}"
        )

        print(
            f"False Positives: "
            f"{metrics['false_positives']}"
        )

        print(
            f"False Negatives: "
            f"{metrics['false_negatives']}"
        )

        print(
            f"Precision: "
            f"{metrics['precision']:.2f}"
        )

        print(
            f"Recall: "
            f"{metrics['recall']:.2f}"
        )

        print(
            f"F1: "
            f"{metrics['f1']:.2f}"
        )


if __name__ == "__main__":
    main()