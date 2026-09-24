from sklearn.metrics import classification_report, confusion_matrix

from ml.config import LABELS

__all__ = ["evaluate_predictions"]


def evaluate_predictions(
    y_true: list[str], y_pred: list[str], dataset_name: str
) -> dict:
    """Print a classification report and return key metrics as a dict."""
    report = classification_report(
        y_true, y_pred, labels=LABELS, output_dict=True, zero_division=0
    )
    matrix = confusion_matrix(y_true, y_pred, labels=LABELS)

    print(f"\n=== Evaluation on {dataset_name} ===")
    print(classification_report(y_true, y_pred, labels=LABELS, zero_division=0))
    print("Confusion matrix (rows=true, cols=predicted):")
    print(f"Labels order: {LABELS}")
    print(matrix)

    return {
        "accuracy": report["accuracy"],
        "precision_macro": report["macro avg"]["precision"],
        "recall_macro": report["macro avg"]["recall"],
        "f1_macro": report["macro avg"]["f1-score"],
        "per_class": {
            label: {
                "precision": report[label]["precision"],
                "recall": report[label]["recall"],
                "f1": report[label]["f1-score"],
            }
            for label in LABELS
        },
    }
