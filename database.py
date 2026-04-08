import sqlite3
from datetime import datetime
import os

class Database:
    def __init__(self, db_name="inventory.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.initialize_database()

    def connect(self):
        """Establish connection to the database"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
            self.cursor = self.conn.cursor()

    def disconnect(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def execute_query(self, query, params=()):
        """Execute a query and return results"""
        try:
            self.connect()  # Ensure connection is open
            self.cursor.execute(query, params)
            if query.strip().upper().startswith(('SELECT', 'PRAGMA')):
                return self.cursor.fetchall()
            else:
                self.conn.commit()
                return self.cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            raise e

    def get_last_row_id(self):
        """Get the ID of the last inserted row"""
        return self.cursor.lastrowid

    def initialize_database(self):
        """Create database tables if they don't exist"""
        try:
            # Create products table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    price REAL NOT NULL,
                    reorder_point INTEGER NOT NULL,
                    unit TEXT NOT NULL DEFAULT 'piece',
                    category_id INTEGER,
                    status TEXT DEFAULT 'Active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories (category_id)
                )
            ''')

            # Create categories table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Check if we need to migrate the table structure
            try:
                # Get current table info
                self.cursor.execute("PRAGMA table_info(products)")
                columns = {row[1]: row[0] for row in self.cursor.fetchall()}
                
                # Check if we need to recreate the table
                needs_migration = False
                
                # Check if all required columns exist
                required_columns = {
                    'product_id': 'INTEGER',
                    'name': 'TEXT',
                    'quantity': 'INTEGER',
                    'price': 'REAL',
                    'reorder_point': 'INTEGER',
                    'unit': 'TEXT',
                    'category_id': 'INTEGER',
                    'status': 'TEXT',
                    'created_at': 'TIMESTAMP'
                }
                
                for col, type_ in required_columns.items():
                    if col not in columns:
                        needs_migration = True
                        break
                
                if needs_migration:
                    # Create new table with correct structure
                    self.cursor.execute('''
                        CREATE TABLE products_new (
                            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            quantity INTEGER NOT NULL DEFAULT 0,
                            price REAL NOT NULL,
                            reorder_point INTEGER NOT NULL,
                            unit TEXT NOT NULL DEFAULT 'piece',
                            category_id INTEGER,
                            status TEXT DEFAULT 'Active',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (category_id) REFERENCES categories (category_id)
                        )
                    ''')
                    
                    # Copy data from old table to new table
                    self.cursor.execute('''
                        INSERT INTO products_new (
                            product_id, name, quantity, price, reorder_point, unit, category_id, status, created_at
                        )
                        SELECT 
                            product_id,
                            name,
                            COALESCE(quantity, 0),
                            price,
                            reorder_point,
                            COALESCE(unit, 'piece'),
                            NULL, -- Default category_id to NULL
                            'Active', -- Default status to Active
                            COALESCE(created_at, CURRENT_TIMESTAMP)
                        FROM products
                    ''')
                    
                    # Drop old table and rename new table
                    self.cursor.execute('DROP TABLE products')
                    self.cursor.execute('ALTER TABLE products_new RENAME TO products')
                    self.conn.commit()
                    
            except sqlite3.OperationalError:
                # Table doesn't exist yet, which is fine
                pass

            # Create inventory table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (product_id)
                )
            ''')

            # Create sales table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    sale_price REAL NOT NULL,
                    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (product_id)
                )
            ''')

            # Create users table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    role TEXT DEFAULT 'worker',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create suppliers table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS suppliers (
                    supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    contact_person TEXT,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create orders table (for ordering supplies)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    supplier_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    total_price REAL NOT NULL,
                    status TEXT DEFAULT 'Pending',
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers (supplier_id),
                    FOREIGN KEY (product_id) REFERENCES products (product_id)
                )
            ''')
            
            # Create chat_messages table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_messages (
                    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create customer_orders table (online purchases)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS customer_orders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name TEXT NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    total_price REAL NOT NULL,
                    status TEXT DEFAULT 'New',
                    is_read INTEGER DEFAULT 0,
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (product_id)
                )
            ''')

            # Create order_chats table (chat linked to a customer order)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS order_chats (
                    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    sender TEXT NOT NULL,
                    message TEXT NOT NULL,
                    is_read INTEGER DEFAULT 0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (order_id) REFERENCES customer_orders (order_id)
                )
            ''')
            
            # Migration: Add is_read column if it doesn't exist
            try:
                self.cursor.execute("ALTER TABLE customer_orders ADD COLUMN is_read INTEGER DEFAULT 0")
            except: pass
            
            try:
                self.cursor.execute("ALTER TABLE order_chats ADD COLUMN is_read INTEGER DEFAULT 0")
            except: pass

            # Create admin_settings table (for mail APIs and SMTP)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_settings (
                    setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_email TEXT,
                    mail_mode TEXT DEFAULT 'Simulation',
                    smtp_host TEXT,
                    smtp_port INTEGER,
                    smtp_user TEXT,
                    smtp_pass TEXT,
                    api_endpoint TEXT,
                    api_sid TEXT,
                    api_key TEXT,
                    imap_host TEXT,
                    imap_port INTEGER,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create supplier_communications table (email exchange log)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS supplier_communications (
                    comm_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    supplier_id INTEGER NOT NULL,
                    sender_type TEXT NOT NULL, -- 'Admin' or 'Supplier'
                    sender_email TEXT,
                    recipient_email TEXT,
                    subject TEXT,
                    message TEXT NOT NULL,
                    status TEXT DEFAULT 'Sent',
                    uid TEXT UNIQUE,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers (supplier_id)
                )
            ''')
            
            # Ensure is_read exists in supplier_communications
            try:
                self.cursor.execute("ALTER TABLE supplier_communications ADD COLUMN is_read INTEGER DEFAULT 0")
            except: pass
            
            # Migration: Ensure settings table is initialized
            try:
                self.cursor.execute("ALTER TABLE admin_settings ADD COLUMN api_sid TEXT")
            except: pass
            
            try:
                self.cursor.execute("ALTER TABLE admin_settings ADD COLUMN imap_host TEXT")
                self.cursor.execute("ALTER TABLE admin_settings ADD COLUMN imap_port INTEGER")
            except: pass

            try:
                self.cursor.execute("ALTER TABLE supplier_communications ADD COLUMN uid TEXT")
            except: pass
            
            self.cursor.execute("SELECT COUNT(*) FROM admin_settings")
            if self.cursor.fetchone()[0] == 0:
                self.cursor.execute("INSERT INTO admin_settings (admin_email) VALUES ('admin@supermarket.com')")
            
            # Default admin
            self.cursor.execute("SELECT COUNT(*) FROM users")
            if self.cursor.fetchone()[0] == 0:
                import hashlib
                admin_pass = hashlib.sha256("admin123".encode()).hexdigest()
                self.cursor.execute(
                    "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                    ("admin", admin_pass, "System Administrator", "admin")
                )

            # Insert dummy customer orders if empty
            self.cursor.execute("SELECT COUNT(*) FROM customer_orders")
            if self.cursor.fetchone()[0] == 0:
                # Get a product or insert a dummy one
                self.cursor.execute("SELECT product_id, price FROM products LIMIT 1")
                product = self.cursor.fetchone()
                if product:
                    pid, pprice = product
                    dummy_orders = [
                        ("Alice Johnson", pid, 2, pprice * 2, "New"),
                        ("Bob Smith", pid, 1, pprice * 1, "In Progress"),
                        ("Charlie Davis", pid, 5, pprice * 5, "Completed")
                    ]
                    for order in dummy_orders:
                        self.cursor.execute(
                            "INSERT INTO customer_orders (customer_name, product_id, quantity, total_price, status) VALUES (?, ?, ?, ?, ?)",
                            order
                        )

            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

    def create_user(self, username, password, full_name, role="worker"):
        import hashlib
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            query = "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)"
            return self.execute_query(query, (username, password_hash, full_name, role))
        except sqlite3.IntegrityError:
            raise Exception("Username already exists")

    def authenticate_user(self, username, password):
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        query = "SELECT user_id, username, full_name, role FROM users WHERE username = ? AND password_hash = ?"
        results = self.execute_query(query, (username, password_hash))
        return results[0] if results else None

    def __del__(self):
        """Destructor to ensure connection is closed"""
        self.disconnect() 