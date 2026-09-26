# Apple Store Review Analyzer

An API that collects real user reviews from the Apple App Store for any
specified app, processes them, and generates metrics and actionable
insights using three different NLP approaches — from a rule-based lexicon
method to a fine-tuned BERT model.

## What this project does

1. **Collects** up to 500 real reviews for any App Store app (just paste
   the app's App Store link).
2. **Processes** the data — text cleaning, deduplication, basic statistics.
3. **Analyzes sentiment** using three methods simultaneously:
   - VADER (lexicon-based, rule-based baseline)
   - TF-IDF + Logistic Regression (classical ML, trained from scratch)
   - Fine-tuned DistilBERT (contextual neural network)
4. **Compares** these three methods on real, measured metrics (accuracy, F1)
5. **Detects anomalies** — reviews where the star rating disagrees with the
   actual sentiment of the text (e.g. 5 stars but a clearly negative review)
6. **Visualizes** results as charts (rating distribution, sentiment
   distribution, model comparison)

## Quick Start

### Requirements
- Docker + Docker Compose

### Run locally

```bash
git clone https://github.com/LilPoly/apple-review-analyzer.git
cd apple-review-analyzer
cp .env.example .env
docker-compose up --build
```

Once running, open **http://localhost:8000/docs** — this is the
interactive Swagger UI with every available endpoint.

### Typical usage flow

1. `POST /api/v1/reviews/collect` — paste a link to any App Store app
   (e.g. `https://apps.apple.com/us/app/tinder/id547702041`)
2. `POST /api/v1/jobs/{job_id}/insights` — run sentiment analysis with
   all three methods
3. `GET /api/v1/jobs/{job_id}/charts/sentiment-distribution?method=bert` —
   view a chart directly in the browser

Full endpoint list: [docs/API_REFERENCE.md](docs/API_REFERENCE.md)

## Sample App: Tinder

The demo report was generated for **Tinder** (App ID: `547702041`, US store)
— an app with an active, emotionally expressive review base, which makes
the differences between the three sentiment methods easy to see.

Full report: [reports/sample_report_tinder.md](reports/sample_report_tinder.md)

## Tech Stack

FastAPI · PostgreSQL · Redis · Docker · scikit-learn · HuggingFace Transformers · pandas

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — layers, design patterns, key decisions
- [ML Approach](docs/ML_APPROACH.md) — dataset, training, evaluation, references
- [API Reference](docs/API_REFERENCE.md) — full description of every endpoint
- [Deployment Notes](docs/DEPLOYMENT.md) — cloud deployment attempt and its limits
