from database import Database

class Supplier:
    def __init__(self):
        self.db = Database()

    def add_supplier(self, name, contact_person, phone, email, address):
        """Add a new supplier to the database"""
        query = """
            INSERT INTO suppliers (name, contact_person, phone, email, address)
            VALUES (?, ?, ?, ?, ?)
        """
        return self.db.execute_query(query, (name, contact_person, phone, email, address))

    def get_all_suppliers(self):
        """Get all suppliers from the database"""
        query = "SELECT * FROM suppliers ORDER BY name ASC"
        return self.db.execute_query(query)

    def get_supplier(self, supplier_id):
        """Get a specific supplier by ID"""
        query = "SELECT * FROM suppliers WHERE supplier_id = ?"
        results = self.db.execute_query(query, (supplier_id,))
        return results[0] if results else None

    def update_supplier(self, supplier_id, **kwargs):
        """Update supplier information"""
        if not kwargs:
            return False
            
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
            
        values.append(supplier_id)
        query = f"UPDATE suppliers SET {', '.join(fields)} WHERE supplier_id = ?"
        return self.db.execute_query(query, tuple(values))

    def delete_supplier(self, supplier_id):
        """Delete a supplier"""
        query = "DELETE FROM suppliers WHERE supplier_id = ?"
        return self.db.execute_query(query, (supplier_id,))
