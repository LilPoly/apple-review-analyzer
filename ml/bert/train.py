import numpy as np
from datasets import Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)

from app.core.logger import get_logger
from ml.classical.evaluate import evaluate_predictions
from ml.config import (
    BERT_BATCH_SIZE,
    BERT_EPOCHS,
    BERT_MAX_LENGTH,
    BERT_MODEL_NAME,
    BERT_MODEL_PATH,
    LABELS,
    RANDOM_STATE,
    RAW_DATASET_PATH,
)
from ml.datasets.preprocessing import load_and_label_dataset, split_dataset

__all__ = ["train_and_evaluate_bert"]

logger = get_logger(__name__)

LABEL_TO_ID = {label: i for i, label in enumerate(LABELS)}
ID_TO_LABEL = {i: label for i, label in enumerate(LABELS)}


def train_and_evaluate_bert() -> dict:
    logger.info("Loading and labeling dataset for BERT...")
    df = load_and_label_dataset(str(RAW_DATASET_PATH))
    train_df, val_df, test_df = split_dataset(df)

    for d in [train_df, val_df, test_df]:
        d["label_id"] = d["label"].map(LABEL_TO_ID)

    train_ds = Dataset.from_pandas(train_df[["text", "label_id"]])
    val_ds = Dataset.from_pandas(val_df[["text", "label_id"]])
    test_ds = Dataset.from_pandas(test_df[["text", "label_id"]])

    logger.info(f"Loading tokenizer {BERT_MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(BERT_MODEL_NAME)

    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            padding="max_length",
            truncation=True,
            max_length=BERT_MAX_LENGTH,
        )

    logger.info("Tokenizing datasets...")
    train_ds = train_ds.map(tokenize_function, batched=True).rename_column(
        "label_id", "labels"
    )
    val_ds = val_ds.map(tokenize_function, batched=True).rename_column(
        "label_id", "labels"
    )
    test_ds = test_ds.map(tokenize_function, batched=True).rename_column(
        "label_id", "labels"
    )

    logger.info("Initializing model...")
    model = AutoModelForSequenceClassification.from_pretrained(
        BERT_MODEL_NAME,
        num_labels=len(LABELS),
        id2label=ID_TO_LABEL,
        label2id=LABEL_TO_ID,
    )

    training_args = TrainingArguments(
        output_dir=str(BERT_MODEL_PATH.parent / "checkpoints"),
        num_train_epochs=BERT_EPOCHS,
        per_device_train_batch_size=BERT_BATCH_SIZE,
        per_device_eval_batch_size=BERT_BATCH_SIZE,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        seed=RANDOM_STATE,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
    )

    logger.info("Starting fine-tuning...")
    trainer.train()

    logger.info(f"Saving final model and tokenizer to {BERT_MODEL_PATH}")
    BERT_MODEL_PATH.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(BERT_MODEL_PATH))
    tokenizer.save_pretrained(str(BERT_MODEL_PATH))

    logger.info("Generating predictions on test set...")
    predictions_output = trainer.predict(test_ds)

    pred_ids = np.argmax(predictions_output.predictions, axis=1)
    y_pred = [ID_TO_LABEL[i] for i in pred_ids]
    y_true = test_df["label"].tolist()

    metrics = evaluate_predictions(y_true, y_pred, "test set (BERT)")
    return metrics


if __name__ == "__main__":
    train_and_evaluate_bert()
