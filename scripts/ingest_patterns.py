import os
import boto3
import uuid
import json
from dotenv import load_dotenv
from models.pattern import Pattern
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
    response = s3_client.list_objects_v2(
        Bucket=os.getenv("AWS_BUCKET_NAME"), Prefix="processed/ravelry/"
    )
    data_to_upsert = []
    for obj in response["Contents"]:

        permalink = obj["Key"].split("/")[-2]
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

        pattern = (
            s3_client.get_object(Bucket=os.getenv("AWS_BUCKET_NAME"), Key=obj["Key"])[
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
                    "pattern_attributes": metadata.pattern_attributes,
                    "pattern_categories": metadata.pattern_categories,
                    "gauge": metadata.gauge,
                    "ratings": metadata.ratings,
                    "permalink": metadata.permalink,
                },
                "embedding": embedding,
            }
        )

    upsert_to_qdrant(qdrant_client, data_to_upsert)
    return data_to_upsert


if __name__ == "__main__":
    init_qdrant()
    patterns = ingest_patterns()
    # print(patterns[0].get("embedding"))
    print("Patterns ingested: ", len(patterns))
