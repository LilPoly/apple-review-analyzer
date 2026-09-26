# ML Approach

## Dataset

Training data: [Google Play Store Reviews](https://www.kaggle.com/datasets/prakharrathi25/google-play-store-reviews?resource=download)
(Kaggle), ~12,000 real app reviews with star ratings.

This dataset is used **only** for training and evaluating the sentiment
models — it is never mixed with reviews scraped from the App Store at
inference time. This avoids data leakage: a model must generalize to
sentiment in general, not memorize the vocabulary of one specific app.

## Labeling

Since there is no pre-existing sentiment label, ratings are mapped to a
3-class scheme, used consistently across all three methods:

| Rating | Label |
|---|---|
| 1-2 stars | negative |
| 3 stars | neutral |
| 4-5 stars | positive |

## Preprocessing

Text is cleaned identically whether it comes from the training dataset or
from a freshly scraped App Store review — URL removal, whitespace
normalization, and a minimum meaningful-word-count filter. This is enforced
by reusing the exact same `clean_text()` / `is_meaningful_text()` functions
in both the training pipeline (`ml/`) and the live API (`app/`), avoiding
any train/serve skew.

## Train / Validation / Test Split

Stratified 80/10/10 split (`random_state=42`), preserving class
proportions across all three subsets.

## Methods Compared

### 1. VADER (rule-based baseline)

Lexicon-based sentiment scoring — no training involved. Used as a
baseline to demonstrate the value of a trained model.

Reference: [VADER Sentiment Model Explained](https://medium.com/@lvdeep9/a-brief-of-how-the-vader-sentiment-model-generates-sentiment-scores-467ba7576cc9)

### 2. TF-IDF + Logistic Regression (classical ML)

`TfidfVectorizer` (unigrams + bigrams) feeding a `LogisticRegression`
classifier with `class_weight="balanced"` to counter class imbalance.
Trained on the Kaggle dataset described above.

Reference: [Sentiment Analysis with TF-IDF and Logistic Regression](https://medium.com/@manwill/sentiment-analysis-with-tf-idf-and-logistic-regression-f4cd86f359a1)

### 3. Fine-tuned DistilBERT

`distilbert-base-uncased`, fine-tuned for 2 epochs on the same labeled
dataset (Colab, T4 GPU — see `notebooks/train_bert_colab.ipynb`).

Reference: [Sentiment Analysis with BERT — A Comprehensive Guide](https://medium.com/@alexrodriguesj/sentiment-analysis-with-bert-a-comprehensive-guide-6d4d091eb6bb)

## Evaluation Results (test set)

| Method | Accuracy | Macro F1 | Negative Recall | Neutral Recall | Positive Recall |
|---|---|---|---|---|---|
| VADER | 0.59 | 0.49 | 0.46 | 0.15 | 0.88 |
| TF-IDF + LogReg | 0.66 | 0.60 | 0.69 | 0.41 | 0.72 |
| BERT | 0.77 | 0.65 | 0.89 | 0.22 | 0.85 |

BERT achieves the best overall accuracy and macro F1, and is used as the
primary model in production. Notably, the balanced classical model
outperforms BERT specifically on the `neutral` class — a reminder that
3-star reviews are genuinely ambiguous text, and no method solves this
perfectly without further tuning (e.g. `class_weight` for BERT, left as a
future improvement).

Full metrics are available live at `GET /api/v1/analytics/baseline-metrics`.

## Model Hosting

The fine-tuned BERT checkpoint (~256MB) exceeds GitHub's 100MB per-file
limit, so it is not committed to this repository. Instead, it is hosted
publicly on Hugging Face Hub:

**https://huggingface.co/LizaPolozenko/apple-review-bert-sentiment**

At container startup, `app/scripts/download_model.py` checks whether the
model already exists locally (`ml/artifacts/bert/bert-sentiment-v1/`); if
not, it downloads it automatically via `huggingface_hub.snapshot_download`.
This means a fresh `git clone` + `docker-compose up --build` works
out of the box with no manual download step required.

The classical model (`tfidf_logreg_v1.joblib`, a few MB) is small enough
to be committed directly to the repository and requires no download step.

## Negative Keyword Extraction

Top negative keywords are extracted via TF-IDF restricted to reviews
classified as negative. Note: for apps with a strong, repeated brand name
in the reviews (e.g. "Tinder", "Duolingo"), this can surface the app name
itself as a top keyword rather than the actual complaint — a known
limitation of frequency-based extraction without a contrastive
(negative-vs-positive) baseline.

## Reproducing Training

```bash
uv run python -m ml.classical.train      # trains and saves TF-IDF + LogReg
uv run python -m ml.bert.evaluate        # evaluates the already fine-tuned BERT model
uv run python -m ml.generate_baseline_report  # regenerates baseline_metrics.json
```

BERT fine-tuning itself is done via Colab (GPU required for reasonable
training time) — see `notebooks/train_bert_colab.ipynb`.
