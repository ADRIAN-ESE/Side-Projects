import json
import os
import sqlite3
import hashlib
import secrets
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

# Try to import user's modules (keeps compatibility). If missing, provide sensible fallbacks.
try:
    from datastore import SalesDB  # original expected DB wrapper
except Exception:
    # simple lightweight SalesDB fallback using sqlite3
    class SalesDB:
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
            order_id = secrets.token_hex(6)
            ts = datetime.utcnow().isoformat()
            cur = self._conn.cursor()
            for it in items:
                cur.execute(
                    "INSERT INTO sales (order_id,item,quantity,price_per_item,total_price,payment_method,timestamp) VALUES (?,?,?,?,?,?,?)",
                    (order_id, it["item"], it["quantity"], it["price_per_item"], it["total_price"], payment_method, ts),
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

try:
    from security import hash_password, verify_password, generate_password
except Exception:
    # simple security fallback (bcrypt would be better; this is compatible but basic)
    def _salted_hash(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        if salt is None:
            salt = secrets.token_hex(16)
        h = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
        return salt, h

    def hash_password(password: str) -> str:
        salt, h = _salted_hash(password)
        # store as salt$hash
        return f"{salt}${h}"

    def verify_password(password: str, stored: Optional[str]) -> bool:
        if not stored:
            return False
        try:
            salt, h = stored.split("$", 1)
        except ValueError:
            return False
        return _salted_hash(password, salt)[1] == h

    def generate_password(length: int = 12) -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))


CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")
MENU_FILE = os.path.join(os.path.dirname(__file__), "menu.json")


class FoodSalesApp:
    """Core logic layer: inventory, orders, checkout, persistence, and reports."""

    def __init__(self, menu_file: str = MENU_FILE, config_file: str = CONFIG_FILE):
        self.menu_file = menu_file
        self.config_file = config_file
        self.inventory: Dict[str, Dict[str, Any]] = self._load_json(self.menu_file, default={})
        self.order: Dict[str, int] = {}  # item -> qty
        self.last_removed: Optional[Tuple[str, int]] = None  # for undo (item, qty)
        self.db = SalesDB()
        self._ensure_config()

    # ---------- Data IO ----------
    def _load_json(self, filename: str, default: Any):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default

    def _save_json(self, data: Any, filename: str):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    # ---------- Config & Password ----------
    def _ensure_config(self):
        cfg = self._load_json(self.config_file, default={})
        changed = False
        if "password" not in cfg:
            temp_pass = generate_password(14)
            cfg["password"] = hash_password(temp_pass)
            cfg["first_run_password"] = temp_pass  # show once in GUI
            changed = True
        # preferences
        if "prefs" not in cfg:
            cfg["prefs"] = {"dark_mode": False, "last_window": None}
            changed = True
        if changed:
            self._save_json(cfg, self.config_file)

    def get_prefs(self) -> Dict[str, Any]:
        cfg = self._load_json(self.config_file, default={})
        return cfg.get("prefs", {})

    def set_pref(self, key: str, value: Any):
        cfg = self._load_json(self.config_file, default={})
        prefs = cfg.setdefault("prefs", {})
        prefs[key] = value
        self._save_json(cfg, self.config_file)

    def validate_password(self, password: str) -> bool:
        cfg = self._load_json(self.config_file, default={})
        return verify_password(password, cfg.get("password"))

    def consume_first_run_password(self) -> Optional[str]:
        cfg = self._load_json(self.config_file, default={})
        temp = cfg.pop("first_run_password", None)
        self._save_json(cfg, self.config_file)
        return temp

    def change_password(self, new_password: str):
        cfg = self._load_json(self.config_file, default={})
        cfg["password"] = hash_password(new_password)
        cfg.pop("first_run_password", None)
        self._save_json(cfg, self.config_file)

    # ---------- Inventory ----------
    def add_update_item(self, item: str, quantity: int, price: float, description: str = "", category: str = "Uncategorized") -> str:
        item = item.strip().lower()
        if quantity < 0:
            return "Quantity cannot be negative."
        if price < 0:
            return "Price cannot be negative."
        entry = self.inventory.get(item)
        if entry:
            entry["quantity"] = int(entry.get("quantity", 0)) + int(quantity)
            if price > 0:
                entry["price"] = float(price)
            if description:
                entry["description"] = description
            if category:
                entry["category"] = category
            feedback = f"Updated {item.capitalize()} to qty={entry['quantity']}."
        else:
            self.inventory[item] = {
                "quantity": int(quantity),
                "price": float(price),
                "description": description or "No description.",
                "category": category or "Uncategorized",
            }
            feedback = f"Added {quantity} {item.capitalize()}."
        self._save_json(self.inventory, self.menu_file)
        return feedback

    def update_item_price(self, item: str, price: float) -> str:
        item = item.lower()
        if item in self.inventory and price >= 0:
            self.inventory[item]["price"] = float(price)
            self._save_json(self.inventory, self.menu_file)
            return f"{item.capitalize()} price updated to ${price:.2f}"
        return f"{item.capitalize()} not found or invalid price."

    def low_stock_items(self, threshold: int = 5) -> List[Tuple[str, int]]:
        results = []
        for k, v in self.inventory.items():
            if int(v.get("quantity", 0)) <= threshold:
                results.append((k, int(v.get("quantity", 0))))
        return results

    # ---------- Order ----------
    def clear_order(self):
        self.order.clear()
        self.last_removed = None

    def add_to_order(self, item: str, quantity: int) -> str:
        item = item.lower()
        if item not in self.inventory:
            return f"{item.capitalize()} not found in menu."
        if quantity <= 0:
            return "Quantity must be positive."
        new_qty = self.order.get(item, 0) + int(quantity)
        if new_qty > self.inventory[item]["quantity"]:
            return f"Insufficient stock for {item.capitalize()}. Only {self.inventory[item]['quantity']} available."
        self.order[item] = new_qty
        return f"Added/Updated {item.capitalize()} to quantity {new_qty}."

    def update_order_quantity(self, item: str, change: int) -> str:
        item = item.lower()
        if item not in self.order:
            return "Item not found in order."
        new_qty = self.order[item] + int(change)
        if new_qty <= 0:
            removed_qty = self.order.pop(item, None)
            self.last_removed = (item, removed_qty or 0)
            return f"{item.capitalize()} removed from order."
        if new_qty > self.inventory[item]["quantity"]:
            return f"Insufficient stock. Only {self.inventory[item]['quantity']} available."
        self.order[item] = new_qty
        return "Quantity updated."

    def remove_from_order(self, item: str) -> str:
        item = item.lower()
        removed = self.order.pop(item, None)
        if removed is not None:
            self.last_removed = (item, removed)
            return f"{item.capitalize()} removed."
        return f"{item.capitalize()} was not in the order."

    def undo_last_removal(self) -> str:
        if not self.last_removed:
            return "Nothing to undo."
        item, qty = self.last_removed
        if self.inventory.get(item, {}).get("quantity", 0) < qty:
            return f"Cannot undo — only {self.inventory.get(item, {}).get('quantity',0)} in stock."
        self.order[item] = self.order.get(item, 0) + qty
        self.last_removed = None
        return f"Restored {qty} x {item.capitalize()} to order."

    # ---------- Checkout ----------
    def checkout(self, payment_method: str) -> Tuple[bool, str]:
        if not self.order:
            return False, "Your order is empty!"

        # Verify stock
        for item, qty in self.order.items():
            if self.inventory.get(item, {}).get("quantity", 0) < qty:
                return False, f"Checkout failed: Insufficient stock for {item.capitalize()}."

        # Build items list and deduct
        items = []
        total = 0.0
        for item, qty in list(self.order.items()):
            price = float(self.inventory[item]["price"])
            subtotal = round(price * qty, 2)
            total += subtotal
            items.append({
                "item": item,
                "quantity": qty,
                "price_per_item": price,
                "total_price": subtotal
            })
            # deduct inventory
            self.inventory[item]["quantity"] -= qty

        # Save inventory first (so crash after DB won't lose stock state)
        try:
            self._save_json(self.inventory, self.menu_file)
        except Exception as e:
            return False, f"Internal error saving inventory: {e}"

        # Persist sale
        try:
            order_id = self.db.add_order(items, payment_method=payment_method)
        except Exception as e:
            # rollback inventory change (best-effort)
            for it in items:
                self.inventory[it["item"]]["quantity"] += it["quantity"]
            self._save_json(self.inventory, self.menu_file)
            return False, f"Internal error saving order: {e}"

        # Build receipt text
        receipt_lines = ["--- Receipt ---"]
        for it in items:
            receipt_lines.append(f"{it['quantity']} x {it['item'].capitalize()} @ ${it['price_per_item']:.2f} = ${it['total_price']:.2f}")
        receipt_lines.append(f"Total: ${round(total,2):.2f}")
        receipt_lines.append(f"Payment: {payment_method.capitalize()}")
        receipt_lines.append(f"Order ID: {order_id}")
        receipt_text = "\n".join(receipt_lines)

        self.clear_order()
        return True, receipt_text

    def save_receipt_pdf(self, receipt_text: str, out_path: str) -> str:
        """
        Attempts to save a PDF receipt using reportlab. If library missing, falls back to .txt.
        Returns path written.
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            c = canvas.Canvas(out_path, pagesize=letter)
            width, height = letter
            y = height - 40
            for line in receipt_text.splitlines():
                c.drawString(40, y, line)
                y -= 14
                if y < 40:
                    c.showPage()
                    y = height - 40
            c.save()
            return out_path
        except Exception:
            # fallback to text file
            if not out_path.lower().endswith(".txt"):
                out_path = os.path.splitext(out_path)[0] + ".txt"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(receipt_text)
            return out_path

    # ---------- Reporting ----------
    def sales_summary(self, period: str = "daily") -> Dict[str, Any]:
        """
        Returns totals for 'daily' (today), 'weekly' (last 7 days), or 'monthly' (30 days).
        """
        now = datetime.utcnow()
        if period == "daily":
            start = datetime(now.year, now.month, now.day)
        elif period == "weekly":
            start = now - timedelta(days=7)
        elif period == "monthly":
            start = now - timedelta(days=30)
        else:
            start = datetime(1970, 1, 1)

        start_iso = start.isoformat()
        end_iso = now.isoformat()
        try:
            rows = self.db.sales_between(start_iso, end_iso) if hasattr(self.db, "sales_between") else self.db.all_sales()
        except Exception:
            rows = self.db.all_sales()

        total_income = 0.0
        total_items = 0
        orders = set()
        for r in rows:
            try:
                total_income += float(r.get("total_price", 0) or 0)
                total_items += int(r.get("quantity", 0) or 0)
                orders.add(r.get("order_id"))
            except Exception:
                continue
        return {
            "period": period,
            "start": start_iso,
            "end": end_iso,
            "total_income": round(total_income, 2),
            "total_items": total_items,
            "orders_count": len(orders),
        }
