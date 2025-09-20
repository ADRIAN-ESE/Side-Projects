
import json, os
from datetime import datetime
from typing import Dict, Any
from datastore import SalesDB
from security import hash_password, verify_password, generate_password

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")
MENU_FILE = os.path.join(os.path.dirname(__file__), "menu.json")

class FoodSalesApp:
    def __init__(self, menu_file: str = MENU_FILE, config_file: str = CONFIG_FILE):
        self.menu_file = menu_file
        self.config_file = config_file
        self.inventory: Dict[str, Dict[str, Any]] = self._load_json(self.menu_file, default={})
        self.order: Dict[str, int] = {}  # item -> qty
        self.db = SalesDB()
        self._ensure_config()

    # ---------- Data IO ----------
    def _load_json(self, filename: str, default: Any):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return default
        except json.JSONDecodeError:
            return default

    def _save_json(self, data: Any, filename: str):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    # ---------- Config & Password ----------
    def _ensure_config(self):
        cfg = self._load_json(self.config_file, default={})
        if "password" not in cfg:
            temp_pass = generate_password(14)
            cfg["password"] = hash_password(temp_pass)
            cfg["first_run_password"] = temp_pass  # show once in GUI
            self._save_json(cfg, self.config_file)

    def validate_password(self, password: str) -> bool:
        cfg = self._load_json(self.config_file, default={})
        return verify_password(password, cfg.get("password"))

    def consume_first_run_password(self) -> str:
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
        item = item.lower()
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
        if item in self.inventory and price > 0:
            self.inventory[item]["price"] = float(price)
            self._save_json(self.inventory, self.menu_file)
            return f"{item.capitalize()} price updated to ${price:.2f}"
        return f"{item.capitalize()} not found or invalid price."

    # ---------- Order ----------
    def clear_order(self):
        self.order.clear()

    def add_to_order(self, item: str, quantity: int) -> str:
        item = item.lower()
        if item not in self.inventory:
            return f"{item.capitalize()} not found in menu."
        new_qty = self.order.get(item, 0) + int(quantity)
        if new_qty <= 0:
            self.order.pop(item, None)
            return f"{item.capitalize()} removed from order."
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
            self.order.pop(item, None)
            return f"{item.capitalize()} removed from order."
        if new_qty > self.inventory[item]["quantity"]:
            return f"Insufficient stock. Only {self.inventory[item]['quantity']} available."
        self.order[item] = new_qty
        return "Quantity updated."

    def remove_from_order(self, item: str) -> str:
        self.order.pop(item.lower(), None)
        return f"{item.capitalize()} removed."

    # ---------- Checkout ----------
    def checkout(self, payment_method: str) -> tuple[bool, str]:
        if not self.order:
            return False, "Your order is empty!"

        for item, qty in self.order.items():
            if self.inventory.get(item, {}).get("quantity", 0) < qty:
                return False, f"Checkout failed: Insufficient stock for {item.capitalize()}."

        items = []
        total = 0.0
        for item, qty in self.order.items():
            price = float(self.inventory[item]["price"])
            subtotal = price * qty
            total += subtotal
            items.append({
                "item": item,
                "quantity": qty,
                "price_per_item": price,
                "total_price": subtotal
            })
            self.inventory[item]["quantity"] -= qty
        self._save_json(self.inventory, self.menu_file)

        order_id = self.db.add_order(items, payment_method=payment_method)

        receipt = ["--- Receipt ---"]
        for it in items:
            receipt.append(f"{it['quantity']} x {it['item'].capitalize()} @ ${it['price_per_item']:.2f} = ${it['total_price']:.2f}")
        receipt.append(f"Total: ${total:.2f}")
        receipt.append(f"Payment: {payment_method.capitalize()}")
        receipt.append(f"Order ID: {order_id}")
        self.clear_order()
        return True, "\n".join(receipt)
