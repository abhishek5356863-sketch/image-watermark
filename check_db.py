import os
import tempfile
import sqlite3

db_path = os.path.join(tempfile.gettempdir(), 'stealthguard_v2.db')
print(f"DB Path: {db_path}")

if not os.path.exists(db_path):
    print("Database does not exist.")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, email, password_hash FROM user")
        rows = cursor.fetchall()
        print(f"Total users: {len(rows)}")
        for row in rows:
            print(row)
    except Exception as e:
        print(f"Error querying db: {e}")
    finally:
        conn.close()
