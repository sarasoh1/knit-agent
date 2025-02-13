import os
import httpx
import asyncio
from typing import List, Dict
import boto3
from dotenv import load_dotenv
from urllib.parse import quote
from utils.preprocess import preprocess_pattern, check_pattern_url_is_active
from models.pattern import Pattern
from db.cache import compute_hash, data_has_changed, update_database
from db.sqlite import init_db
from utils.aws import save_json_to_s3, save_file_to_s3

load_dotenv()

# Ravelry API configuration
RAVELRY_API_URL = os.getenv("RAVELRY_API_URL")
RAVELRY_AUTH = (
    os.getenv("RAVELRY_PERSONAL_USERNAME"),
    os.getenv("RAVLERY_PASSWORD_KEY"),
)
RATE_LIMIT = 5  # Max requests per second (adjust based on Ravelry's rate limits)

S3_BUCKET = os.getenv("AWS_BUCKET_NAME")
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)


async def fetch_patterns(
    client: httpx.AsyncClient, page: int, query: str
) -> List[Dict]:
    """
    Fetch a page of patterns from Ravelry's API for a specific category.
    In the first iteration, we will only fetch free patterns that are written in english.
    """
    patterns_url = RAVELRY_API_URL + "/patterns/search.json"
    patterns = []
    try:

        # Get patterns from Ravelry
        response = await client.get(
            patterns_url,
            auth=RAVELRY_AUTH,
            params={
                "query": query,
                "page": page,
                "page_size": 100,  # Adjust page_size as needed
            },
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        json_patterns = response.json()["patterns"]

        # Search for each pattern
        for pattern in json_patterns:
            pattern_response = await client.get(
                RAVELRY_API_URL + f"/patterns/{pattern['id']}.json", auth=RAVELRY_AUTH
            )
            pattern_response.raise_for_status()
            pattern_json = pattern_response.json()["pattern"]
            print(pattern_json)
            available_languages = [
                language["code"] for language in pattern_json["languages"]
            ]

            if pattern_json["free"] and "en" in available_languages:
                try:
                    pattern_hash = compute_hash(pattern_json)
                    if data_has_changed(pattern_json["permalink"], pattern_hash):
                        cleaned_pattern = Pattern(**preprocess_pattern(pattern_json))
                        extension, file_url = cleaned_pattern.retrieve_pattern_url()
                        update_database(
                            cleaned_pattern.permalink, pattern_hash
                        )  # Update the database so that we won't scrape the same pattern again
                        if check_pattern_url_is_active(file_url):
                            save_json_to_s3(
                                cleaned_pattern.model_dump(), cleaned_pattern.permalink
                            )
                            save_file_to_s3(
                                file_url, extension, cleaned_pattern.permalink
                            )
                            patterns.append(cleaned_pattern)
                except Exception as e:
                    print(f"Error processing pattern {pattern_json['permalink']}: {e}")

        return patterns

    except httpx.HTTPStatusError as e:
        print(f"Error fetching page {page} for category {query}: {e}")
        return []


async def fetch_all_patterns(max_pages: int) -> List[Dict]:
    """
    Fetch all patterns from Ravelry's API with rate limiting.
    Reads categories from to_scrape.txt and fetches patterns for each category.
    """
    patterns = []

    # Read categories from to_scrape.txt
    with open("to_scrape_trunc.txt", "r", encoding="utf-8") as f:
        categories = [line.strip() for line in f if line.strip()]

    async with httpx.AsyncClient() as client:
        for category in categories:
            category = quote(category)
            print(f"Fetching patterns for category: {category}")
            tasks = []
            for page in range(1, max_pages + 1):
                tasks.append(fetch_patterns(client, page, category))
                if len(tasks) >= RATE_LIMIT:
                    # Wait for the current batch of tasks to complete
                    results = await asyncio.gather(*tasks)
                    patterns.extend([p for result in results for p in result])
                    tasks = []
                    await asyncio.sleep(2)  # Respect rate limits

            # Fetch any remaining tasks for this category
            if tasks:
                results = await asyncio.gather(*tasks)
                patterns.extend([p for result in results for p in result])

    return patterns


async def main():
    """
    Main function to scrape Ravelry and save data.
    """
    init_db()
    max_pages = 2  # Adjust based on how many pages you want to fetch
    patterns = await fetch_all_patterns(max_pages)

    print(f"Fetched {len(patterns)} patterns.")


if __name__ == "__main__":
    asyncio.run(main())
