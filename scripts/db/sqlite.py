# Initialize database
import sqlite3

def init_db():
    conn = sqlite3.connect("db/scraper.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS scraped_patterns (
            id TEXT PRIMARY KEY, 
            hash TEXT, 
            last_checked TEXT
        )"""
    )
    conn.commit()
    conn.close()

