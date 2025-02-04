import os
import json
import asyncio
import boto3
from typing import List, Dict
from dotenv import load_dotenv
from models.pattern import Pattern

load_dotenv()

S3_BUCKET = os.getenv("AWS_BUCKET_NAME")
s3_client = boto3.client("s3",
                        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                        region_name=os.getenv("AWS_REGION"))

def retrieve_pattern_file(permalink: str) -> None:
    """
    Retrieve a pattern file from S3 and save it to s3 files directory.
    """
    key = f"raw/ravelry/{permalink}.json"
    response = s3_client.get_object(Bucket=S3_BUCKET, Key=key)
    pattern_json = response['Body'].read().decode('utf-8')
    pattern = Pattern(**pattern_json)


    with open(f"s3_files/{permalink}.json", "w") as f:
        f.write(content)


async def fetch_s3_object(key: str) -> Dict:
    """
    Fetch a single object from S3 asynchronously
    """
    loop = asyncio.get_event_loop()
    try:
        response = await loop.run_in_executor(
            None,
            lambda: s3_client.get_object(Bucket=S3_BUCKET, Key=key)
        )
        content = await loop.run_in_executor(
            None,
            lambda: json.loads(response['Body'].read().decode('utf-8'))
        )
        return content
    except Exception as e:
        print(f"Error fetching object {key}: {e}")
        return None

async def fetch_all_s3_objects(prefix: str = "raw/ravelry/") -> List[Dict]:
    """
    Fetch all objects from S3 with the given prefix concurrently
    """
    try:
        # List all objects with the given prefix
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix)
        
        all_keys = []
        async for page in pages:
            if 'Contents' in page:
                all_keys.extend([obj['Key'] for obj in page['Contents']])
        
        # Fetch all objects concurrently
        tasks = [fetch_s3_object(key) for key in all_keys]
        results = await asyncio.gather(*tasks)
        
        # Filter out None results from failed fetches
        return [r for r in results if r is not None]
        
    except Exception as e:
        print(f"Error fetching objects from S3: {e}")
        return []

def ingest_data():
    """
    Ingest data from S3 into a database.
    """
