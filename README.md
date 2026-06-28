# Amazon RAG Assistant

Proyecto del bootcamp de ingeniería de IA: pipeline RAG sobre productos de Amazon, API FastAPI, UI Streamlit y evaluación con LangSmith/Ragas.

## Estructura del proyecto

```
├── apps/
│   ├── api/              # FastAPI + RAG pipeline + evals
│   └── chatbot_ui/       # Streamlit UI
├── data/demo/            # Dataset demo (15 productos, incluido en git)
├── docker-compose.yml    # API + UI + Qdrant
├── pyproject.toml        # Workspace uv (monorepo)
└── Makefile              # Comandos habituales
```

> Los **notebooks** y los **datasets grandes** son locales y no se suben a GitHub (ver `.gitignore`).

## Requisitos

- [uv](https://docs.astral.sh/uv/)
- Docker & Docker Compose
- API keys: OpenAI (obligatoria para RAG), Groq y Google (opcionales)

## Configuración

1. Clona el repositorio e instala dependencias:

```bash
uv sync
```

2. Copia las variables de entorno:

```bash
cp .env.example .env
```

3. Rellena `.env` con tus API keys.

## Levantar con Docker

```bash
make run-docker-compose
```

| Servicio | URL |
|----------|-----|
| API (FastAPI) | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| Chatbot (Streamlit) | http://localhost:8501 |
| Qdrant | http://localhost:6333 |

### Probar el RAG

```bash
curl -X POST http://localhost:8000/rag/ \
  -H "Content-Type: application/json" \
  -d '{"query": "USB fan for router"}'
```

## Dataset demo

En `data/demo/meta_Electronics_sample.jsonl` hay **15 productos** de ejemplo (~84 KB) para desarrollo sin descargar ficheros de varios GB.

Para el dataset completo, descarga los metadatos de [Amazon Reviews 2023](https://amazon-reviews-2023.github.io/) y colócalos en `data/` (esa carpeta está ignorada por git).

## Evaluaciones

Con Qdrant en marcha y LangSmith configurado:

```bash
make run-evals-retriever
```

## Qué no se sube a GitHub

- `.env` y secretos
- `.venv/`
- `data/` (excepto `data/demo/`)
- `qdrant_data/`
- `notebooks/`

## Licencia

Ver [LICENSE](LICENSE).
