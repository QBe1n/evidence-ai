# API Reference

EvidenceAI provides a REST API built with FastAPI. Interactive documentation
is available at `http://localhost:8000/docs` (Swagger UI) and
`http://localhost:8000/redoc` (ReDoc) when running locally.

## Base URL

```
http://localhost:8000/api/v1       (local development)
https://api.evidenceai.com/api/v1  (production)
```

## Authentication

All endpoints require a Bearer token in the `Authorization` header:

```
Authorization: Bearer <your-api-key>
```

In development mode (`APP_ENV=development`), authentication is bypassed.

---

## Endpoints

### POST /reviews

Start a new systematic review. Returns a job ID for polling.

**Request:**

```json
{
  "question": "Does semaglutide reduce cardiovascular mortality in T2DM?",
  "databases": ["pubmed", "clinicaltrials"],
  "date_range": {"start": "2015-01-01", "end": "2025-12-31"},
  "study_designs": ["RCT", "META"],
  "max_results": 500,
  "include_augmentation": false
}
```

**Response (202 Accepted):**

```json
{
  "review_id": "rev_a1b2c3d4",
  "status": "queued",
  "estimated_minutes": 10,
  "job_url": "/api/v1/status/rev_a1b2c3d4"
}
```

---

### GET /status/{review_id}

Poll the status of an in-progress or completed review.

**Response:**

```json
{
  "review_id": "rev_a1b2c3d4",
  "status": "completed",
  "created_at": "2025-04-01T12:00:00Z",
  "updated_at": "2025-04-01T12:12:00Z",
  "question": "Does semaglutide reduce cardiovascular mortality in T2DM?",
  "stages_completed": ["ingest", "extract", "triangulate", "augment", "summarize"],
  "papers_found": 847,
  "papers_included": 124,
  "level_of_evidence": 0.88,
  "effect_direction": "inhibitory",
  "confidence": "strong"
}
```

**Status values:**
- `queued` — Job is waiting in the queue
- `running` — Pipeline is executing
- `completed` — Review is complete
- `failed` — Pipeline failed (see `error_message`)

---

### GET /reviews/{review_id}

Retrieve the full review result.

**Response:**

```json
{
  "review_id": "rev_a1b2c3d4",
  "question": "Does semaglutide reduce cardiovascular mortality in T2DM?",
  "status": "completed",
  "level_of_evidence": 0.88,
  "loe_label": "strong",
  "effect_direction": "inhibitory",
  "coe_scores": {
    "p_excitatory": 0.04,
    "p_no_change": 0.08,
    "p_inhibitory": 0.88,
    "dominant_direction": "inhibitory"
  },
  "summary": "Strong evidence (9 RCTs, n=47,382) demonstrates...",
  "key_findings": [
    "Level of Evidence: 0.88 (strong)",
    "Effect direction: inhibitory (p=0.880)",
    ...
  ],
  "papers_screened": 847,
  "papers_included": 124,
  "generated_at": "2025-04-01T12:12:00Z"
}
```

---

### GET /reviews/{review_id}/package

Download the FDA evidence package as a ZIP file.

**Response:** Binary ZIP file containing:
- `module_2.5_clinical_overview_{id}.txt`
- `module_2.7.3_clinical_efficacy_{id}.txt`
- `module_2.7.4_clinical_safety_{id}.txt`
- `evidence_table.json`

---

### POST /search

Search the evidence base.

**Request:**

```json
{
  "query": "KRAS G12D neoantigen immune response",
  "limit": 20,
  "databases": ["pubmed"]
}
```

---

### GET /evidence

Quick GET-based search.

```
GET /api/v1/evidence?q=KRAS+G12D+neoantigen&limit=20
```

---

## Error Responses

All errors follow a standard format:

```json
{
  "error": "validation_error",
  "message": "question must be at least 10 characters",
  "request_id": "req_abc123",
  "details": null
}
```

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | `validation_error` | Invalid request parameters |
| 401 | `unauthorized` | Missing or invalid API key |
| 404 | `not_found` | Review or resource not found |
| 429 | `rate_limited` | Too many requests |
| 500 | `internal_server_error` | Unexpected server error |

---

## Rate Limits

| Plan | Requests/minute | Requests/hour |
|------|-----------------|---------------|
| Free | 10 | 100 |
| Growth | 60 | 1,000 |
| Enterprise | Custom | Custom |

---

## Python SDK

The EvidenceAI Python package provides a high-level SDK. See
[README.md](../README.md) for full Python SDK documentation.

```python
from evidence_ai import EvidenceAI

client = EvidenceAI(openai_api_key="sk-...")
review = await client.synthesize(question="...")
```
