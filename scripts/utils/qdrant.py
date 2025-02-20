from typing import List
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

load_dotenv()
# TODO: Write a qdrant client that can be used by other scripts


def init_qdrant():
    qdrant_client = QdrantClient(
        url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY")
    )

    try:
        # Create new collection with correct vector size (1536 for OpenAI embeddings)
        qdrant_client.create_collection(
            collection_name="patterns",
            vectors_config=VectorParams(
                size=1536,  # Updated to match your embedding dimension
                distance=Distance.COSINE,
            ),
        )
    except Exception:
        print("collection already created!")

    return qdrant_client


def upsert_to_qdrant(qdrant_client, patterns: List[dict]):
    qdrant_client.upsert(
        collection_name="patterns",
        points=[
            PointStruct(
                id=pattern["id"],
                vector=pattern["embedding"],
                payload=pattern["metadata"],
            )
            for pattern in patterns
        ],
    )
