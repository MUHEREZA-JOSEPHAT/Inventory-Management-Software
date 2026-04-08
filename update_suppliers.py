import sqlite3
import os

def update_suppliers():
    db_path = 'D:/inventory management system/inventory.db'
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    test_email = 'muhereza.josephat@stud.ndejjeuniversity.ac.ug'
    target_suppliers = ['Fresh Farms Co.', 'Global Foods Ltd']
    
    query = "UPDATE suppliers SET email = ? WHERE name = ?"
    
    updated_count = 0
    for name in target_suppliers:
        cursor.execute(query, (test_email, name))
        if cursor.rowcount > 0:
            updated_count += 1
            print(f"Updated {name} -> {test_email}")
        else:
            print(f"Supplier '{name}' not found or email already matches.")
            
    conn.commit()
    print(f"Total suppliers updated: {updated_count}")
    conn.close()

if __name__ == "__main__":
    update_suppliers()
