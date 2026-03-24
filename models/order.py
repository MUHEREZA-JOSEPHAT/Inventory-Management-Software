from database import Database

class Order:
    def __init__(self):
        self.db = Database()

    def place_order(self, supplier_id, product_id, quantity, unit_price):
        """Place a single order item"""
        total_price = quantity * unit_price
        query = """
            INSERT INTO orders (supplier_id, product_id, quantity, unit_price, total_price)
            VALUES (?, ?, ?, ?, ?)
        """
        return self.db.execute_query(query, (supplier_id, product_id, quantity, unit_price, total_price))

    def get_all_orders(self):
        """Get all orders with product and supplier names"""
        query = """
            SELECT o.order_id, s.name, p.name, o.quantity, o.unit_price, o.total_price, o.status, o.order_date
            FROM orders o
            JOIN suppliers s ON o.supplier_id = s.supplier_id
            JOIN products p ON o.product_id = p.product_id
            ORDER BY o.order_date DESC
        """
        return self.db.execute_query(query)

    def update_order_status(self, order_id, status):
        """Update the status of an order (e.g., Pending -> Received)"""
        query = "UPDATE orders SET status = ? WHERE order_id = ?"
        return self.db.execute_query(query, (status, order_id))
