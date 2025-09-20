
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime
from typing import Any, Dict
import json, os

from app import FoodSalesApp
from datastore import SalesDB

DARK = {
    "bg_main": "#1f2430",
    "bg_frame": "#2b313e",
    "fg": "#e6e6e6",
    "accent": "#4a90e2",
    "danger": "#d9534f",
    "success": "#5cb85c",
    "warn": "#f0ad4e",
    "tree_header": "#384055"
}
LIGHT = {
    "bg_main": "#F0F8FF",
    "bg_frame": "#ADD8E6",
    "fg": "#000080",
    "accent": "#4682B4",
    "danger": "#F08080",
    "success": "#32CD32",
    "warn": "#FFD27F",
    "tree_header": "#B0C4DE"
}

class FoodSalesGUI:
    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("Food Sales Management System — Pro")
        self.master.geometry("1150x820")
        self.dark_mode = False
        self.theme = LIGHT.copy()

        self.app = FoodSalesApp()
        self.db = self.app.db

        self._style = ttk.Style()
        self._style.configure("Treeview.Heading", font=('Arial', 12, 'bold'))

        self._build_main_menu()
        tmp = self.app.consume_first_run_password()
        if tmp:
            messagebox.showinfo("First Run", f"Temporary manager password:\n\n{tmp}\n\nGo to Manager → Change Password.")

    # Theming
    def _apply_theme(self):
        self.master.configure(bg=self.theme["bg_main"])

    def _toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.theme = DARK.copy() if self.dark_mode else LIGHT.copy()
        self._build_main_menu()

    # Helpers
    def _clear(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        self._apply_theme()

    def _searchbox(self, parent, on_change):
        frame = tk.Frame(parent, bg=self.theme["bg_frame"])
        tk.Label(frame, text="Search:", bg=self.theme["bg_frame"], fg=self.theme["fg"]).pack(side="left", padx=5)
        var = tk.StringVar()
        ent = tk.Entry(frame, textvariable=var, width=30)
        ent.pack(side="left", padx=5)
        def cb(*_):
            on_change(var.get().strip().lower())
        var.trace_add("write", cb)
        return frame

    def _sortable_tree(self, parent, columns, stretch=True):
        tv = ttk.Treeview(parent, columns=columns, show='headings')
        for col in columns:
            tv.heading(col, text=col, command=lambda c=col: self._sort_tree(tv, c, False))
            tv.column(col, stretch=stretch)
        return tv

    def _sort_tree(self, tree, col, reverse):
        data = [(tree.set(k, col), k) for k in tree.get_children("")]
        # try numeric
        def to_num(s):
            try:
                return float(str(s).replace("$",""))
            except:
                return s
        data.sort(key=lambda t: to_num(t[0]), reverse=reverse)
        for idx, (_, k) in enumerate(data):
            tree.move(k, "", idx)
        tree.heading(col, command=lambda: self._sort_tree(tree, col, not reverse))

    # Main menu
    def _build_main_menu(self):
        self._clear()
        frame = tk.Frame(self.master, bg=self.theme["bg_frame"], bd=6, relief="ridge")
        frame.pack(pady=40, padx=40, fill="both", expand=True)

        tk.Label(frame, text="Food Sales Management System — Pro", font=("Arial", 24, "bold"), bg=self.theme["bg_frame"], fg=self.theme["fg"]).pack(pady=20)

        btns = tk.Frame(frame, bg=self.theme["bg_frame"])
        btns.pack(pady=10)

        def mkbtn(text, cmd, bg=None):
            return tk.Button(btns, text=text, command=cmd, font=("Arial", 14, "bold"), bg=bg or self.theme["accent"], fg="white", width=22, height=2, bd=0, activebackground=self.theme["accent"])

        mkbtn("Manager Menu", self._manager_menu).grid(row=0, column=0, padx=10, pady=10)
        mkbtn("Customer Menu", self._customer_menu).grid(row=0, column=1, padx=10, pady=10)
        mkbtn("Toggle Dark Mode", self._toggle_dark_mode, bg=self.theme["warn"]).grid(row=1, column=0, padx=10, pady=10)
        mkbtn("Exit", self.master.quit, bg=self.theme["danger"]).grid(row=1, column=1, padx=10, pady=10)

    # Manager flow
    def _manager_login(self) -> bool:
        pw = simpledialog.askstring("Manager Login", "Enter Manager Password:", show="*")
        return (pw is not None) and self.app.validate_password(pw)

    def _manager_menu(self):
        if not self._manager_login():
            messagebox.showerror("Denied", "Incorrect password.")
            return
        self._manager_menu_gui()

    def _manager_menu_gui(self):
        self._clear()
        frame = tk.Frame(self.master, bg=self.theme["bg_frame"], bd=6, relief="groove")
        frame.pack(pady=30, padx=30, fill="both", expand=True)
        tk.Label(frame, text="Manager Dashboard", font=("Arial", 20, "bold"), bg=self.theme["bg_frame"], fg=self.theme["fg"]).pack(pady=10)

        btns = tk.Frame(frame, bg=self.theme["bg_frame"])
        btns.pack(pady=10)

        def mk(text, cmd):
            tk.Button(btns, text=text, command=cmd, font=("Arial", 13), bg=self.theme["accent"], fg="white", width=25, height=2, bd=0).pack(pady=6)

        mk("View Inventory", self._view_inventory)
        mk("Add/Update Item", self._add_update_item)
        mk("Adjust Item Price", self._adjust_price)
        mk("Review Sales (DB)", self._view_sales)
        mk("Export Sales to CSV", self._export_sales)
        mk("Change Password", self._change_password)
        mk("Back to Main Menu", self._build_main_menu)

    def _view_inventory(self):
        self._clear()
        frame = tk.Frame(self.master, bg=self.theme["bg_frame"])
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        tk.Label(frame, text="Current Inventory", font=("Arial", 18, "bold"), bg=self.theme["bg_frame"], fg=self.theme["fg"]).pack(pady=10)

        # search box
        def apply_filter(q):
            for i in tv.get_children():
                tv.delete(i)
            for item, d in sorted(self.app.inventory.items()):
                if q and q not in item.lower() and q not in d.get("category","").lower():
                    continue
                qty = int(d.get("quantity",0))
                price = float(d.get("price",0))
                desc = d.get("description","")
                cat = d.get("category","Uncategorized")
                node = tv.insert("", "end", values=(item.capitalize(), qty, f"${price:.2f}", cat, desc))
                if qty < 5:
                    tv.item(node, tags=("low",))
            tv.tag_configure("low", background="#ffcccc")

        sb = self._searchbox(frame, apply_filter)
        sb.pack(pady=5)

        cols = ("Item","Quantity","Price","Category","Description")
        tv = self._sortable_tree(frame, cols)
        tv.pack(fill="both", expand=True)
        apply_filter("")
        tk.Button(frame, text="Back", command=self._manager_menu_gui, bg=self.theme["accent"], fg="white").pack(pady=10)

    def _add_update_item(self):
        win = tk.Toplevel(self.master); win.title("Add/Update Item"); win.configure(bg=self.theme["bg_frame"])
        fields = [("Name",""),("Quantity","0"),("Price","0.0"),("Category","Uncategorized"),("Description","")]
        vars = []
        for i,(label,default) in enumerate(fields):
            tk.Label(win, text=label+":", bg=self.theme["bg_frame"], fg=self.theme["fg"]).grid(row=i, column=0, padx=8, pady=6, sticky="e")
            v = tk.StringVar(value=default); vars.append(v)
            tk.Entry(win, textvariable=v, width=30).grid(row=i, column=1, padx=8, pady=6)
        def submit():
            name = vars[0].get().strip()
            try:
                qty = int(vars[1].get())
                price = float(vars[2].get())
            except:
                messagebox.showerror("Invalid", "Quantity must be int; Price must be number.", parent=win); return
            cat = vars[3].get().strip() or "Uncategorized"
            desc = vars[4].get().strip()
            if not name or qty <= 0 or price <= 0:
                messagebox.showerror("Invalid", "Provide name, positive quantity and price.", parent=win); return
            msg = self.app.add_update_item(name, qty, price, desc, cat)
            messagebox.showinfo("OK", msg, parent=win); win.destroy()
        tk.Button(win, text="Submit", command=submit, bg=self.theme["success"], fg="white").grid(row=len(fields), column=0, columnspan=2, pady=10)

    def _adjust_price(self):
        items = list(self.app.inventory.keys())
        if not items:
            messagebox.showinfo("No Items", "Inventory is empty."); return
        win = tk.Toplevel(self.master); win.title("Adjust Price"); win.configure(bg=self.theme["bg_frame"])
        tk.Label(win, text="Item:", bg=self.theme["bg_frame"], fg=self.theme["fg"]).grid(row=0, column=0, padx=6, pady=6)
        item_var = tk.StringVar(value=items[0])
        ttk.Combobox(win, textvariable=item_var, values=[i.capitalize() for i in items], state="readonly").grid(row=0, column=1, padx=6, pady=6)
        tk.Label(win, text="New Price:", bg=self.theme["bg_frame"], fg=self.theme["fg"]).grid(row=1, column=0, padx=6, pady=6)
        price_var = tk.StringVar()
        tk.Entry(win, textvariable=price_var).grid(row=1, column=1, padx=6, pady=6)
        def submit():
            try:
                price = float(price_var.get())
            except:
                messagebox.showerror("Invalid", "Enter a number for price.", parent=win); return
            res = self.app.update_item_price(item_var.get(), price)
            messagebox.showinfo("Result", res, parent=win); win.destroy()
        tk.Button(win, text="Submit", command=submit, bg=self.theme["success"], fg="white").grid(row=2, column=0, columnspan=2, pady=10)

    def _view_sales(self):
        self._clear()
        frame = tk.Frame(self.master, bg=self.theme["bg_frame"])
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        tk.Label(frame, text="Sales (from SQLite)", font=("Arial", 18, "bold"), bg=self.theme["bg_frame"], fg=self.theme["fg"]).pack(pady=10)

        cols = ("Order ID","Item","Qty","Price/Item","Total","Payment","Timestamp")
        tv = self._sortable_tree(frame, cols)
        tv.pack(fill="both", expand=True)

        for r in self.db.all_sales():
            tv.insert("", "end", values=(
                r["order_id"],
                r["item"].capitalize(),
                r["quantity"],
                f"${r['price_per_item']:.2f}",
                f"${r['total_price']:.2f}",
                r["payment_method"].capitalize(),
                r["timestamp"].split(".")[0].replace("T"," ")
            ))

        tk.Button(frame, text="Back", command=self._manager_menu_gui, bg=self.theme["accent"], fg="white").pack(pady=10)

    def _export_sales(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")], title="Export Sales CSV")
        if not path:
            return
        out = self.db.export_csv(path)
        messagebox.showinfo("Exported", f"Saved to:\n{out}")

    def _change_password(self):
        new = simpledialog.askstring("Change Password", "Enter new manager password:", show="*")
        if not new or len(new) < 8:
            messagebox.showerror("Invalid", "Password must be at least 8 characters."); return
        self.app.change_password(new)
        messagebox.showinfo("Done", "Password changed successfully.")

    # Customer flow
    def _customer_menu(self):
        self._clear()
        self.app.clear_order()
        frame = tk.Frame(self.master, bg=self.theme["bg_frame"], bd=6, relief="ridge")
        frame.pack(pady=30, padx=30, fill="both", expand=True)

        tk.Label(frame, text="Welcome, Customer!", font=("Arial", 20, "bold"), bg=self.theme["bg_frame"], fg=self.theme["fg"]).pack(pady=10)

        tk.Button(frame, text="▶ Start New Order", command=self._ordering, font=("Arial", 16, "bold"), bg=self.theme["success"], fg="white", width=24, height=2, bd=0).pack(pady=12)
        tk.Button(frame, text="Back to Main Menu", command=self._build_main_menu, bg=self.theme["danger"], fg="white").pack(pady=6)

    def _ordering(self):
        self._clear()
        main = tk.Frame(self.master, bg=self.theme["bg_main"])
        main.pack(fill="both", expand=True, padx=8, pady=8)
        main.columnconfigure(0, weight=2)
        main.columnconfigure(1, weight=3)
        main.rowconfigure(0, weight=1)

        # Left: Menu + search + description
        left = tk.Frame(main, bg=self.theme["bg_frame"]); left.grid(row=0,column=0,sticky="nsew",padx=6,pady=6)
        tk.Label(left, text="Our Menu", font=("Arial", 16, "bold"), bg=self.theme["bg_frame"], fg=self.theme["fg"]).pack(pady=6)

        cols = ("Item","Price")
        self.menu_tree = ttk.Treeview(left, columns=cols, show="headings")
        for c in cols: self.menu_tree.heading(c, text=c)
        self.menu_tree.column("Price", width=80, anchor="e")
        self.menu_tree.pack(fill="both", expand=True, padx=6, pady=6)

        def refresh_menu(q=""):
            for i in self.menu_tree.get_children():
                self.menu_tree.delete(i)
            for item, d in sorted(self.app.inventory.items()):
                if d.get("quantity",0) <= 0: 
                    continue
                if q and q not in item.lower() and q not in d.get("category","").lower():
                    continue
                self.menu_tree.insert("", "end", values=(item.capitalize(), f"${d['price']:.2f}"), tags=(item,))
        refresh_menu("")

        sb = self._searchbox(left, refresh_menu)
        sb.pack(pady=4)

        desc_box = tk.LabelFrame(left, text="Item Details", bg=self.theme["bg_frame"], fg=self.theme["fg"], labelanchor="n")
        desc_box.pack(fill="x", padx=6, pady=6)
        self.item_desc_label = tk.Label(desc_box, text="Select an item to see its description.", bg=self.theme["bg_frame"], fg=self.theme["fg"], wraplength=340, justify="left")
        self.item_desc_label.pack(fill="x", padx=6, pady=6)

        def on_select(_=None):
            sel = self.menu_tree.selection()
            if not sel: 
                self.item_desc_label.config(text="Select an item to see its description."); return
            tag = self.menu_tree.item(sel[0])['tags'][0]
            desc = self.app.inventory.get(tag, {}).get("description","No description.")
            self.item_desc_label.config(text=desc)
        self.menu_tree.bind("<<TreeviewSelect>>", on_select)

        tk.Button(left, text="Add Selected to Order ➔", command=self._add_from_menu, bg=self.theme["success"], fg="white").pack(pady=6, fill="x")

        # Right: Order
        right = tk.LabelFrame(main, text="Your Order", bg=self.theme["bg_frame"], fg=self.theme["fg"])
        right.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
        right.rowconfigure(0, weight=1); right.columnconfigure(0, weight=1)

        cols_order = ("Item","Qty","Subtotal")
        self.order_tree = ttk.Treeview(right, columns=cols_order, show="headings")
        for c in cols_order: self.order_tree.heading(c, text=c)
        self.order_tree.column("Qty", anchor="center", width=60); self.order_tree.column("Subtotal", anchor="e", width=120)
        self.order_tree.grid(row=0, column=0, columnspan=3, sticky="nsew", pady=6, padx=6)

        tk.Button(right, text="+", command=lambda: self._mod_qty(1), width=6).grid(row=1, column=0, sticky="e", padx=6, pady=4)
        tk.Button(right, text="-", command=lambda: self._mod_qty(-1), width=6).grid(row=1, column=1, sticky="w", padx=6, pady=4)
        tk.Button(right, text="Remove", command=self._remove_item, bg=self.theme["danger"], fg="white").grid(row=1, column=2, sticky="e", padx=6, pady=4)

        self.total_label = tk.Label(right, text="Total: $0.00", font=("Arial", 16, "bold"), bg=self.theme["bg_frame"], fg=self.theme["fg"])
        self.total_label.grid(row=2, column=0, columnspan=3, pady=(10,4))

        tk.Button(right, text="Checkout", command=self._checkout, bg=self.theme["success"], fg="white").grid(row=3, column=0, columnspan=3, pady=8, sticky="ew")
        tk.Button(right, text="Back", command=self._customer_menu, bg=self.theme["accent"], fg="white").grid(row=4, column=0, columnspan=3, pady=6, sticky="ew")

        self._refresh_order()

    def _add_from_menu(self):
        sel = self.menu_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Pick an item from the menu."); return
        tag = self.menu_tree.item(sel[0])['tags'][0]
        qty = simpledialog.askinteger("Quantity", f"How many {tag.capitalize()}s?", minvalue=1, maxvalue=99)
        if not qty: return
        res = self.app.add_to_order(tag, qty)
        if "Insufficient stock" in res or "not found" in res:
            messagebox.showerror("Error", res); return
        self._refresh_order()

    def _mod_qty(self, delta: int):
        sel = self.order_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Pick an item in your order."); return
        tag = self.order_tree.item(sel[0])['tags'][0]
        res = self.app.update_order_quantity(tag, delta)
        if "Insufficient stock" in res:
            messagebox.showerror("Error", res)
        self._refresh_order()

    def _remove_item(self):
        sel = self.order_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Pick an item to remove."); return
        tag = self.order_tree.item(sel[0])['tags'][0]
        self.app.remove_from_order(tag)
        self._refresh_order()

    def _refresh_order(self):
        for i in self.order_tree.get_children(): self.order_tree.delete(i)
        total = 0.0
        for item, qty in self.app.order.items():
            price = float(self.app.inventory[item]['price'])
            subtotal = price * qty
            total += subtotal
            self.order_tree.insert("", "end", values=(item.capitalize(), qty, f"${subtotal:.2f}"), tags=(item,))
        self.total_label.config(text=f"Total: ${total:.2f}")

    def _checkout(self):
        self._clear()
        frame = tk.Frame(self.master, bg=self.theme["bg_frame"], bd=6, relief="ridge")
        frame.pack(pady=30, padx=30, fill="both", expand=True)
        tk.Label(frame, text="Secure Checkout", font=("Arial", 18, "bold"), bg=self.theme["bg_frame"], fg=self.theme["fg"]).pack(pady=10)

        total = sum(self.app.inventory[it]['price'] * qty for it, qty in self.app.order.items())
        if total <= 0:
            tk.Label(frame, text="Your order is empty.", bg=self.theme["bg_frame"], fg=self.theme["fg"]).pack()
            tk.Button(frame, text="Back", command=self._ordering).pack(pady=10)
            return

        tk.Label(frame, text=f"Total Amount Due: ${total:.2f}", font=("Arial", 16, "bold"), bg=self.theme["bg_frame"], fg=self.theme["fg"]).pack(pady=10)
        tk.Label(frame, text="Select Payment Method:", bg=self.theme["bg_frame"], fg=self.theme["fg"]).pack(pady=6)

        var = tk.StringVar(value="cash")
        ttk.Combobox(frame, textvariable=var, values=["cash","card","online"], state="readonly").pack(pady=6)
        def complete():
            ok, msg = self.app.checkout(var.get())
            if ok:
                messagebox.showinfo("Success", msg)
                self._customer_menu()
            else:
                messagebox.showerror("Error", msg)
        tk.Button(frame, text="Complete Payment", command=complete, bg=self.theme["success"], fg="white").pack(pady=12)
        tk.Button(frame, text="Back", command=self._ordering, bg=self.theme["accent"], fg="white").pack(pady=6)
