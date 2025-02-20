import os
from typing import List
import boto3
import trafilatura
from dotenv import load_dotenv
import re
from s3fs import S3FileSystem
from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader
from llama_index.core.extractors import (
    TitleExtractor,
    SummaryExtractor,
    KeywordExtractor,
)

from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from utils.text_embedding_generator import EMBEDDING_GENERATOR
from utils.qdrant import init_qdrant

load_dotenv()

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)


def process_pdfs_batch(permalinks: List[str]) -> dict:
    """
    Process all PDF files in a batch using SimpleDirectoryReader
    """
    llamaparse = LlamaParse(
        api_key=os.getenv("LLAMAINDEX_API_KEY2"), segment_sentences=True
    )
    s3_fs = S3FileSystem(anon=False, endpoint_url=None)
    qdrant_client = init_qdrant()
    vector_store = QdrantVectorStore(client=qdrant_client, collection_name="patterns")
    pipeline = IngestionPipeline(
        transformations=[
            SentenceSplitter(chunk_size=512, chunk_overlap=50),
            TitleExtractor(),
            SummaryExtractor(summaries=["prev", "self"]),
            KeywordExtractor(keywords=10),
            OpenAIEmbedding(api_key=os.getenv("OPENAI_API_KEY")),
        ],
        vector_store=vector_store,
    )

    try:
        # Update reader input directory to include all relevant PDFs
        pdf_paths = [
            f"{os.getenv('AWS_BUCKET_NAME')}/raw/ravelry/{p}/{p}.pdf"
            for p in permalinks
        ]
        reader = SimpleDirectoryReader(
            input_dir=os.getenv("AWS_BUCKET_NAME"),
            input_files=pdf_paths,
            file_extractor={".pdf": llamaparse},
            fs=s3_fs,
            filename_as_id=True,
        )
        documents = reader.load_data()

        pipeline.run(documents=documents)

    except Exception as e:
        print(f"Error processing PDF batch: {e}")
        print(f"Permalinks in failed batch: {permalinks}")


async def process_html_file(permalink: str) -> tuple[str, str]:
    """
    Process a single HTML file asynchronously
    """
    try:
        html_key = f"raw/ravelry/{permalink}/{permalink}.html"
        html_file = s3_client.get_object(
            Bucket=os.getenv("AWS_BUCKET_NAME"), Key=html_key
        )
        text = html_file.get("Body").read().decode("utf-8")

        # Trafilatura is synchronous but lightweight enough to not block
        pattern = trafilatura.extract(
            text, include_comments=False, favor_precision=True, deduplicate=True
        )

        # Write to s3
        processed_html_key = f"processed/ravelry/{permalink}/{permalink}.txt"
        s3_client.put_object(
            Bucket=os.getenv("AWS_BUCKET_NAME"), Key=processed_html_key, Body=pattern
        )
        return (permalink, pattern)
    except Exception as e:
        print(f"Error processing HTML for {permalink}: {e}")
        return (permalink, None)


def clean_text(text: str) -> str:
    text = re.sub(r"\n+", "\n", text)  # Normalize multiple newlines
    text = re.sub(r"([a-zA-Z])- \n([a-zA-Z])", r"\1\2", text)  # Fix hyphenation
    text = re.sub(r"\s+", " ", text)  # Collapse multiple spaces
    return text.strip()
