import sqlite3
import hashlib
import json
from datetime import datetime, timezone

# Function to hash API response
def compute_hash(data: dict):
    """
    Compute the hash of the pattern

    Args:
        data (Pattern): pattern object

    Returns:
        str: The hash of the pattern
    """
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

# Check if data has changed
def data_has_changed(item_permalink, new_hash):
    """
    Check if the data has changed

    Args:
        item_id (str): the id of the pattern
        new_hash (str): the new hash of the pattern

    Returns:
        bool: True if the data has changed, False otherwise
    """
    conn = sqlite3.connect("db/scraper.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT hash FROM scraped_patterns WHERE id = ?", (item_permalink,))
    result = cursor.fetchone()
    
    conn.close()
    
    # If no existing record, it's new data
    if not result:
        return True  
    # If the hash is different, data has changed
    return result[0] != new_hash  

# Store new hash in database
def update_database(item_permalink: str, new_hash: str):
    """
    Updating database with latest hash for a given id
    """
    conn = sqlite3.connect("db/scraper.db")
    cursor = conn.cursor()
    
    cursor.execute(
        """INSERT INTO scraped_patterns (id, hash, last_checked) 
        VALUES (?, ?, ?) 
        ON CONFLICT(id) DO UPDATE 
        SET hash = excluded.hash, last_checked = excluded.last_checked""",
        (item_permalink, new_hash, datetime.now(timezone.utc).isoformat())
    )
    
    conn.commit()
    conn.close()

# # Fetch data from API
# def scrape_api():
#     API_URL = "https://jsonplaceholder.typicode.com/posts"  # Replace with actual API
#     response = requests.get(API_URL)
    
#     if response.status_code == 200:
#         return response.json()
#     return None

# # Main function
# def main():
#     init_db()  # Ensure database exists
#     data = scrape_api()
    
#     if data:
#         for item in data:
#             item_id = str(item["id"])  # Unique ID from API
#             new_hash = compute_hash(item)
            
#             if data_has_changed(item_id, new_hash):
#                 print(f"🔄 Data updated for ID {item_id}. Storing new hash.")
#                 update_database(item_id, new_hash)
#             else:
#                 print(f"✅ No changes for ID {item_id}. Skipping update.")
#     else:
#         print("❌ Failed to fetch data from API.")

# # Run the script
# if __name__ == "__main__":
#     main()
