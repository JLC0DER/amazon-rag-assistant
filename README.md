# Amazon RAG Assistant

A retrieval-augmented generation (RAG) application for Amazon product search. It combines a FastAPI backend, a Streamlit chat UI, Qdrant vector search, and optional evaluation tooling with LangSmith and Ragas.

## Project structure

```
├── apps/
│   ├── api/              # FastAPI backend, RAG pipeline, and evals
│   └── chatbot_ui/       # Streamlit frontend
├── data/demo/            # Small demo dataset (tracked in git)
├── scripts/
│   └── index_demo.py     # Optional helper for fresh local setups
├── docker-compose.yml    # API, UI, and Qdrant services
├── pyproject.toml        # uv workspace (monorepo)
└── Makefile              # Common development commands
```

> Large datasets and local notebooks are excluded from version control (see `.gitignore`).

## Requirements

- [uv](https://docs.astral.sh/uv/)
- Docker & Docker Compose
- API keys: OpenAI (required for RAG), Groq and Google (optional)

## Setup

1. Clone the repository and install dependencies:

```bash
git clone https://github.com/JLC0DER/amazon-rag-assistant.git
cd amazon-rag-assistant
uv sync
```

2. Copy the environment template:

```bash
cp .env.example .env
```

3. Fill in your API keys in `.env`.

## Run with Docker

```bash
make run-docker-compose
```

| Service | URL |
|---------|-----|
| API (FastAPI) | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| Chatbot (Streamlit) | http://localhost:8501 |
| Qdrant | http://localhost:6333 |

## Fresh clone setup (optional)

If you clone the repository on a new machine and Qdrant is empty, run the standalone indexing helper:

```bash
make index-demo
```

This script only loads the demo dataset into Qdrant. It does **not** modify the application source code.

What it does:

- reads `data/demo/meta_Electronics_sample.jsonl`
- creates the `Amazon-items-collection-01` collection
- generates OpenAI embeddings
- upserts 15 demo products into Qdrant

If you already have a populated `qdrant_data/` directory from your own environment, you can skip this step.

### Test the RAG endpoint

```bash
curl -X POST http://localhost:8000/rag/ \
  -H "Content-Type: application/json" \
  -d '{"query": "USB fan for router"}'
```

## Demo dataset

`data/demo/meta_Electronics_sample.jsonl` contains **15 sample products** (~84 KB) for local development without downloading multi-gigabyte files.

For the full dataset, download metadata from [Amazon Reviews 2023](https://amazon-reviews-2023.github.io/) and place the files in `data/` (that directory is ignored by git).

## Evaluations (optional)

With Qdrant running and LangSmith configured:

```bash
make run-evals-retriever
```

## Excluded from version control

- `.env` and other secrets
- `.venv/`
- `data/` (except `data/demo/`)
- `qdrant_data/`
- local notebooks

## License

See [LICENSE](LICENSE).
