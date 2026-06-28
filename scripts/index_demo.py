"""Index the demo Amazon products dataset into Qdrant."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import openai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEMO_FILE = PROJECT_ROOT / "data/demo/meta_Electronics_sample.jsonl"
EMBEDDING_MODEL = "text-embedding-3-small"
VECTOR_SIZE = 1536


def get_settings() -> tuple[str, str, str]:
    openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333").strip()
    collection_name = os.getenv("QDRANT_COLLECTION", "Amazon-items-collection-01").strip()

    if not openai_api_key:
        print("Error: OPENAI_API_KEY is required. Set it in your .env file.")
        sys.exit(1)

    return openai_api_key, qdrant_url, collection_name


def preprocess_item(item: dict) -> str:
    title = item.get("title", "")
    features = item.get("features") or []
    description = item.get("description") or []
    text_parts = [title, " ".join(features), " ".join(description)]
    return " ".join(part for part in text_parts if part).strip()


def extract_image(item: dict) -> str:
    images = item.get("images") or []
    if not images:
        return ""
    return images[0].get("large") or images[0].get("hi_res") or ""


def build_payload(item: dict) -> dict:
    return {
        "preprocessed_description": preprocess_item(item),
        "image": extract_image(item),
        "rating_number": item.get("rating_number"),
        "price": item.get("price"),
        "average_rating": item.get("average_rating"),
        "parent_asin": item.get("parent_asin"),
    }


def get_embedding(text: str) -> list[float]:
    response = openai.embeddings.create(input=text, model=EMBEDDING_MODEL)
    return response.data[0].embedding


def load_demo_items() -> list[dict]:
    if not DEMO_FILE.exists():
        print(f"Error: demo file not found at {DEMO_FILE}")
        sys.exit(1)

    items = []
    with DEMO_FILE.open() as file:
        for line in file:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def index_demo_dataset() -> None:
    openai_api_key, qdrant_url, collection_name = get_settings()
    openai.api_key = openai_api_key

    client = QdrantClient(url=qdrant_url)
    items = load_demo_items()
    payloads = [build_payload(item) for item in items]

    if client.collection_exists(collection_name):
        client.delete_collection(collection_name)

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )

    points = []
    for index, payload in enumerate(payloads):
        embedding = get_embedding(payload["preprocessed_description"])
        points.append(PointStruct(id=index, vector=embedding, payload=payload))

    client.upsert(collection_name=collection_name, points=points)
    print(f"Indexed {len(points)} products into '{collection_name}' at {qdrant_url}")


if __name__ == "__main__":
    index_demo_dataset()
