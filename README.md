# SentinelAI

AI-powered production incident investigation built with FastAPI and
Retrieval-Augmented Generation (RAG).

An incident is created through the API. SentinelAI collects the logs and
metrics attached to it, turns them into searchable evidence, retrieves the
pieces most relevant to a question, and asks an LLM to produce a structured
root-cause analysis grounded only in that evidence.

## How it works

```
POST /incidents/{id}/investigate  { "question": "..." }
        |
        v
1. Collect      incident + logs + metrics          (EvidenceService)
2. Chunk        one text chunk per log / metric,
                plus one trend summary per series  (ai/chunking.py)
3. Embed        chunks -> vectors (once per incident) (ai/embeddings.py)
4. Retrieve     question -> vector, top-k by
                cosine similarity                  (ai/vector_store.py)
5. Augment      incident + question + [E1..Ek]     (ai/prompt.py)
6. Generate     structured InvestigationResult     (ai/llm_client.py)
7. Store        InvestigationReport, incident
                status -> investigating            (InvestigationService)
```

Retrieval is scoped to a single incident, so evidence from one incident never
leaks into another investigation. Each piece of retrieved evidence is labelled
`[E1]`, `[E2]`, ... in the prompt, and the model is instructed to reference
those labels, not to invent facts, and to separate hypotheses from confirmed
causes.

## Project layout

```
backend/
  app/
    main.py                 FastAPI application
    config.py               Environment settings
    dependencies.py         Service wiring and OpenAI client setup
    routers/incidents.py    HTTP endpoints
    schemas/                Pydantic models (incident, log, metric,
                            evidence, investigation)
    services/               Business logic (incident, log, metric,
                            evidence, investigation)
    repositories/           In-memory storage
    simulators/             Synthetic auth-failure logs and metrics
    ai/
      chunking.py           Evidence -> text chunks
      embeddings.py         OpenAI embeddings
      vector_store.py       In-memory vector store, cosine similarity
      prompt.py             Prompt construction
      llm_client.py         Structured LLM analysis
  scripts/
    run_investigation.py    One real end-to-end run against OpenAI
  tests/                    Offline tests with fake embedder and LLM
```

All storage is in memory. Restarting the server clears incidents, evidence,
vectors, and investigation reports.

## Setup

Requires Python 3.12+.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then set OPENAI_API_KEY
```

| Variable                 | Default                  |
| ------------------------ | ------------------------ |
| `OPENAI_API_KEY`         | required for investigate |
| `OPENAI_MODEL`           | `gpt-4.1-mini`           |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` |

Without `OPENAI_API_KEY` the API still runs; only `/investigate` returns
`503`.

## Run

```bash
cd backend
uvicorn app.main:app --reload
```

Interactive docs: http://127.0.0.1:8000/docs

## API

| Method | Path                                          | Description                      |
| ------ | --------------------------------------------- | -------------------------------- |
| GET    | `/health`                                     | Health check                     |
| POST   | `/api/v1/incidents`                           | Create an incident               |
| GET    | `/api/v1/incidents`                           | List incidents                   |
| GET    | `/api/v1/incidents/count`                     | Count incidents                  |
| GET    | `/api/v1/incidents/{id}`                      | Get one incident                 |
| GET    | `/api/v1/incidents/{id}/logs`                 | Incident logs                    |
| GET    | `/api/v1/incidents/{id}/metrics`              | Incident metrics                 |
| POST   | `/api/v1/incidents/{id}/investigate`          | Run a RAG investigation          |
| GET    | `/api/v1/incidents/{id}/investigations`       | Past investigations              |

### Example

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/incidents \
  -H "Content-Type: application/json" \
  -d '{"title": "Authentication service failure",
       "description": "Users receive 401 errors after deployment",
       "severity": "high"}'

curl -s -X POST http://127.0.0.1:8000/api/v1/incidents/<id>/investigate \
  -H "Content-Type: application/json" \
  -d '{"question": "Why are refresh tokens rejected?", "top_k": 5}'
```

The request body is optional. Without it, the default question asks for the
most likely root cause and next steps, with `top_k = 6`.

Response shape:

```json
{
  "id": "...",
  "incident_id": "...",
  "question": "Why are refresh tokens rejected?",
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

## Tests

```bash
cd backend
pytest
```

Tests never call OpenAI. They replace the embedder and LLM with deterministic
fakes (`tests/fakes.py`) through FastAPI dependency overrides.

To try the real pipeline once:

```bash
cd backend
python -m scripts.run_investigation
python -m scripts.run_investigation "Did the deployment cause the 401 errors?"
```

## Limitations and next steps

- In-memory storage only; a database and a persistent vector store
  (pgvector, Chroma) would be the next step.
- Logs and metrics come from a single simulated auth-failure scenario.
- The vector index is built once per incident and is not refreshed if new
  evidence arrives later.
- Retrieval quality is not yet measured; a small labelled question set would
  allow tracking precision of the top-k results.
