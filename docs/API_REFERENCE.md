# API Reference

Base URL: `http://localhost:8000/api/v1`

## 1. `POST /reviews/collect`

**What it does:** Collects reviews for a given App Store app. Accepts
either a full App Store URL or a raw `app_id`. Internally: parses the
URL, checks Redis for an already-cached pool of reviews for this app
(keyed by `app_id` + `country`, with a 48-hour TTL), scrapes fresh data
from Apple's public RSS feed if the cache is empty or too small for the
requested `count`, deduplicates and cleans the text, then saves
everything to the database as one atomic transaction.

**Caching behavior:** the first request for a given app always hits
Apple's RSS feed directly. Any subsequent request for the same app,
within 48 hours, is served from Redis instead — as long as the cached
pool already contains at least as many reviews as requested. A request
for more reviews than are currently cached triggers a fresh scrape and
refreshes the cache with the larger pool.

**Request body:**
```json
{
  "app_store_url": "https://apps.apple.com/us/app/tinder/id547702041",
  "count": 100
}
```

**Response:** `job_id`, review count, average rating, rating distribution.

Errors: `400` invalid URL, `404` app not found on the App Store, `502`
scraper failure (e.g. Apple rate-limiting).

## 2. `GET /reviews/raw-data/{job_id}`

**What it does:** Fetches every review saved for the given `job_id` and
streams them back as a downloadable CSV file — the raw, cleaned data
behind any analysis.

## 3. `POST /jobs/{job_id}/insights`

**What it does:** Runs sentiment analysis on every review in a job using
all three methods at once — VADER, TF-IDF + Logistic Regression, and
fine-tuned BERT. For each method, it calculates the sentiment
distribution (% positive/neutral/negative), extracts the top keywords
from negative reviews, times the execution, and persists the full result
(including per-review predictions) to the database.

**Response:** a list of three `AnalysisResultDTO` objects, one per method.

**Note:** this endpoint must be called before endpoints 4, 5, and 8 below
— they read the results this endpoint saves, rather than recomputing them.

## 4. `GET /jobs/{job_id}/anomalies?method={vader|classical|bert}`

**What it does:** Compares the chosen method's predictions against a
"naive" rating-based label (1-2★→negative, 3★→neutral, 4-5★→positive) and
returns the reviews where they disagree most confidently — e.g. a
5-star review the model reads as negative from its actual text. Useful
for spotting cases where the star rating doesn't tell the full story.

## 5. `GET /jobs/{job_id}/actionable-insights?method={vader|classical|bert}`

**What it does:** Takes the negative keywords already extracted in step 3
and maps them to plain-language, human-readable recommendations via a
rule-based generator (e.g. "crash" → "prioritize stability and
crash-reporting fixes").

## 6. `GET /analytics/baseline-metrics`

**What it does:** A static endpoint — reads a JSON file generated offline
by `ml/generate_baseline_report.py` and returns it as-is. No computation
happens at request time. Returns precision/recall/F1/accuracy for all
three methods, evaluated on a held-out test split of the Kaggle training
dataset — this is the "which method is actually best" evidence, entirely
independent of any specific scraped app.

## 7. `GET /jobs/{job_id}/charts/rating-distribution`

**What it does:** Renders a bar chart of the star-rating distribution for
a job and returns it directly as a PNG image (open the URL in a browser
to view it).

## 8. `GET /jobs/{job_id}/charts/sentiment-distribution?method={vader|classical|bert}`

**What it does:** Renders a bar chart of the sentiment distribution
(positive/neutral/negative) for the chosen method, using the results
already saved in step 3.

## 9. `GET /analytics/charts/model-comparison`

**What it does:** Renders a bar chart comparing macro F1 scores of all
three methods, using the same data as endpoint 6, as a chart instead of JSON.

## 10. `GET /jobs/{job_id}/report/pdf`

**What it does:** Generates a complete, styled PDF report for a job —
overview stats, rating distribution chart, and a dedicated section per
NLP method (sentiment chart, negative keywords, actionable insights,
execution time). Built with Jinja2 + WeasyPrint, with all charts embedded
as base64 images (no temporary files written to disk). This is the same
kind of report used for the demo sample report included in this repo
(`reports/sample_report_tinder.md`), generated on demand for any job.

**Note:** like endpoints 4 and 5, this requires step 3 to have already
run and saved results for at least one method — otherwise returns `404`
with a message explaining what to do first.

Returns: a downloadable PDF file (`Content-Disposition: attachment`).
