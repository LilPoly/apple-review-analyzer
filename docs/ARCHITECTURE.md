# Architecture

## Overview

The project follows a layered architecture with clear separation of
concerns, built around SOLID principles.


## Layers

- **`app/api/`** — FastAPI routes. Thin: no business logic, only request
  parsing, dependency injection, and error-to-HTTP-status mapping.
- **`app/schemas/`** — Pydantic DTOs. The API's public contract, decoupled
  from the internal ORM models.
- **`app/db/models/`** — SQLAlchemy ORM models (`AnalysisJob`, `Review`,
  `AnalysisResult`).
- **`app/repositories/`** — Thin data-access classes, one per entity. They
  only add/remove objects from the current session; they never commit.
- **`app/db/unit_of_work.py`** — Owns the DB session and commit boundary.
  A service opens `with uow:`, performs multiple repository operations,
  and calls `uow.commit()` once — guaranteeing atomicity (e.g. a job and
  all its reviews are saved together, or not at all).
- **`app/services/`** — Business logic and orchestration.
- **`app/utils/`** — Small, pure, stateless helper functions (text
  cleaning, statistics, URL parsing) with no external dependencies.
- **`ml/`** — Fully separate from `app/`. Offline training scripts,
  dataset preprocessing, and evaluation. Nothing here runs during a live
  API request.

## Key design decisions

### Strategy pattern for sentiment analysis

`SentimentAnalyzer` is an abstract base class implemented by three
interchangeable classes: `VaderAnalyzer`, `ClassicalAnalyzer`,
`BertAnalyzer`. `SentimentAnalysisService` receives a list of analyzers
via dependency injection and runs each one identically — adding a fourth
method later requires only a new class, no changes to existing code
(Open/Closed principle).

### Decorator pattern for caching

`CachedScraper` wraps `AppleRSSScraper`, implementing the same
`ScraperService` interface. The scraper itself has no knowledge of Redis;
caching is a separate, composable concern.

### Unit of Work over direct repository commits

Repositories never call `session.commit()`. Commit boundaries are decided
explicitly by services, which prevents partial writes (e.g. a job saved
without its reviews if an error occurs midway).

### Heavy models loaded once, not per-request

`BertAnalyzer` is loaded once at FastAPI startup via `lifespan` and stored
in `app.state`. `VaderAnalyzer` and `ClassicalAnalyzer` are cached via
`@lru_cache`. No model is ever re-loaded on a per-request basis.

### Why a pool-based cache, not a result-based cache

Redis caches the deduplicated, cleaned pool of raw reviews for an app —
not the final sampled subset. This means a request for `count=200` can
reuse the same cached pool as an earlier request for `count=50`, as long
as the pool is large enough; otherwise a fresh pool is fetched and the
cache is refreshed.
