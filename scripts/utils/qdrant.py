import os
import qdrant_client
from dotenv import load_dotenv

load_dotenv()

qdrant_client = qdrant_client.QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

def upsert_to_qdrant(patterns: dict):
    for permalink, content in patterns.items():
        qdrant_client.upsert(
            collection_name="patterns",
            points=[{"id": permalink, "text": content}]
        )
