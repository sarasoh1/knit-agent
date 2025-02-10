import os
import json
import boto3
import requests
from dotenv import load_dotenv

load_dotenv()

S3_BUCKET = os.getenv("AWS_BUCKET_NAME")
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)


def save_json_to_s3(data: dict, permalink: str):
    """

    Save data to S3 (optional).
    """
    key = f"raw/ravelry/{permalink}/{permalink}.json"
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=json.dumps(data),
    )
    print(f"Saved data to S3: {permalink}")


def save_file_to_s3(file_url: str, extension: str, permalink: str):
    """
    Save a file to S3
    """
    file_response = requests.get(file_url, timeout=20)
    key = f"raw/ravelry/{permalink}/{permalink}.{extension}"
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=file_response.content,
    )
    print(f"Saved file to S3: {permalink}")
