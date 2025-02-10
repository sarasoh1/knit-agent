import os
import json
import asyncio
import boto3
from dotenv import load_dotenv
import nest_asyncio
from utils.extraction import process_pdfs_batch, process_html_file

nest_asyncio.apply()

load_dotenv()

s3_client = boto3.client("s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

async def process_all_patterns():
    """
    Process all patterns in the S3 bucket, with async HTML processing
    """
    # List all pattern folders
    prefix = "raw/ravelry/"
    all_files = s3_client.list_objects_v2(Bucket=os.getenv("AWS_BUCKET_NAME"), Prefix=prefix)
    
    # Separate PDFs and HTMLs by permalink
    pdf_permalinks = []
    html_permalinks = []
    
    for obj in all_files.get("Contents", []):
        file_key = obj.get("Key")
        extension = file_key.split('.')[-1]
        permalink = file_key.split('/')[-2]
        
        if extension == "json":
            continue
        elif extension == "pdf":
            pdf_permalinks.append(permalink)
        elif extension == "html":
            html_permalinks.append(permalink)

    print(f"Found {len(pdf_permalinks)} PDFs and {len(html_permalinks)} HTMLs to process")
    
    # Process PDFs in batches (synchronously)
    pdf_results = {}
    total_pdfs = len(pdf_permalinks)
    batch_size = min(25, max(5, total_pdfs // 10))
    print(f"Processing {total_pdfs} PDFs in batches of {batch_size}")
    
    for i in range(0, total_pdfs, batch_size):
        batch = pdf_permalinks[i:min(i + batch_size, total_pdfs)]
        if batch:
            batch_results = process_pdfs_batch(batch)
            pdf_results.update(batch_results)
    
    # Process HTMLs asynchronously
    html_tasks = [process_html_file(permalink) for permalink in html_permalinks]
    html_results = await asyncio.gather(*html_tasks)
    
    # Combine results
    all_results = pdf_results.copy()
    for permalink, content in html_results:
        if content is not None:
            all_results[permalink] = content

    print(f"Successfully processed {len(all_results)} patterns")
    return all_results


if __name__ == "__main__":
    patterns = asyncio.run(process_all_patterns())