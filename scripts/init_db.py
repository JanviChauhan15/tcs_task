import sqlite3
import os

DB_PATH = "data/database.sqlite"
SEED_PATH = "data/seed.sql"

def init_db():
    if not os.path.exists("data"):
        os.makedirs("data")
        
    print(f"Initializing database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    with open(SEED_PATH, "r") as f:
        sql_script = f.read()
        
    try:
        cursor.executescript(sql_script)
        conn.commit()
        print("Database initialized successfully with seed data.")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
