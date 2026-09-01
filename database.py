"""
IntelliSQL - Database Manager
Handles SQLite database creation, sample data, and query execution.
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random


DB_PATH = "/tmp/intellisql.db"


class DatabaseManager:
    """
    Manages the SQLite database:
    - Creates tables and seeds sample data
    - Provides schema info to Gemini
    - Executes SQL queries safely
    """

    def __init__(self):
        self.db_path = DB_PATH

    def get_connection(self):
        """Returns a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Lets us access columns by name
        return conn

    # ─────────────────────────────────────────────
    # INITIALIZE DATABASE
    # ─────────────────────────────────────────────

    def initialize(self):
        """Create tables and insert sample data if DB doesn't exist."""
        if os.path.exists(self.db_path):
            print("✅ Database already exists. Skipping initialization.")
            return

        print("🔧 Creating database and seeding sample data...")
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create tables
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT NOT NULL,
                email         TEXT UNIQUE NOT NULL,
                country       TEXT NOT NULL,
                city          TEXT,
                age           INTEGER,
                created_at    TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS products (
                product_id    INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT NOT NULL,
                category      TEXT NOT NULL,
                price         REAL NOT NULL,
                stock         INTEGER DEFAULT 0,
                supplier      TEXT
            );

            CREATE TABLE IF NOT EXISTS orders (
                order_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id   INTEGER NOT NULL,
                order_date    TEXT NOT NULL,
                status        TEXT DEFAULT 'pending',
                total_amount  REAL NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            );

            CREATE TABLE IF NOT EXISTS order_items (
                item_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id      INTEGER NOT NULL,
                product_id    INTEGER NOT NULL,
                quantity      INTEGER NOT NULL,
                unit_price    REAL NOT NULL,
                FOREIGN KEY (order_id)   REFERENCES orders(order_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            );

            CREATE TABLE IF NOT EXISTS employees (
                employee_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT NOT NULL,
                department    TEXT NOT NULL,
                salary        REAL NOT NULL,
                hire_date     TEXT NOT NULL,
                manager_id    INTEGER,
                FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
            );
        """)

        # ── Seed Customers ──
        customers = [
            ("Alice Chen",      "alice@example.com",   "India",   "Mumbai",    28),
            ("Bob Smith",       "bob@example.com",     "USA",     "New York",  35),
            ("Carol White",     "carol@example.com",   "UK",      "London",    42),
            ("David Kumar",     "david@example.com",   "India",   "Delhi",     31),
            ("Emma Wilson",     "emma@example.com",    "Canada",  "Toronto",   29),
            ("Frank Zhang",     "frank@example.com",   "China",   "Shanghai",  38),
            ("Grace Lee",       "grace@example.com",   "Korea",   "Seoul",     26),
            ("Henry Brown",     "henry@example.com",   "USA",     "Chicago",   45),
            ("Isla Martinez",   "isla@example.com",    "Spain",   "Madrid",    33),
            ("Jake Thompson",   "jake@example.com",    "India",   "Bangalore", 27),
            ("Karen Patel",     "karen@example.com",   "India",   "Pune",      36),
            ("Liam O'Brien",    "liam@example.com",    "Ireland", "Dublin",    30),
        ]
        cursor.executemany(
            "INSERT INTO customers (name,email,country,city,age) VALUES (?,?,?,?,?)",
            customers
        )

        # ── Seed Products ──
        products = [
            ("Wireless Earbuds",    "Electronics",  1999.00, 150, "Sony"),
            ("Laptop Stand",        "Electronics",   899.00, 200, "Belkin"),
            ("Running Shoes",       "Sports",       3500.00, 80,  "Nike"),
            ("Python Cookbook",     "Books",         699.00, 500, "O'Reilly"),
            ("Office Chair",        "Furniture",    8999.00, 30,  "Herman Miller"),
            ("USB-C Hub",           "Electronics",  1299.00, 300, "Anker"),
            ("Yoga Mat",            "Sports",        799.00, 120, "Liforme"),
            ("Mechanical Keyboard", "Electronics",  4999.00, 60,  "Keychron"),
            ("Water Bottle",        "Lifestyle",     499.00, 400, "Hydro Flask"),
            ("Desk Lamp",           "Furniture",    1199.00, 100, "BenQ"),
            ("Data Science Book",   "Books",         899.00, 250, "O'Reilly"),
            ("Protein Powder",      "Health",       2499.00, 90,  "Optimum"),
        ]
        cursor.executemany(
            "INSERT INTO products (name,category,price,stock,supplier) VALUES (?,?,?,?,?)",
            products
        )

        # ── Seed Orders & Order Items ──
        statuses = ["completed", "completed", "completed", "pending", "shipped", "cancelled"]
        base_date = datetime.now() - timedelta(days=180)

        for i in range(1, 13):  # One order per customer
            days_offset = random.randint(0, 180)
            order_date = (base_date + timedelta(days=days_offset)).strftime("%Y-%m-%d")
            status = random.choice(statuses)

            # Pick 1-3 random products
            num_items = random.randint(1, 3)
            selected_products = random.sample(range(1, 13), num_items)
            total = 0

            for prod_id in selected_products:
                qty = random.randint(1, 4)
                price = products[prod_id - 1][2]  # Get price from our list
                total += qty * price

            cursor.execute(
                "INSERT INTO orders (customer_id,order_date,status,total_amount) VALUES (?,?,?,?)",
                (i, order_date, status, round(total, 2))
            )
            order_id = cursor.lastrowid

            for prod_id in selected_products:
                qty = random.randint(1, 4)
                price = products[prod_id - 1][2]
                cursor.execute(
                    "INSERT INTO order_items (order_id,product_id,quantity,unit_price) VALUES (?,?,?,?)",
                    (order_id, prod_id, qty, price)
                )

        # ── Seed Employees ──
        employees = [
            ("Raj Mehta",      "Engineering",  95000, "2020-01-15", None),
            ("Sara Johnson",   "Marketing",    72000, "2019-06-01", None),
            ("Tom Baker",      "Engineering",  88000, "2021-03-10", 1),
            ("Uma Sharma",     "HR",           65000, "2018-09-20", None),
            ("Vikram Nair",    "Engineering",  92000, "2020-07-05", 1),
            ("Wendy Clark",    "Marketing",    68000, "2022-01-12", 2),
            ("Xander Roy",     "Sales",        75000, "2021-11-30", None),
            ("Yuki Tanaka",    "Engineering",  85000, "2023-02-14", 1),
        ]
        cursor.executemany(
            "INSERT INTO employees (name,department,salary,hire_date,manager_id) VALUES (?,?,?,?,?)",
            employees
        )

        conn.commit()
        conn.close()
        print("✅ Database initialized with sample data!")

    # ─────────────────────────────────────────────
    # EXECUTE QUERY
    # ─────────────────────────────────────────────

    def execute_query(self, sql: str):
        """
        Executes a SQL SELECT query safely.

        Returns:
            - results: list of rows (each row is a list)
            - columns: list of column names
            - row_count: total rows returned
        """
        conn = self.get_connection()
        try:
            cursor = conn.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            results = [list(row) for row in rows]
            return results, columns, len(results)
        finally:
            conn.close()

    # ─────────────────────────────────────────────
    # SCHEMA HELPERS (fed to Gemini as context)
    # ─────────────────────────────────────────────

    def get_schema_text(self) -> str:
        """
        Returns database schema as readable text for Gemini's prompt.
        This is critical — Gemini needs to know exact table/column names.
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        schema_parts = []

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]

        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()

            col_defs = []
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                is_pk = "PRIMARY KEY" if col[5] else ""
                col_defs.append(f"  {col_name} ({col_type}) {is_pk}".strip())

            schema_parts.append(f"Table: {table}\n" + "\n".join(col_defs))

        conn.close()

        # Also add relationship hints
        schema_parts.append("""
Relationships:
- orders.customer_id → customers.customer_id
- order_items.order_id → orders.order_id
- order_items.product_id → products.product_id
- employees.manager_id → employees.employee_id (self-referencing)
""")
        return "\n\n".join(schema_parts)

    def get_schema_dict(self) -> dict:
        """Returns schema as a dict for the frontend sidebar."""
        conn = self.get_connection()
        cursor = conn.cursor()

        schema = {}
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]

        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            cols = cursor.fetchall()
            schema[table] = [
                {"name": c[1], "type": c[2], "pk": bool(c[5])}
                for c in cols
            ]

        conn.close()
        return schema

    def get_schema_summary(self) -> list:
        """Returns a simple list of table names for template rendering."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables
