from database import Database
from datetime import datetime

class Product:
    def __init__(self):
        self.db = Database()

    def add_product(self, name, quantity, price, reorder_point, unit='piece', category_id=None, status='Active'):
        """Add a new product to the database"""
        query = '''
            INSERT INTO products (name, price, reorder_point, unit, quantity, category_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        params = (name, price, reorder_point, unit, quantity, category_id, status)
        self.db.execute_query(query, params)
        product_id = self.db.get_last_row_id()
        self._initialize_inventory(product_id)
        return product_id

    def _initialize_inventory(self, product_id):
        """Initialize inventory record for a new product"""
        query = '''
            INSERT INTO inventory (product_id, quantity)
            VALUES (?, 0)
        '''
        self.db.execute_query(query, (product_id,))

    def get_product(self, product_id):
        """Get product details by ID with category name"""
        query = '''
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            WHERE p.product_id = ?
        '''
        result = self.db.execute_query(query, (product_id,))
        return result[0] if result else None

    def get_all_products(self, include_ordered=False):
        """Get all products with category names, optionally including ordered items"""
        query = '''
            SELECT 
                p.product_id, 
                p.name, 
                p.quantity, 
                p.price, 
                p.reorder_point, 
                p.unit, 
                p.created_at, 
                c.name as category_name,
                p.status
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
        '''
        if not include_ordered:
            query += " WHERE p.status = 'Active'"
            
        query += " ORDER BY p.name"
        return self.db.execute_query(query)

    def update_product(self, product_id, name=None, price=None, reorder_point=None, unit=None, quantity=None, category_id=None, status=None):
        """Update product details"""
        current = self.get_product(product_id)
        if not current:
            return False

        updates = []
        params = []
        
        fields = {
            'name': name, 'price': price, 'reorder_point': reorder_point, 
            'unit': unit, 'quantity': quantity, 'category_id': category_id,
            'status': status
        }
        
        for field, value in fields.items():
            if value is not None:
                updates.append(f"{field} = ?")
                params.append(value)
        
        if not updates:
            return False
            
        params.append(product_id)
        query = f"UPDATE products SET {', '.join(updates)} WHERE product_id = ?"
        return self.db.execute_query(query, params)

    def delete_product(self, product_id):
        """Delete a product and its associated records"""
        try:
            # Delete associated inventory
            self.db.execute_query("DELETE FROM inventory WHERE product_id = ?", (product_id,))
            # Delete associated sales
            self.db.execute_query("DELETE FROM sales WHERE product_id = ?", (product_id,))
            # Delete associated orders
            self.db.execute_query("DELETE FROM orders WHERE product_id = ?", (product_id,))
            # Delete product
            self.db.execute_query("DELETE FROM products WHERE product_id = ?", (product_id,))
            return True
        except Exception:
            return False

    def get_low_stock_products(self):
        """Get products below reorder point"""
        query = '''
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            WHERE p.quantity <= p.reorder_point AND p.status = 'Active'
        '''
        return self.db.execute_query(query)

    def get_product_count(self):
        """Get total number of active products"""
        query = "SELECT COUNT(*) FROM products WHERE status = 'Active'"
        result = self.db.execute_query(query)
        return result[0][0] if result else 0