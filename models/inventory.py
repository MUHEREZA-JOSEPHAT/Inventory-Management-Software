from database import Database
from datetime import datetime

class Inventory:
    def __init__(self):
        self.db = Database()

    def update_stock(self, product_id, quantity_change):
        """
        Update stock quantity for a product.

        NOTE: We now treat the `products.quantity` column as the single
        source of truth for stock levels across the app, so this method
        updates that column directly instead of using the separate
        `inventory` table.
        """
        # First get current quantity from products
        result = self.db.execute_query(
            "SELECT quantity FROM products WHERE product_id = ?",
            (product_id,),
        )
        if not result:
            return False

        current_quantity = int(result[0][0])
        new_quantity = current_quantity + quantity_change

        if new_quantity < 0:
            return False  # Cannot have negative inventory

        # Update product quantity
        query = """
            UPDATE products
            SET quantity = ?
            WHERE product_id = ?
        """
        return self.db.execute_query(query, (new_quantity, product_id)) > 0

    def get_stock_level(self, product_id):
        """Get current stock level for a product (from products table)."""
        query = '''
            SELECT p.quantity, p.reorder_point, p.name, p.unit
            FROM products p
            WHERE p.product_id = ?
        '''
        result = self.db.execute_query(query, (product_id,))
        return result[0] if result else None

    def get_all_stock_levels(self):
        """Get stock levels for all products with category names."""
        query = '''
            SELECT p.product_id, p.name, p.quantity, p.reorder_point,
                   CASE WHEN p.quantity <= p.reorder_point THEN 'Low Stock'
                        ELSE 'In Stock' END as status,
                   p.unit,
                   c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            ORDER BY p.name
        '''
        return self.db.execute_query(query)

    def get_stock_movements(self, product_id, start_date=None, end_date=None):
        """Get stock movement history for a product"""
        query = '''
            SELECT s.sale_date, -s.quantity as quantity_change, 'Sale' as type
            FROM sales s
            WHERE s.product_id = ?
            UNION ALL
            SELECT i.last_updated, i.quantity_change, 'Adjustment' as type
            FROM inventory_history i
            WHERE i.product_id = ?
            ORDER BY 1 DESC
        '''
        params = [product_id, product_id]
        
        if start_date:
            query = query.replace('WHERE', 'WHERE date(?) <= ')
            params.insert(0, start_date)
        if end_date:
            query = query.replace('ORDER BY', 'AND date(?) >= ORDER BY')
            params.insert(0, end_date)

        return self.db.execute_query(query, tuple(params))

    def record_stock_adjustment(self, product_id, quantity_change, reason):
        """Record a manual stock adjustment"""
        if self.update_stock(product_id, quantity_change):
            query = '''
                INSERT INTO inventory_history 
                (product_id, quantity_change, reason, adjustment_date)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            '''
            return self.db.execute_query(query, (product_id, quantity_change, reason)) > 0
        return False 