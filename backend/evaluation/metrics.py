def calculate_precision(true_positives, false_positives):
    total = true_positives + false_positives

    if total == 0:
        return 0.0

    return true_positives / total


def calculate_recall(true_positives, false_negatives):
    total = true_positives + false_negatives

    if total == 0:
        return 0.0

    return true_positives / total


def calculate_f1(precision, recall):
    if precision + recall == 0:
        return 0.0

    return (
        2 * precision * recall
    ) / (
        precision + recall
    )


def calculate_metrics(
    true_positives,
    false_positives,
    false_negatives,
):
    precision = calculate_precision(
        true_positives,
        false_positives,
    )

    recall = calculate_recall(
        true_positives,
        false_negatives,
    )

    f1 = calculate_f1(
        precision,
        recall,
    )

    return {
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }