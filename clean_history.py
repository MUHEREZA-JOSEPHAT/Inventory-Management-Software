import sqlite3
import re

def clean_database():
    db_path = 'D:/inventory management system/inventory.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Fetch all supplier messages
    cursor.execute("SELECT comm_id, message FROM supplier_communications WHERE sender_type = 'Supplier'")
    rows = cursor.fetchall()
    
    count = 0
    for cid, msg in rows:
        lines = msg.splitlines()
        clean_lines = []
        
        # Standard reply markers
        split_markers = ["On ", "From: ", "---", "Sent from my"]
        
        for line in lines:
            trimmed = line.strip()
            # Stop taking lines if we hit a reply header
            if any(trimmed.startswith(m) for m in split_markers) and ("wrote:" in trimmed or ":" in trimmed):
                break
            
            # Skip quoted lines (both standard > and html-style &gt;)
            if trimmed.startswith(">") or trimmed.startswith("&gt;"):
                continue
                
            clean_lines.append(line)
            
        cleaned_msg = "\n".join(clean_lines).strip()
        
        # Update if changed
        if cleaned_msg and cleaned_msg != msg.strip():
            cursor.execute("UPDATE supplier_communications SET message = ? WHERE comm_id = ?", (cleaned_msg, cid))
            count += 1
            
    conn.commit()
    print(f"Cleaned {count} existing messages.")
    conn.close()

if __name__ == "__main__":
    clean_database()
