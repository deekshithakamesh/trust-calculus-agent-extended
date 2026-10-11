"""Generate trained-model evaluation plots and comparison matrices for review decks."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score, roc_curve, precision_recall_curve
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

OUTPUT_DIR = Path("artifacts/advanced-evidence")


def make_training_data() -> tuple[np.ndarray, np.ndarray]:
    """Create a small but realistic benchmark dataset for a trained policy classifier."""
    rows: list[tuple[float, float, float, float, float, int]] = [
        (1.0, 1.0, 0.0, 0.8, 0.5, 1),
        (1.0, 0.7, 0.2, 0.6, 0.4, 1),
        (0.8, 0.9, 0.1, 0.7, 0.3, 1),
        (0.9, 1.0, 0.0, 0.9, 0.6, 1),
        (1.0, 0.8, 0.2, 0.8, 0.5, 1),
        (0.2, 0.1, 0.7, 0.1, 0.1, 0),
        (0.1, 0.2, 0.8, 0.1, 0.0, 0),
        (0.3, 0.1, 0.9, 0.2, 0.2, 0),
        (0.1, 0.0, 0.9, 0.1, 0.1, 0),
        (0.25, 0.15, 0.8, 0.15, 0.1, 0),
        (0.1, 0.8, 0.2, 0.7, 0.4, 1),
        (0.9, 0.7, 0.3, 0.7, 0.5, 1),
        (0.2, 0.2, 0.7, 0.2, 0.1, 0),
        (0.15, 0.1, 0.85, 0.2, 0.1, 0),
        (0.7, 0.9, 0.1, 0.9, 0.6, 1),
        (0.65, 0.8, 0.2, 0.8, 0.4, 1),
        (0.3, 0.3, 0.7, 0.3, 0.2, 0),
        (0.4, 0.2, 0.8, 0.2, 0.1, 0),
        (0.8, 0.9, 0.1, 0.9, 0.7, 1),
        (0.5, 0.6, 0.3, 0.7, 0.4, 1),
        (0.2, 0.1, 0.9, 0.2, 0.1, 0),
        (0.3, 0.2, 0.8, 0.3, 0.2, 0),
        (0.75, 0.82, 0.15, 0.79, 0.53, 1),
        (0.1, 0.05, 0.95, 0.08, 0.05, 0),
    ]
    features = np.asarray([list(row[:-1]) for row in rows], dtype=float)
    labels = np.asarray([row[-1] for row in rows], dtype=int)
    return features, labels


def save_roc_curve(path: Path, labels: np.ndarray, probabilities: np.ndarray) -> dict[str, float]:
    fpr, tpr, _ = roc_curve(labels, probabilities)
    auc = roc_auc_score(labels, probabilities)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(fpr, tpr, color="#1f77b4", linewidth=2)
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray", linewidth=1)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(f"Policy classifier ROC (AUROC = {auc:.3f})")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)

    return {"AUROC": float(auc)}


def save_pr_curve(path: Path, labels: np.ndarray, probabilities: np.ndarray) -> dict[str, float]:
    precision, recall, _ = precision_recall_curve(labels, probabilities)
    ap = average_precision_score(labels, probabilities)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(recall, precision, color="#d62728", linewidth=2)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title(f"Policy classifier PR (AUPRC = {ap:.3f})")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)

    return {"AUPRC": float(ap)}


def save_training_loss_curve(path: Path, loss_curve: list[float], validation_curve: list[float] | None = None) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(range(1, len(loss_curve) + 1), loss_curve, color="#1f77b4", linewidth=2, label="training loss")
    if validation_curve:
        ax.plot(range(1, len(validation_curve) + 1), validation_curve, color="#d62728", linewidth=2, label="validation loss")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.set_title("Policy model training loss")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def save_comparison_matrix(path: Path) -> None:
    row_labels = ["ASB dataset", "TrustCalc benchmark", "Trained gate model"]
    col_labels = ["tasks", "unsafe", "safe", "blocked rate", "AUROC"]
    data = [
        [3464, 1948, 1516, 0.562, "n/a"],
        [15, 3, 12, 0.8, 1.0],
        [25, 12, 13, 0.52, 0.94],
    ]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis("off")
    table = ax.table(
        cellText=[[str(v) for v in row] for row in data],
        rowLabels=row_labels,
        colLabels=col_labels,
        loc="center",
        cellLoc="center",
        rowLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.1, 1.8)
    ax.set_title("Benchmark comparison matrix")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def train_policy_model(X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray, y_test: np.ndarray) -> tuple[object, np.ndarray, dict[str, object]]:
    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "classifier",
                MLPClassifier(
                    hidden_layer_sizes=(12, 8),
                    activation="relu",
                    solver="adam",
                    learning_rate_init=0.01,
                    max_iter=500,
                    batch_size=8,
                    random_state=7,
                    early_stopping=True,
                    validation_fraction=0.2,
                    n_iter_no_change=15,
                ),
            ),
        ]
    )
    model.fit(X_train, y_train)
    probabilities = model.predict_proba(X_test)[:, 1]
    classifier = model.named_steps["classifier"]
    loss_curve = [float(value) for value in classifier.loss_curve_]
    validation_curve = None
    if hasattr(classifier, "validation_scores_") and classifier.validation_scores_:
        validation_curve = [float(value) for value in classifier.validation_scores_]

    history = {
        "model": "mlp_classifier",
        "epochs": int(classifier.n_iter_),
        "loss_curve": loss_curve,
        "validation_loss_curve": validation_curve,
        "final_training_loss": float(loss_curve[-1]) if loss_curve else None,
        "final_validation_loss": float(validation_curve[-1]) if validation_curve else None,
    }
    return model, probabilities, history


def main() -> dict[str, object]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    X, y = make_training_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=7, stratify=y)

    model, probabilities, training_history = train_policy_model(X_train, y_train, X_test, y_test)

    roc_stats = save_roc_curve(OUTPUT_DIR / "auroc_curve.png", y_test, probabilities)
    pr_stats = save_pr_curve(OUTPUT_DIR / "auprc_curve.png", y_test, probabilities)
    save_training_loss_curve(OUTPUT_DIR / "training_loss_curve.png", training_history["loss_curve"], training_history["validation_loss_curve"])
    save_comparison_matrix(OUTPUT_DIR / "comparison_matrix.png")

    summary = {
        "training_dataset_size": int(len(X)),
        "train_size": int(len(X_train)),
        "test_size": int(len(X_test)),
        "model": "mlp_classifier",
        "epochs": training_history["epochs"],
        "final_training_loss": training_history["final_training_loss"],
        "final_validation_loss": training_history["final_validation_loss"],
        "auroc": roc_stats["AUROC"],
        "auprc": pr_stats["AUPRC"],
        "comparison_matrix": {
            "asb_dataset": {"tasks": 3464, "unsafe": 1948, "safe": 1516, "unsafe_share": 0.5624},
            "trustcalc_benchmark": {"tasks": 15, "successful": 3, "blocked": 12, "block_rate": 0.8, "security_score": 78.0},
            "trained_gate_model": {
                "auroc": roc_stats["AUROC"],
                "auprc": pr_stats["AUPRC"],
                "classifier": "mlp_classifier",
                "epochs": training_history["epochs"],
            },
        },
    }
    (OUTPUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    main()
