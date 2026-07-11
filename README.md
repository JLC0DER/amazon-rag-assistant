# Amazon RAG Assistant

A retrieval-augmented generation (RAG) application for Amazon product search. It combines a FastAPI backend, a Streamlit chat UI, Qdrant vector search, and optional evaluation tooling with LangSmith and Ragas.

## Project structure

```
├── apps/
│   ├── api/              # FastAPI backend, RAG pipeline, and evals
│   └── chatbot_ui/       # Streamlit frontend
├── data/demo/            # Small demo dataset (tracked in git)
├── scripts/
│   └── index_demo.py     # Index demo products into Qdrant
├── docker-compose.yml    # API, UI, and Qdrant services
├── pyproject.toml        # uv workspace (monorepo)
└── Makefile              # Common development commands
```

> Large datasets and local notebooks are excluded from version control (see `.gitignore`).

## Requirements

- [uv](https://docs.astral.sh/uv/)
- Docker & Docker Compose
- API keys: **OpenAI** (required for embeddings and chat), **Cohere** (optional, for reranking), Groq and Google (optional)

## Local setup tutorial

Follow these steps on a fresh clone to run the project end to end.

### 1. Clone and install dependencies

```bash
git clone https://github.com/JLC0DER/amazon-rag-assistant.git
cd amazon-rag-assistant
uv sync
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set at least:

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Embeddings (`text-embedding-3-small`) and chat completions |
| `CO_API_KEY` | No | Cohere reranking (needed for hybrid+rerank evals) |
| `QDRANT_URL` | No | Defaults to `http://localhost:6333` for local scripts |
| `LANGSMITH_*` | No | Only needed for tracing and evals |

### 3. Start the stack with Docker

From the project root:

```bash
make run-docker-compose
```

This builds and starts three services:

| Service | URL |
|---------|-----|
| API (FastAPI) | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| Chatbot (Streamlit) | http://localhost:8501 |
| Qdrant | http://localhost:6333 |

Wait until the API logs show `Application startup complete`.

### 4. Index the demo dataset into Qdrant

On a **new terminal**, still from the project root, run:

```bash
make index-demo
```

Qdrant must already be running (step 3). The script loads the demo file from `data/demo/`, generates embeddings, and stores the products in Qdrant.

> If you already have a populated `qdrant_data/` directory, you can skip this step.

#### Run the script manually (without Make)

```bash
uv run --env-file .env --directory apps/api python ../../scripts/index_demo.py
```

### 5. Test the RAG API

```bash
curl -X POST http://localhost:8000/rag/ \
  -H "Content-Type: application/json" \
  -d '{"query": "Do you have a USB fan for router?"}'
```

Or open [http://localhost:8000/docs](http://localhost:8000/docs), select **POST /rag/**, and send:

```json
{
  "query": "Do you have a USB fan for router?"
}
```

### 6. Use the chatbot UI

Open [http://localhost:8501](http://localhost:8501) and ask product questions in the chat interface.

## Makefile commands

| Command | What it does |
|---------|--------------|
| `make run-docker-compose` | Sync deps and start API, Streamlit, and Qdrant |
| `make index-demo` | Index the 15-product demo dataset into Qdrant |
| `make run-evals-retriever` | Run baseline retriever evals (requires LangSmith + Qdrant) |
| `make run-evals-retriever-extended` | Run plain / hybrid / hybrid+rerank eval experiments |
| `make clean-notebook-outputs` | Clear Jupyter outputs from local notebooks |

## Demo dataset

`data/demo/meta_Electronics_sample.jsonl` contains **15 sample Electronics products** (~84 KB) for local development without downloading multi-gigabyte files.

The data comes from [Amazon Reviews 2023](https://amazon-reviews-2023.github.io/). For the full dataset, download the metadata from the official source and place the files in `data/` (that directory is ignored by git).

## Evaluations (optional)

With Qdrant running and LangSmith configured in `.env`:

```bash
make run-evals-retriever
```

### Extended retrieval experiments

Compare plain retrieval, hybrid search, and hybrid + Cohere reranking:

```bash
make run-evals-retriever-extended
```

Concurrency depends on your Cohere plan. In `apps/api/evals/eval_retriever_extended.py`:

```python
# Default is "trial". Switch to "paid" when using a paid Cohere API key.
COHERE_API_MODE = "trial"  # "trial" | "paid"
MAX_CONCURRENCY_TRIAL = 1
MAX_CONCURRENCY_PAID = 10
```

| Mode | `COHERE_API_MODE` | `max_concurrency` | When to use |
|------|-------------------|-------------------|-------------|
| Trial (default) | `"trial"` | `1` | Free/trial Cohere key (~10 req/min); avoids `429` |
| Paid | `"paid"` | `10` | Production Cohere key with higher rate limits |

The script also adds short sleeps between examples and retries Cohere `429` responses. That only slows the run; it does not change evaluation scores.

## Citation

This repository uses data provided by the authors of the following paper. If you use this work, please cite:

```bibtex
@article{hou2024bridging,
  title={Bridging Language and Items for Retrieval and Recommendation},
  author={Hou, Yupeng and Li, Jiacheng and He, Zhankui and Yan, An and Chen, Xiusi and McAuley, Julian},
  journal={arXiv preprint arXiv:2403.03952},
  year={2024}
}
```

Paper: [https://arxiv.org/abs/2403.03952](https://arxiv.org/abs/2403.03952)  
Dataset: [https://amazon-reviews-2023.github.io/](https://amazon-reviews-2023.github.io/)

## Excluded from version control

- `.env` and other secrets
- `.venv/`
- `data/` (except `data/demo/`)
- `qdrant_data/`
- local notebooks

## License

See [LICENSE](LICENSE).
