import boto3
import os
import trafilatura
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader
from typing import List
import re
from llama_parse import LlamaParse
from s3fs import S3FileSystem
from utils.text_embedding_generator import EMBEDDING_GENERATOR

load_dotenv()

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

llamaparse = LlamaParse(api_key=os.getenv("LLAMAINDEX_API_KEY"), segment_sentences=True)
s3_fs = S3FileSystem(anon=False, endpoint_url=None)


def process_pdfs_batch(permalinks: List[str]) -> dict:
    """
    Process all PDF files in a batch using SimpleDirectoryReader
    """
    results = {}
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
        )
        documents = reader.load_data()

        # Group results by permalink with safer path parsing
        for doc in documents:
            try:
                permalink = doc.metadata.get("file_path").split("/")[-2]
                results[permalink] = clean_text(doc.text)
                s3_client.put_object(
                    Bucket=os.getenv("AWS_BUCKET_NAME"),
                    Key=f"processed/ravelry/{permalink}/{permalink}.txt",
                    Body=results[permalink],
                )
                print(f"Successfully processed {permalink}")
            except Exception as e:
                print(f"Error processing document {doc.id_}: {e}")
                continue

        return results
    except Exception as e:
        print(f"Error processing PDF batch: {e}")
        print(f"Permalinks in failed batch: {permalinks}")
        return results


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


def get_pattern_embedding(pattern_text: str):
    """
    Get the embedding of a pattern text
    """
    try:
        if pattern_text:
            embedding = EMBEDDING_GENERATOR.process_large_text(pattern_text)
            return embedding
        else:
            print("Skipping embedding")
    except Exception as e:
        print(f"Error getting pattern embedding: {e}")
        return None
