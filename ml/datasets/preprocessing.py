import pandas as pd
from sklearn.model_selection import train_test_split

from app.utils.text_preprocessing import clean_text, is_meaningful_text
from ml.config import (
    RATING_TO_LABEL,
    RANDOM_STATE,
    RATING_COLUMN,
    TEST_SIZE,
    TEXT_COLUMN,
    VAL_SIZE,
)

__all__ = ["load_and_label_dataset", "split_dataset"]


def load_and_label_dataset(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    df = df[[TEXT_COLUMN, RATING_COLUMN]].rename(
        columns={TEXT_COLUMN: "text", RATING_COLUMN: "rating"}
    )

    df = df.dropna(subset=["text", "rating"])
    df["rating"] = df["rating"].astype(int)
    df = df[df["rating"].between(1, 5)]

    df["text"] = df["text"].apply(clean_text)
    df = df[df["text"].apply(is_meaningful_text)]

    df = df.drop_duplicates(subset="text")
    df["label"] = df["rating"].map(RATING_TO_LABEL)

    return df.reset_index(drop=True)


def split_dataset(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split into stratified train/val/test sets, preserving label proportions."""
    train_df, temp_df = train_test_split(
        df,
        test_size=(TEST_SIZE + VAL_SIZE),
        stratify=df["label"],
        random_state=RANDOM_STATE,
    )

    relative_test_size = TEST_SIZE / (TEST_SIZE + VAL_SIZE)
    val_df, test_df = train_test_split(
        temp_df,
        test_size=relative_test_size,
        stratify=temp_df["label"],
        random_state=RANDOM_STATE,
    )

    return (
        train_df.reset_index(drop=True),
        val_df.reset_index(drop=True),
        test_df.reset_index(drop=True),
    )


if __name__ == "__main__":
    from ml.config import RAW_DATASET_PATH

    df = load_and_label_dataset(str(RAW_DATASET_PATH))
    print(f"Total rows after cleaning: {len(df)}")
    print(df["label"].value_counts())
    print(df["label"].value_counts(normalize=True).round(3))

    train_df, val_df, test_df = split_dataset(df)
    print(f"\nTrain: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
    print("\nTrain label distribution:")
    print(train_df["label"].value_counts(normalize=True).round(3))
