import sqlite3

def migrate():
    db_path = 'D:/inventory management system/inventory.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE supplier_communications ADD COLUMN attachments TEXT")
        conn.commit()
        print("Database migration successful: added 'attachments' column.")
    except Exception as e:
        print(f"Migration note: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
