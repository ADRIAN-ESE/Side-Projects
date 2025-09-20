import sqlite3
from datetime import datetime
import csv

class SalesDB:
    def __init__(self, db_path="sales.db"):
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        cur = self._conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS inventory (
            item TEXT PRIMARY KEY,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            username TEXT,
            item TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            payment_method TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        self._conn.commit()

    def add_user(self, username, password_hash, role):
        try:
            self._conn.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", (username, password_hash, role))
            self._conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user(self, username):
        cur = self._conn.execute("SELECT * FROM users WHERE username=?", (username,))
        return cur.fetchone()

    def all_users(self):
        cur = self._conn.execute("SELECT username, role, created_at FROM users")
        return cur.fetchall()

    def add_update_item(self, item, qty, price):
        self._conn.execute("INSERT INTO inventory (item, quantity, price) VALUES (?, ?, ?) "
                           "ON CONFLICT(item) DO UPDATE SET quantity=?, price=?",
                           (item, qty, price, qty, price))
        self._conn.commit()

    def get_inventory(self):
        cur = self._conn.execute("SELECT * FROM inventory")
        return {row["item"]: {"quantity": row["quantity"], "price": row["price"]} for row in cur.fetchall()}

    def record_sale(self, order_id, username, item, qty, total_price, payment):
        self._conn.execute("INSERT INTO sales (order_id, username, item, quantity, total_price, payment_method) VALUES (?, ?, ?, ?, ?, ?)",
                           (order_id, username, item, qty, total_price, payment))
        self._conn.commit()

    def all_sales(self):
        cur = self._conn.execute("SELECT * FROM sales ORDER BY timestamp DESC")
        return cur.fetchall()

    def sales_between(self, start, end):
        cur = self._conn.execute("SELECT * FROM sales WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp ASC", (start, end))
        return cur.fetchall()

    def export_csv(self, path):
        rows = self.all_sales()
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(rows[0].keys() if rows else [])
            for r in rows:
                writer.writerow(r)

    def log_action(self, username, action, details=""):
        self._conn.execute("INSERT INTO audit (username, action, details) VALUES (?, ?, ?)", (username, action, details))
        self._conn.commit()

    def audit_log(self, limit=100):
        cur = self._conn.execute("SELECT * FROM audit ORDER BY timestamp DESC LIMIT ?", (limit,))
        return cur.fetchall()
