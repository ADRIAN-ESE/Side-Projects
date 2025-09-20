import sqlite3
import os
from typing import Any, Dict, List


class SalesDB:
    """SQLite wrapper for sales records."""

    def __init__(self, path: str = None):
        self.path = path or os.path.join(os.path.dirname(__file__), "sales.db")
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._ensure_table()

    def _ensure_table(self):
        cur = self._conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT,
                item TEXT,
                quantity INTEGER,
                price_per_item REAL,
                total_price REAL,
                payment_method TEXT,
                timestamp TEXT
            )"""
        )
        self._conn.commit()

    def add_order(self, items: List[Dict[str, Any]], payment_method: str = "cash") -> str:
        import secrets
        from datetime import datetime

        order_id = secrets.token_hex(6)
        ts = datetime.utcnow().isoformat()
        cur = self._conn.cursor()
        for it in items:
            cur.execute(
                "INSERT INTO sales (order_id,item,quantity,price_per_item,total_price,payment_method,timestamp) VALUES (?,?,?,?,?,?,?)",
                (
                    order_id,
                    it["item"],
                    it["quantity"],
                    it["price_per_item"],
                    it["total_price"],
                    payment_method,
                    ts,
                ),
            )
        self._conn.commit()
        return order_id

    def all_sales(self) -> List[Dict[str, Any]]:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM sales ORDER BY id DESC")
        rows = cur.fetchall()
        return [dict(r) for r in rows]

    def export_csv(self, path: str) -> str:
        import csv

        rows = self.all_sales()
        if not rows:
            with open(path, "w", newline="", encoding="utf-8") as f:
                f.write("")  # empty file
            return path
        keys = rows[0].keys()
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)
        return path

    def sales_between(self, start_iso: str, end_iso: str) -> List[Dict[str, Any]]:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM sales WHERE timestamp BETWEEN ? AND ?", (start_iso, end_iso))
        return [dict(r) for r in cur.fetchall()]
