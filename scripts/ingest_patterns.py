import os
import boto3
import uuid
import json
from dotenv import load_dotenv
from models.pattern import Pattern
from db.cache import fetch_latest_processed_patterns
from utils.qdrant import init_qdrant, upsert_to_qdrant
from utils.text_embedding_generator import EMBEDDING_GENERATOR

load_dotenv()

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

qdrant_client = init_qdrant()


def generate_stable_uuid(string_input):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, string_input))


def ingest_patterns():
    
    patterns_to_process = fetch_latest_processed_patterns()
    data_to_upsert = []
    for permalink in patterns_to_process:
        try:
            file_key = f"processed/ravelry/{permalink}/{permalink}.txt"
            metadata_key = f"raw/ravelry/{permalink}/{permalink}.json"

            metadata_dict = json.loads(
                s3_client.get_object(Bucket=os.getenv("AWS_BUCKET_NAME"), Key=metadata_key)[
                    "Body"
                ]
                .read()
                .decode("utf-8")
            )

            # Clean needle size
            if any(metadata_dict["gauge"]["pattern_needle_sizes"]):
                metadata_dict["gauge"]["pattern_needle_sizes"] = [
                    needle_size
                    for needle_size in metadata_dict["gauge"]["pattern_needle_sizes"]
                    if needle_size is not None
                ]
            else:
                metadata_dict["gauge"]["pattern_needle_sizes"] = None

            metadata = Pattern(**metadata_dict)
            print("filekey:", file_key)
            pattern = (
                s3_client.get_object(Bucket=os.getenv("AWS_BUCKET_NAME"), Key=file_key)[
                    "Body"
                ]
                .read()
                .decode("utf-8")
            )
            embedding = EMBEDDING_GENERATOR.get_document_embeddings(pattern)
            data_to_upsert.append(
                {
                    "id": generate_stable_uuid(permalink),
                    "metadata": {
                        "craft": metadata.craft,
                        "pattern_attributes": [attr.permalink.lower() for attr in metadata.pattern_attributes],
                        "pattern_categories": [attr.permalink.lower() for attr in metadata.pattern_categories],
                        "gauge": metadata.gauge,
                        "ratings": metadata.ratings,
                        "permalink": metadata.permalink,
                        "yarn_weight": metadata.gauge.map_yarn_weight()
                    },
                    "embedding": embedding,
                }
            )
        except Exception as e:
            print(f"Error processing {permalink}, {e}")

    upsert_to_qdrant(qdrant_client, data_to_upsert)
    return data_to_upsert



if __name__ == "__main__":
    init_qdrant()
    patterns = ingest_patterns()
    # print(patterns[0].get("embedding"))
    print("Patterns ingested: ", len(patterns))
