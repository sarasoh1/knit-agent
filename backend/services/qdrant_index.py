from pydantic import BaseModel
from llama_index.core.indices.vector_store.base import VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from backend.config.settings import config


# Connect to your Qdrant instance
class QdrantIndex(BaseModel):
    qdrant_url: str
    api_key: str

    def setup(self) -> VectorStoreIndex:
        """
        Sets up Qdrant vector base for querying

        Returns:
            BaseIndex: qdrant db index
        """
        vector_store = QdrantVectorStore(
            collection_name="patterns",
            url=config.get("QDRANT_URL"),
            api_key=config.get("QDRANT_API_KEY"),
        )
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
        print("index:", index.vector_store)
        return index


QDRANT_INDEX_TOOL = QdrantIndex(
    qdrant_url=config.get("QDRANT_URL"), api_key=config.get("QDRANT_API_KEY")
).setup()
