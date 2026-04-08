from database import Database

class CustomerOrder:
    def __init__(self):
        self.db = Database()

    def get_all_orders(self):
        """Fetch all customer online orders with joined product details"""
        query = """
            SELECT co.order_id, co.customer_name, p.name as product_name, 
                   co.quantity, co.total_price, co.status, co.order_date
            FROM customer_orders co
            JOIN products p ON co.product_id = p.product_id
            ORDER BY co.order_date DESC
        """
        return self.db.execute_query(query)

    def get_new_orders_count(self):
        """Get total count of unread notifications (New orders or unread messages)"""
        # Count orders with is_read = 0
        order_query = "SELECT COUNT(*) FROM customer_orders WHERE is_read = 0"
        order_count = self.db.execute_query(order_query)[0][0]
        
        # Count customer messages with is_read = 0
        msg_query = "SELECT COUNT(*) FROM order_chats WHERE sender = 'Customer' AND is_read = 0"
        msg_count = self.db.execute_query(msg_query)[0][0]
        
        return order_count + msg_count

    def mark_as_read(self, order_id):
        """Mark the order and all its messages as read"""
        self.db.execute_query("UPDATE customer_orders SET is_read = 1 WHERE order_id = ?", (order_id,))
        self.db.execute_query("UPDATE order_chats SET is_read = 1 WHERE order_id = ?", (order_id,))

    def update_order_status(self, order_id, status):
        """Update the status of an online order"""
        query = "UPDATE customer_orders SET status = ? WHERE order_id = ?"
        # When status changes from 'New', it should also mark it as read
        self.mark_as_read(order_id)
        return self.db.execute_query(query, (status, order_id))

    def get_order_messages(self, order_id):
        """Fetch all chat messages related to a specific order"""
        query = """
            SELECT sender, message, timestamp 
            FROM order_chats 
            WHERE order_id = ? 
            ORDER BY timestamp ASC
        """
        return self.db.execute_query(query, (order_id,))

    def send_order_message(self, order_id, sender, message):
        """Send a message to the order's dedicated chat"""
        query = "INSERT INTO order_chats (order_id, sender, message) VALUES (?, ?, ?)"
        self.db.execute_query(query, (order_id, sender, message))
        
    def add_simulated_customer_message(self, order_id, message):
        """Helper to simulate the customer talking back"""
        query = "INSERT INTO order_chats (order_id, sender, message, is_read) VALUES (?, 'Customer', ?, 0)"
        self.db.execute_query(query, (order_id, message))

    def simulate_random_event(self):
        """Simulate a new order OR a new message for a 'Live' demo"""
        import random
        # First, try to get an active order
        active_orders = self.db.execute_query("SELECT order_id FROM customer_orders LIMIT 10")
        
        if active_orders and random.choice([True, False]):
            # Simulate a message for an existing order
            oid = random.choice(active_orders)[0]
            messages = [
                "Is my order coming soon?", 
                "I forgot to add one more item!", 
                "Do you have delivery available today?",
                "The Basmati Rice looks great!",
                "Can I pay on delivery?"
            ]
            self.add_simulated_customer_message(oid, random.choice(messages))
            return "message"
        else:
            # Simulate a completely new order
            self.db.execute_query("SELECT product_id, name, price FROM products LIMIT 5")
            prods = self.db.execute_query("SELECT product_id, name, price FROM products LIMIT 5")
            if prods:
                p = random.choice(prods)
                cust_names = ["Joseph", "Sarah", "George", "Emma", "David", "Grace"]
                cust = random.choice(cust_names)
                qty = random.randint(1, 5)
                amt = p[2] * qty
                self.db.execute_query(
                    "INSERT INTO customer_orders (customer_name, product_id, quantity, total_price, status, is_read) VALUES (?, ?, ?, ?, 'New', 0)",
                    (cust, p[0], qty, amt)
                )
                return "order"
        return None
