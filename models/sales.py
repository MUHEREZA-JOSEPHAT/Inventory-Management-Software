from database import Database
from datetime import datetime
from .inventory import Inventory

class Sales:
    def __init__(self):
        self.db = Database()
        self.inventory = Inventory()

    def record_sale(self, product_id, quantity, sale_price=None):
        """Record a new sale transaction"""
        # Get product price if not provided
        if sale_price is None:
            query = "SELECT price FROM products WHERE product_id = ?"
            result = self.db.execute_query(query, (product_id,))
            if not result:
                return False
            sale_price = result[0][0]

        # Check if we have enough stock
        stock_level = self.inventory.get_stock_level(product_id)
        if not stock_level or stock_level[0] < quantity:
            return False

        # Record the sale
        query = '''
            INSERT INTO sales (product_id, quantity, sale_price, sale_date)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        '''
        if self.db.execute_query(query, (product_id, quantity, sale_price)):
            # Update inventory
            return self.inventory.update_stock(product_id, -quantity)
        return False

    def get_sales_by_date_range(self, start_date, end_date):
        """Get sales records within a date range"""
        query = '''
            SELECT s.sale_id, p.name, s.quantity, s.sale_price,
                   s.quantity * s.sale_price as total_amount,
                   s.sale_date
            FROM sales s
            JOIN products p ON s.product_id = p.product_id
            WHERE date(s.sale_date) BETWEEN date(?) AND date(?)
            ORDER BY s.sale_date DESC
        '''
        return self.db.execute_query(query, (start_date, end_date))

    def get_sales_summary(self, start_date=None, end_date=None):
        """Get sales summary including total revenue and units sold"""
        query = '''
            SELECT 
                COUNT(DISTINCT sale_id) as total_transactions,
                SUM(quantity) as total_units_sold,
                SUM(quantity * sale_price) as total_revenue,
                AVG(sale_price) as average_sale_price
            FROM sales
        '''
        params = []
        
        if start_date or end_date:
            query += " WHERE "
            conditions = []
            if start_date:
                conditions.append("date(sale_date) >= date(?)")
                params.append(start_date)
            if end_date:
                conditions.append("date(sale_date) <= date(?)")
                params.append(end_date)
            query += " AND ".join(conditions)

        result = self.db.execute_query(query, tuple(params))
        return result[0] if result else None

    def get_top_selling_products(self, limit=10, start_date=None, end_date=None):
        """Get top selling products by quantity"""
        query = '''
            SELECT 
                p.product_id,
                p.name,
                SUM(s.quantity) as total_quantity_sold,
                SUM(s.quantity * s.sale_price) as total_revenue
            FROM sales s
            JOIN products p ON s.product_id = p.product_id
        '''
        params = []
        
        if start_date or end_date:
            query += " WHERE "
            conditions = []
            if start_date:
                conditions.append("date(s.sale_date) >= date(?)")
                params.append(start_date)
            if end_date:
                conditions.append("date(s.sale_date) <= date(?)")
                params.append(end_date)
            query += " AND ".join(conditions)

        query += '''
            GROUP BY p.product_id, p.name
            ORDER BY total_quantity_sold DESC
            LIMIT ?
        '''
        params.append(limit)

        return self.db.execute_query(query, tuple(params)) 