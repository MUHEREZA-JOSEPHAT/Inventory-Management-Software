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
            self.conn = sqlite3.connect(self.db_name)
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
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    
                    # Copy data from old table to new table
                    self.cursor.execute('''
                        INSERT INTO products_new (
                            product_id, name, quantity, price, reorder_point, unit, created_at
                        )
                        SELECT 
                            product_id,
                            name,
                            COALESCE(quantity, 0),
                            price,
                            reorder_point,
                            COALESCE(unit, 'piece'),
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

            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

    def __del__(self):
        """Destructor to ensure connection is closed"""
        self.disconnect() 