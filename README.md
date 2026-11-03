# SentinelAI

AI-powered production incident investigation built with FastAPI,
Retrieval-Augmented Generation (RAG), and Chroma.

An incident is created through the API. SentinelAI collects the logs and
metrics attached to it, embeds them into a Chroma vector store, retrieves the
pieces most relevant to a question, and asks an LLM to produce a structured
root-cause analysis grounded only in that evidence.

## How it works

```
POST /incidents/{id}/investigate  { "question": "..." }
        |
        v
1. Collect      incident + logs + metrics           (EvidenceService)
2. Chunk        one text chunk per log / metric,
                plus one trend summary per series   (ai/chunking.py)
3. Embed        chunks -> vectors, once per incident (ai/embeddings.py)
4. Store        upsert into Chroma, tagged with
                incident_id and source              (ai/vector_store.py)
5. Retrieve     question -> vector, top-k by cosine
                similarity within this incident     (ai/vector_store.py)
6. Augment      incident + question + [E1..Ek]      (ai/prompt.py)
7. Generate     structured InvestigationResult      (ai/llm_client.py)
8. Persist      InvestigationReport in SQLite,
                incident status -> investigating    (InvestigationService)
```

Retrieval is filtered by `incident_id`, so evidence from one incident never
leaks into another investigation. Each retrieved chunk is labelled `[E1]`,
`[E2]`, ... in the prompt, and the model is instructed to reference those
labels, not to invent facts, and to separate hypotheses from confirmed causes.

Chunk ids are deterministic (a log chunk reuses the log id, the incident and
trend chunks are derived from the incident id), so re-indexing an incident
overwrites its vectors instead of duplicating them.

## Storage

| Data                                     | Store  | Default location        |
| ---------------------------------------- | ------ | ----------------------- |
| Incidents, logs, metrics, investigations | SQLite | `backend/data/sentinel.db` |
| Evidence vectors                         | Chroma | `backend/data/chroma/`  |

Both survive restarts. `backend/data/` is git-ignored. Delete it to start
from an empty state.

Chroma keeps one collection per embedding model
(`incident-evidence-<model>`), because vectors from different models have
different sizes and cannot be compared. Changing `OPENAI_EMBEDDING_MODEL`
therefore re-indexes incidents on their next investigation.

## Simulated scenarios

Telemetry is simulated. The `scenario` field on an incident selects which
logs and metrics are attached to it. Each scenario mixes relevant evidence
with unrelated noise, so retrieval has to pick the right chunks.

| Scenario                   | Story                                                                 | Metrics                                   |
| -------------------------- | --------------------------------------------------------------------- | ----------------------------------------- |
| `auth_failure` (default)   | auth-service v2.4.0 deploy breaks refresh token signatures, 401s      | auth-service error rate                   |
| `database_pool_exhaustion` | order-service v3.1.0 raises worker concurrency, connection pool runs dry, 504s | order-service p95 latency, error rate |
| `cache_outage`             | a Redis node drops out, cache misses push load onto the catalog DB    | catalog-db request count, catalog p95 latency |

## Project layout

```
backend/
  app/
    main.py                 FastAPI application
    config.py               Environment settings
    db.py                   SQLite connection and schema
    dependencies.py         Service wiring, OpenAI and Chroma clients
    routers/incidents.py    HTTP endpoints
    schemas/                Pydantic models (incident, log, metric,
                            evidence, investigation)
    services/               Business logic (incident, log, metric,
                            evidence, investigation)
    repositories/           SQLite repositories
    simulators/             Simulated telemetry per scenario
    ai/
      chunking.py           Evidence -> text chunks
      embeddings.py         OpenAI embeddings
      vector_store.py       Chroma vector store
      prompt.py             Prompt construction
      llm_client.py         Structured LLM analysis
    evaluation/
      retrieval.py          Labelled questions, hit rate and MRR
  scripts/
    run_investigation.py    One real end-to-end investigation
    evaluate_retrieval.py   Retrieval quality with real embeddings
  tests/                    Offline tests with fake embedder and LLM
```

## Setup

Requires Python 3.12+.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then set OPENAI_API_KEY
```

| Variable                 | Default                    |
| ------------------------ | -------------------------- |
| `OPENAI_API_KEY`         | required for investigate   |
| `OPENAI_MODEL`           | `gpt-4.1-mini`             |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small`   |
| `SENTINEL_DB_PATH`       | `backend/data/sentinel.db` |
| `CHROMA_PATH`            | `backend/data/chroma`      |

Without `OPENAI_API_KEY` the API still runs; only `/investigate` returns
`503`.

## Run

```bash
cd backend
uvicorn app.main:app --reload
```

Interactive docs: http://127.0.0.1:8000/docs

## API

| Method | Path                                    | Description             |
| ------ | --------------------------------------- | ----------------------- |
| GET    | `/health`                               | Health check            |
| POST   | `/api/v1/incidents`                     | Create an incident      |
| GET    | `/api/v1/incidents`                     | List incidents          |
| GET    | `/api/v1/incidents/count`               | Count incidents         |
| GET    | `/api/v1/incidents/{id}`                | Get one incident        |
| GET    | `/api/v1/incidents/{id}/logs`           | Incident logs           |
| GET    | `/api/v1/incidents/{id}/metrics`        | Incident metrics        |
| POST   | `/api/v1/incidents/{id}/investigate`    | Run a RAG investigation |
| GET    | `/api/v1/incidents/{id}/investigations` | Past investigations     |

### Example

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/incidents \
  -H "Content-Type: application/json" \
  -d '{"title": "Order API timing out",
       "description": "Checkout requests fail with 504 errors",
       "severity": "critical",
       "scenario": "database_pool_exhaustion"}'

curl -s -X POST http://127.0.0.1:8000/api/v1/incidents/<id>/investigate \
  -H "Content-Type: application/json" \
  -d '{"question": "Why are order requests timing out?", "top_k": 5}'
```

The request body is optional. Without it, the default question asks for the
most likely root cause and next steps, with `top_k = 6`.

Response shape:

```json
{
  "id": "...",
  "incident_id": "...",
  "question": "Why are order requests timing out?",
  "model": "gpt-4.1-mini",
  "result": {
    "summary": "...",
    "probable_root_cause": "...",
    "confidence": "medium",
    "evidence": ["[E1] ...", "[E2] ..."],
    "recommended_actions": ["..."]
  },
  "retrieved_evidence": [
    {
      "chunk": { "id": "...", "incident_id": "...", "source": "log", "text": "..." },
      "score": 0.83
    }
  ],
  "created_at": "..."
}
```

Errors: `404` unknown incident, `422` invalid body, `502` LLM provider failure,
`503` missing API key.

## Retrieval evaluation

`app/evaluation/retrieval.py` defines labelled questions for every scenario.
Each question names a piece of text that appears in exactly one relevant
chunk. The evaluation indexes the sample incidents, runs each question, and
reports:

- **hit rate@k**: share of questions whose relevant chunk is in the top k
- **MRR@k**: mean of `1 / rank` of the relevant chunk (0 when missed)

```bash
cd backend
python -m scripts.evaluate_retrieval        # k = 3
python -m scripts.evaluate_retrieval --k 1
```

It uses real OpenAI embeddings and an in-memory Chroma collection, so the
persistent index is not touched. Cost is a fraction of a cent.

## Tests

```bash
cd backend
pytest
```

Tests never call OpenAI. They replace the embedder and LLM with deterministic
fakes (`tests/fakes.py`) through FastAPI dependency overrides, use an
in-memory SQLite database, and give every test its own in-memory Chroma
collection.

To try the real pipeline:

```bash
cd backend
python -m scripts.run_investigation
python -m scripts.run_investigation --scenario cache_outage
python -m scripts.run_investigation "Did the deployment cause the 401 errors?"
```

## Cost

The OpenAI API is billed separately from ChatGPT and needs prepaid credit.
One investigation uses roughly 1,500 tokens with `gpt-4.1-mini` and
`text-embedding-3-small`, which is around a tenth of a cent. Check current
prices at https://openai.com/api/pricing/.

## Limitations

- Telemetry is simulated; there is no integration with a real log or metrics
  backend.
- An incident is indexed once. Evidence added after the first investigation
  is not picked up unless the incident's vectors are deleted.
- SQLite uses one shared connection, which is fine for a single process but
  not for multiple workers.
