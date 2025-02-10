import os
from typing import List, Dict, Any
import time
import openai
from tenacity import retry, stop_after_attempt, wait_exponential
import tiktoken  

class TextEmbeddingGenerator:
    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        chunk_size: int = 8000,
        chunk_overlap: int = 200
    ):
        """
        Initialize the embedding generator with OpenAI credentials and parameters.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI embedding model to use
            chunk_size: Maximum number of tokens per chunk
            chunk_overlap: Number of overlapping tokens between chunks
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.encoding_for_model(model)

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks based on token count with overlap.
        
        Args:
            text: Input text to be chunked
            
        Returns:
            List of text chunks
        """
        tokens = self.encoding.encode(text)
        chunks = []
        
        start_idx = 0
        while start_idx < len(tokens):
            # Find end index for current chunk
            end_idx = start_idx + self.chunk_size
            
            if end_idx >= len(tokens):
                chunks.append(self.encoding.decode(tokens[start_idx:]))
                break
                
            # Move end index to nearest sentence boundary if possible
            decode_chunk = self.encoding.decode(tokens[start_idx:end_idx])
            last_period = decode_chunk.rfind('.')
            if last_period != -1:
                # Adjust end_idx to match token boundary after the period
                partial_chunk = decode_chunk[:last_period + 1]
                end_idx = start_idx + len(self.encoding.encode(partial_chunk))
            
            chunks.append(self.encoding.decode(tokens[start_idx:end_idx]))
            start_idx = end_idx - self.chunk_overlap
            
        return chunks

    @retry(wait=wait_exponential(min=1, max=60), stop=stop_after_attempt(5))
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embeddings for a single text chunk using OpenAI's API.
        Includes retry logic for API failures.
        
        Args:
            text: Text chunk to embed
            
        Returns:
            List of embedding values
        """
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            raise

    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for multiple text chunks.
        
        Args:
            texts: List of text chunks to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for chunk in texts:
            embedding = self.get_embedding(chunk)
            embeddings.append(embedding)
            # Simple rate limiting
            time.sleep(0.1)
        return embeddings

    def process_large_text(self, text: str) -> Dict[str, Any]:
        """
        Process large text by chunking and generating embeddings.
        
        Args:
            text: Input text to process
            
        Returns:
            Dictionary containing chunks and their embeddings
        """
        chunks = self.chunk_text(text)
        embeddings = self.get_embeddings_batch(chunks)
        
        return {
            'chunks': chunks,
            'embeddings': embeddings,
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'model': self.model
        }
    
EMBEDDING_GENERATOR = TextEmbeddingGenerator(os.getenv("OPENAI_API_KEY"))
