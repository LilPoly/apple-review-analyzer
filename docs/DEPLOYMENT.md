# Deployment Notes

## Status

Full deployment configuration for Render is ready in this repository
(`render.yaml`, production-ready `Dockerfile` with `entrypoint.sh`), but
the live deployment is **not currently running** due to a memory
constraint described below. The application runs correctly and in full
locally via `docker-compose up --build`.

## What's ready

- `Dockerfile` — production entrypoint (`entrypoint.sh`) that downloads
  the BERT model from Hugging Face Hub, runs Alembic migrations, and
  starts Uvicorn, in that order, on every container start.
- `render.yaml` — Docker-based web service + managed Postgres + managed
  Redis, with all required environment variables mapped to Render's
  naming conventions (`DB_URL`, `REDIS_URL`, etc.).
- A `field_validator` in `Settings` that normalizes Render's
  `postgresql://` connection string to the `postgresql+psycopg://` format
  the app's SQLAlchemy driver expects.

## Known limitation: out-of-memory on Render's free tier

The container starts, downloads the BERT model, and connects to
Postgres/Redis successfully — but crashes with an out-of-memory error
during the FastAPI `lifespan` startup, specifically when `BertAnalyzer`
loads the PyTorch model into memory.

**Root cause:** PyTorch's runtime memory footprint — even for CPU-only
inference with a relatively small model like DistilBERT — is
significantly larger than the model's file size alone suggests. Loading
`torch`, `transformers`, and the model weights together exceeds Render's
free-tier memory allowance (512MB) once combined with FastAPI, the
Postgres/Redis clients, and the rest of the application's dependencies.

## Possible solutions (not implemented due to time constraints)

Given more time, the following approaches would likely resolve this:

- **Model optimization / quantization** — exporting the fine-tuned model
  to ONNX Runtime or using `optimum` for int8 quantization would
  significantly reduce both the memory footprint and inference time,
  at a small, usually acceptable, cost to accuracy.
- **Upgrading to a paid Render tier** with more RAM — the simplest fix,
  but outside the scope of a free-tier demo deployment.
- **Splitting BERT inference into a separate worker service** — keeping
  the main API lightweight (VADER + classical model only) and calling a
  dedicated, better-resourced service for BERT inference specifically.
- **Lazy-loading BERT only on first request** rather than at startup,
  trading a slower first request for a smaller baseline memory footprint
  — though this alone would likely not be sufficient given how close to
  the limit the app already runs without BERT loaded at all.

Given the one-week deadline for this test assignment, none of these were
implemented — the priority was a fully working local application with
all required features, rather than a partially-optimized cloud deployment.

## Running locally (recommended for review)

```bash
git clone https://github.com/LilPoly/apple-review-analyzer.git
cd apple-review-analyzer
cp .env.example .env
docker-compose up --build
```

See the main [README](../README.md) for the full usage flow.
