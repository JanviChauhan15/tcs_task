import sqlite3
from typing import Any, List, Dict, Union
from langchain_core.tools import tool

# Adjusted path to match existing project structure
DB_PATH = "data/database.sqlite"

def _rows_to_dicts(cursor, rows) -> List[Dict[str, Any]]:
    cols = [c[0] for c in cursor.description] if cursor.description else []
    return [dict(zip(cols, r)) for r in rows]

# Schema Definitions
CUSTOMERS_COLUMNS = ["id", "name", "email", "phone", "account_status", "created_at"]
TICKETS_COLUMNS = ["id", "customer_id", "subject", "description", "status", "priority", "created_at", "resolved_at"]

def _validate_columns(query: str) -> Union[bool, str]:
    """Basic validation to check if query references non-existent columns."""
    q_lower = query.lower()
    
    # Check customers columns
    if "customers" in q_lower:
        for word in q_lower.replace(",", " ").replace("(", " ").replace(")", " ").split():
            # Simple heuristic: if it looks like a column usage and isn't a keyword
            # This is hard to do perfectly with regex without a parser, 
            # but we can look for specific common mistakes like 'status' instead of 'account_status'
            if word == "status" and "account_status" not in q_lower and "tickets" not in q_lower:
               return "Error: 'status' is not a valid column for customers. Did you mean 'account_status'?"
            
    return True

@tool
def query_sql_db(query: str) -> str:
    """
    Run a READ-ONLY SQL query on the support SQLite DB.
    
    SCHEMA:
    - customers(id, name, email, phone, account_status, created_at)
    - tickets(id, customer_id, subject, description, status, priority, created_at, resolved_at)
    
    CRITICAL: 
    - Use 'account_status' for customers (Values: 'Active', 'Suspended').
    - Only SELECT queries are allowed.
    """
    q = query.strip().lower()
    if not q.startswith("select"):
        return "ERROR: Only SELECT queries are allowed."

    # Pre-validation
    validation = _validate_columns(query)
    if validation is not True:
        return validation

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = None
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        data = _rows_to_dicts(cur, rows)
        return str(data)
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {e}"

@tool
def get_customer_profile(name_query: str) -> str:
    """
    Retrieves a full customer profile including contact details and ticket history.
    Use this tool when asked for a customer overview, profile, or history.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # 1. Find Customer
        # Basic fuzzy search
        cur.execute("SELECT * FROM customers WHERE name LIKE ? OR email LIKE ?", (f"%{name_query}%", f"%{name_query}%"))
        customers = [dict(row) for row in cur.fetchall()]
        
        if not customers:
            conn.close()
            return str({"error": "No matching customer found in the database."})
            
        if len(customers) > 1:
            conn.close()
            return str({"error": f"Found {len(customers)} customers matching '{name_query}'. Please be more specific.", "matches": [c['name'] for c in customers]})
            
        customer = customers[0]
        customer_id = customer['id']
        
        # 2. Find Tickets
        cur.execute("SELECT * FROM tickets WHERE customer_id = ? ORDER BY created_at DESC", (customer_id,))
        tickets = [dict(row) for row in cur.fetchall()]
        
        # 3. Calculate Summary Stats
        total_tickets = len(tickets)
        open_tickets = sum(1 for t in tickets if t['status'] == 'Open')
        closed_tickets = sum(1 for t in tickets if t['status'] == 'Closed')
        high_priority = sum(1 for t in tickets if t['priority'] == 'High')
        
        conn.close()
        
        # 4. Construct Result
        result = {
            "customer": customer,
            "tickets": tickets, # All tickets
            "summary": {
                "total": total_tickets,
                "open": open_tickets,
                "closed": closed_tickets,
                "high_priority": high_priority
            },
            "_meta": {
                "customer_query": f"SELECT * FROM customers WHERE name LIKE '%{name_query}%'",
                "ticket_query": f"SELECT * FROM tickets WHERE customer_id = {customer_id} ORDER BY created_at DESC"
            }
        }
        
        return str(result)
        
    except Exception as e:
        return f"ERROR: {type(e).__name__}: {e}"
    finally:
        if 'conn' in locals():
            conn.close()
