import time

from api.agents.retrieval_generation import rag_pipeline

from langsmith import Client

from openai import AsyncOpenAI

from ragas.llms import llm_factory
from ragas.embeddings import OpenAIEmbeddings

from ragas.metrics.collections import Faithfulness, AnswerRelevancy

from qdrant_client import QdrantClient


ls_client = Client()
qdrant_client = QdrantClient(url="http://localhost:6333")

openai_client = AsyncOpenAI()

ragas_llm = llm_factory("gpt-4.1-mini", client=openai_client, max_tokens=4000)
ragas_embeddings = OpenAIEmbeddings(client=openai_client, model="text-embedding-3-small")

# Cohere API plan controls LangSmith evaluate concurrency.
# - "trial": free/trial key (~10 req/min) -> keep concurrency at 1 to avoid 429s
# - "paid": production key -> allow higher concurrency
# Default is "trial". Switch to "paid" when using a paid Cohere API key.
COHERE_API_MODE = "trial"  # "trial" | "paid"
MAX_CONCURRENCY_TRIAL = 1
MAX_CONCURRENCY_PAID = 10
MAX_CONCURRENCY = MAX_CONCURRENCY_TRIAL if COHERE_API_MODE == "trial" else MAX_CONCURRENCY_PAID

# Throttle calls to stay under trial API limits.
# Cohere trial keys allow ~10 requests/minute.
SLEEP_BETWEEN_CALLS_SECONDS = 2
SLEEP_BETWEEN_RERANK_CALLS_SECONDS = 7
SLEEP_BETWEEN_EXPERIMENTS_SECONDS = 10


def _safe_outputs(run):
    return run.outputs or {}


def context_precision_id_based(run, example):
    outputs = _safe_outputs(run)
    if "retrieved_context_ids" not in outputs:
        return None

    retrieved_context_ids = {str(id) for id in outputs["retrieved_context_ids"]}
    reference_context_ids = {str(id) for id in example.outputs["reference_context_ids"]}

    score = (
        len(retrieved_context_ids & reference_context_ids) / len(retrieved_context_ids)
        if retrieved_context_ids
        else 0.0
    )
    return score


def context_recall_id_based(run, example):
    outputs = _safe_outputs(run)
    if "retrieved_context_ids" not in outputs:
        return None

    retrieved_context_ids = {str(id) for id in outputs["retrieved_context_ids"]}
    reference_context_ids = {str(id) for id in example.outputs["reference_context_ids"]}

    score = (
        len(retrieved_context_ids & reference_context_ids) / len(reference_context_ids)
        if reference_context_ids
        else 0.0
    )
    return score


def ragas_faithfulness(run, example):
    outputs = _safe_outputs(run)
    if not all(key in outputs for key in ("question", "answer", "retrieved_context")):
        return None

    scorer = Faithfulness(llm=ragas_llm)
    result = scorer.score(
        user_input=outputs["question"],
        response=outputs["answer"],
        retrieved_contexts=outputs["retrieved_context"],
    )
    return result.value


def ragas_relevancy(run, example):
    outputs = _safe_outputs(run)
    if not all(key in outputs for key in ("question", "answer")):
        return None

    scorer = AnswerRelevancy(llm=ragas_llm, embeddings=ragas_embeddings)
    result = scorer.score(
        user_input=outputs["question"],
        response=outputs["answer"],
    )
    return result.value


def make_target(hybrid: bool, rerank: bool, sleep_seconds: float):
    def target(example):
        result = rag_pipeline(
            example["question"],
            qdrant_client,
            top_k=10,
            hybrid=hybrid,
            rerank=rerank,
        )
        time.sleep(sleep_seconds)
        return result

    return target


EVALUATORS = [
    context_precision_id_based,
    context_recall_id_based,
    #ragas_faithfulness,
    #ragas_relevancy,
]


def run_experiment(prefix: str, hybrid: bool, rerank: bool, sleep_seconds: float):
    print(f"Evaluating {prefix} retriever (max_concurrency={MAX_CONCURRENCY}, mode={COHERE_API_MODE})")
    return ls_client.evaluate(
        make_target(hybrid=hybrid, rerank=rerank, sleep_seconds=sleep_seconds),
        data="rag-evaluation-dataset-extended",
        evaluators=EVALUATORS,
        experiment_prefix=prefix,
        max_concurrency=MAX_CONCURRENCY,
    )


results = run_experiment(
    prefix="plain",
    hybrid=False,
    rerank=False,
    sleep_seconds=SLEEP_BETWEEN_CALLS_SECONDS,
)

time.sleep(SLEEP_BETWEEN_EXPERIMENTS_SECONDS)

results = run_experiment(
    prefix="hybrid",
    hybrid=True,
    rerank=False,
    sleep_seconds=SLEEP_BETWEEN_CALLS_SECONDS,
)

time.sleep(SLEEP_BETWEEN_EXPERIMENTS_SECONDS)

results = run_experiment(
    prefix="hybrid-rerank",
    hybrid=True,
    rerank=True,
    sleep_seconds=SLEEP_BETWEEN_RERANK_CALLS_SECONDS,
)
