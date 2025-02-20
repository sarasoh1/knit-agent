from pydantic import BaseModel
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.llms.openai import OpenAI
from backend.services.qdrant_index import QDRANT_INDEX_TOOL
from backend.models.pattern_query import PatternQuery
from backend.config.settings import config

llm = OpenAI(model="gpt-4o", api_key=config.get("OPENAI_API_KEY"))


class ChatSession(BaseModel):
    sessionId: str
    requirements: PatternQuery

    @property
    def qdrant_retriever(self) -> RetrieverQueryEngine:
        """
        Create the retriever for Qdrant vector database
        """
        retriever = VectorIndexRetriever(
            index=QDRANT_INDEX_TOOL,
            similarity_top_k=2,
            # filters = self.requirements.create_pattern_query_filters()
        )
        query_engine = RetrieverQueryEngine(retriever=retriever)
        return query_engine

    async def query_qdrant_engine(self, query: str):
        """
        sets up the query engine for every chat session

        Args:
            query (str): query given to the set of patterns

        Returns:
            _type_: _description_
        """
        # return QDRANT_INDEX_TOOL.as_query_engine(llm=llm).query(query)
        return self.qdrant_retriever.query(query)
