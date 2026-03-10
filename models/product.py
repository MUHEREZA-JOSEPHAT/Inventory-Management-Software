from database import Database
from datetime import datetime

class Product:
    def __init__(self):
        self.db = Database()

    def add_product(self, name, quantity, price, reorder_point, unit='piece'):
        """Add a new product to the database"""
        query = '''
            INSERT INTO products (name, price, reorder_point, unit, quantity)
            VALUES (?, ?, ?, ?, ?)
        '''
        params = (name, price, reorder_point, unit, quantity)
        self.db.execute_query(query, params)
        return self.db.get_last_row_id()

    def _initialize_inventory(self, product_id):
        """Initialize inventory record for a new product"""
        query = '''
            INSERT INTO inventory (product_id, quantity)
            VALUES (?, 0)
        '''
        self.db.execute_query(query, (product_id,))

    def get_product(self, product_id):
        """Get product details by ID"""
        query = '''
            SELECT p.* 
            FROM products p
            WHERE p.product_id = ?
        '''
        result = self.db.execute_query(query, (product_id,))
        return result[0] if result else None

    def get_all_products(self):
        """Get all products"""
        # First verify the table structure
        self.db.cursor.execute("PRAGMA table_info(products)")
        columns = {row[1]: row[0] for row in self.db.cursor.fetchall()}
        
        # Ensure we select columns in the correct order
        query = '''
            SELECT 
                p.product_id,
                p.name,
                CAST(p.quantity AS INTEGER) as quantity,
                p.price,
                p.reorder_point,
                p.unit,
                p.created_at
            FROM products p
            ORDER BY p.name
        '''
        return self.db.execute_query(query)

    def update_product(self, product_id, name=None, price=None, reorder_point=None, unit=None, quantity=None):
        """Update product details"""
        current = self.get_product(product_id)
        if not current:
            return False

        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if price is not None:
            updates.append("price = ?")
            params.append(price)
        if reorder_point is not None:
            updates.append("reorder_point = ?")
            params.append(reorder_point)
        if unit is not None:
            updates.append("unit = ?")
            params.append(unit)
        if quantity is not None:
            updates.append("quantity = ?")
            params.append(quantity)

        if not updates:
            return False

        query = f'''
            UPDATE products 
            SET {', '.join(updates)}
            WHERE product_id = ?
        '''
        params.append(product_id)
        
        return self.db.execute_query(query, tuple(params)) > 0

    def update_quantity(self, product_id, quantity_change):
        """Update product quantity"""
        query = '''
            UPDATE products 
            SET quantity = quantity + ?
            WHERE product_id = ?
        '''
        return self.db.execute_query(query, (quantity_change, product_id)) > 0

    def delete_product(self, product_id):
        """Delete a product and its associated inventory"""
        # First delete inventory record
        self.db.execute_query("DELETE FROM inventory WHERE product_id = ?", (product_id,))
        # Then delete product
        return self.db.execute_query("DELETE FROM products WHERE product_id = ?", (product_id,)) > 0

    def get_low_stock_products(self):
        """Get products that are below their reorder point"""
        query = '''
            SELECT * FROM products
            WHERE quantity <= reorder_point
            ORDER BY quantity ASC
        '''
        return self.db.execute_query(query) 