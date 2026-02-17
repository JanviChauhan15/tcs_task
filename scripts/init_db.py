import sqlite3
import os

DB_FILE = "data/database.sqlite"

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        return conn
    except Exception as e:
        print(e)
    return conn

def create_table(conn):
    create_customers_table = """
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT,
        membership_level TEXT
    );
    """
    
    create_tickets_table = """
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        issue_description TEXT NOT NULL,
        status TEXT NOT NULL,
        resolution_notes TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    );
    """
    
    try:
        c = conn.cursor()
        c.execute(create_customers_table)
        c.execute(create_tickets_table)
    except Exception as e:
        print(e)

def insert_dummy_data(conn):
    customers = [
        (1, 'Ema Stone', 'ema.stone@example.com', '555-0101', 'Gold'),
        (2, 'John Doe', 'john.doe@example.com', '555-0102', 'Silver'),
        (3, 'Alice Smith', 'alice.smith@example.com', '555-0103', 'Platinum')
    ]
    
    tickets = [
        (1, 1, 'Login fails after password reset', 'Open', None, '2023-10-25 10:00:00'),
        (2, 1, 'Billing query for October', 'Closed', 'Refund processed', '2023-10-20 14:30:00'),
        (3, 2, 'Feature request: Dark mode', 'Pending', None, '2023-10-26 09:15:00'),
        (4, 3, 'App crashes on startup', 'Resolved', 'Cleared cache', '2023-10-24 16:45:00')
    ]
    
    c = conn.cursor()
    c.executemany("INSERT OR IGNORE INTO customers VALUES (?,?,?,?,?)", customers)
    c.executemany("INSERT OR IGNORE INTO tickets VALUES (?,?,?,?,?,?)", tickets)
    conn.commit()

def main():
    if not os.path.exists("data"):
        os.makedirs("data")
        
    conn = create_connection()
    if conn is not None:
        create_table(conn)
        insert_dummy_data(conn)
        print("Database initialized successfully.")
        conn.close()
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()
