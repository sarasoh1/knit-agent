import os
import json
import time
import asyncio
import boto3
from dotenv import load_dotenv
import nest_asyncio
from utils.extraction import process_pdfs_batch, process_html_file
from db.cache import fetch_latest_processed_patterns

nest_asyncio.apply()

load_dotenv()

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)


async def process_all_patterns():
    """
    Process all patterns in the S3 bucket, with async HTML processing
    """
    # List all pattern folders
    prefix = "raw/ravelry/"

    # TODO: Want to only process new patterns, not all of them
    # Get the latest processed patterns from the database
    latest_processed_patterns = fetch_latest_processed_patterns()

    # Separate PDFs and HTMLs by permalink
    pdf_permalinks = []
    # html_permalinks = []

    for permalink in latest_processed_patterns:
        # file_key = key.get("Key")
        file_key = s3_client.list_objects_v2(
            Bucket=os.getenv("AWS_BUCKET_NAME"), Prefix=f"{prefix}{permalink}"
        )
        for obj in file_key.get("Contents", []):
            extension = obj.get("Key").split(".")[-1]

            if extension == "pdf":
                pdf_permalinks.append(permalink)

    print(f"Found {len(pdf_permalinks)} PDFs to process")

    total_pdfs = len(pdf_permalinks)
    batch_size = min(25, max(5, total_pdfs // 10))
    print(f"Processing {total_pdfs} PDFs in batches of {batch_size}")

    for i in range(0, total_pdfs, batch_size):
        batch = pdf_permalinks[i : min(i + batch_size, total_pdfs)]
        if batch:
            process_pdfs_batch(batch)
            time.sleep(9 * batch_size)

    print(f"Successfully processed {len(pdf_permalinks)} patterns")
    # return all_results


if __name__ == "__main__":
    asyncio.run(process_all_patterns())
