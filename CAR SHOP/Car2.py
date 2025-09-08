import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json
from datetime import datetime


# --- Your existing Car, Customer, Purchase classes (unchanged) ---
class Car:
    def __init__(self, make, model, year, price):
        self.make = make
        self.model = model
        self.year = year
        self.price = price

    def display_details(self):
        return f"{self.year} {self.make} {self.model} - ${self.price:,.2f}"

    def to_dict(self):
        return {
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "price": self.price
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data['make'], data['model'], data['year'], data['price'])


class Customer:
    def __init__(self, name, address, phone):
        self.name = name
        self.address = address
        self.phone = phone

    def display_info(self):
        return f"Name: {self.name}\nAddress: {self.address}\nPhone: {self.phone}"


class Purchase:
    def __init__(self, customer, car, payment_method):
        self.customer = customer
        self.car = car
        self.payment_method = payment_method
        self.purchase_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "customer": {
                "name": self.customer.name,
                "address": self.customer.address,
                "phone": self.customer.phone
            },
            "car": {
                "make": self.car.make,
                "model": self.car.model,
                "year": self.car.year,
                "price": self.car.price
            },
            "payment_method": self.payment_method,
            "purchase_date": self.purchase_date
        }

    @classmethod
    def from_dict(cls, data):
        customer = Customer(data['customer']['name'], data['customer']['address'], data['customer']['phone'])
        car = Car(data['car']['make'], data['car']['model'], data['car']['year'], data['car']['price'])
        return cls(customer, car, data['payment_method'])


# --- Global variables and file management (unchanged) ---
inventory = []
purchases = []
current_customer = None
INVENTORY_FILE = "inventory-Cars.json"
PURCHASES_FILE = "purchases.json"


def load_inventory():
    try:
        with open(INVENTORY_FILE, 'r') as f:
            data = json.load(f)
            inventory.extend([Car.from_dict(item) for item in data])
        print("Inventory loaded successfully!")
    except FileNotFoundError:
        print("No existing inventory file found. Starting with an empty inventory.")
    except json.JSONDecodeError:
        print("Error decoding inventory file. Starting with an empty inventory.")


def load_purchases():
    try:
        with open(PURCHASES_FILE, 'r') as f:
            data = json.load(f)
            purchases.extend([Purchase.from_dict(item) for item in data])
        print("Purchases loaded successfully!")
    except FileNotFoundError:
        print("No existing purchases file found. Starting with an empty purchase record.")
    except json.JSONDecodeError:
        print("Error decoding purchases file. Starting with an empty purchase record.")


def save_inventory():
    data = [car.to_dict() for car in inventory]
    with open(INVENTORY_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    messagebox.showinfo("Success", "Inventory saved successfully!")


def save_purchases():
    data = [purchase.to_dict() for purchase in purchases]
    with open(PURCHASES_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    messagebox.showinfo("Success", "Purchases saved successfully!")


# --- GUI Application Class ---
class CarDealershipApp:
    def __init__(self, master):
        self.master = master
        master.title("Orion Car Dealership Management")
        master.geometry("800x600")  # Set initial window size
        master.configure(bg="#ADD8E6")  # Light Blue background

        self.load_data()

        # Main frame
        self.main_frame = tk.Frame(master, bg="#ADD8E6")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        self.create_main_menu()

    def load_data(self):
        load_inventory()
        load_purchases()

    def create_main_menu(self):
        # Clear existing widgets
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        tk.Label(self.main_frame, text="Welcome to the Car Dealership!", font=("Arial", 24, "bold"), bg="#ADD8E6",
                 fg="#333333").pack(pady=30)

        # Buttons with styling
        button_style = {"font": ("Arial", 16), "bg": "#4CAF50", "fg": "white", "width": 20, "height": 2,
                        "relief": tk.RAISED, "bd": 5}
        button_pack_options = {"pady": 10}

        tk.Button(self.main_frame, text="Manager Access", command=self.manager_access, **button_style).pack(
            **button_pack_options)
        tk.Button(self.main_frame, text="Customer Access", command=self.customer_access, **button_style).pack(
            **button_pack_options)
        tk.Button(self.main_frame, text="Exit", command=self.exit_app, **button_style).pack(**button_pack_options)

    def manager_access(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        tk.Label(self.main_frame, text="Manager Menu", font=("Arial", 20, "bold"), bg="#ADD8E6", fg="#333333").pack(
            pady=20)

        button_style = {"font": ("Arial", 14), "bg": "#FFC107", "fg": "black", "width": 25, "height": 1,
                        "relief": tk.RAISED, "bd": 3}
        button_pack_options = {"pady": 8}

        tk.Button(self.main_frame, text="View Inventory", command=self.show_inventory_manager, **button_style).pack(
            **button_pack_options)
        tk.Button(self.main_frame, text="Add Car", command=self.add_car_gui, **button_style).pack(**button_pack_options)
        tk.Button(self.main_frame, text="Remove Car", command=self.remove_car_gui, **button_style).pack(
            **button_pack_options)
        tk.Button(self.main_frame, text="View Purchases History", command=self.show_purchases_history,
                  **button_style).pack(**button_pack_options)
        tk.Button(self.main_frame, text="Save Data", command=lambda: [save_inventory(), save_purchases()],
                  **button_style).pack(**button_pack_options)
        tk.Button(self.main_frame, text="Back to Main Menu", command=self.create_main_menu, **button_style).pack(
            **button_pack_options)

    def customer_access(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        tk.Label(self.main_frame, text="Customer Menu", font=("Arial", 20, "bold"), bg="#ADD8E6", fg="#333333").pack(
            pady=20)

        button_style = {"font": ("Arial", 14), "bg": "#2196F3", "fg": "white", "width": 25, "height": 1,
                        "relief": tk.RAISED, "bd": 3}
        button_pack_options = {"pady": 8}

        tk.Button(self.main_frame, text="View Available Cars", command=self.show_inventory_customer,
                  **button_style).pack(**button_pack_options)
        tk.Button(self.main_frame, text="Purchase Car", command=self.purchase_car_gui, **button_pack_options).pack()
        tk.Button(self.main_frame, text="Back to Main Menu", command=self.create_main_menu,
                  **button_pack_options).pack()

    def show_inventory_manager(self):
        # Create a new window for inventory display
        inventory_window = tk.Toplevel(self.master)
        inventory_window.title("Current Car Inventory")
        inventory_window.geometry("700x500")
        inventory_window.configure(bg="#F0F8FF")  # Alice Blue

        tk.Label(inventory_window, text="Current Car Inventory", font=("Arial", 18, "bold"), bg="#F0F8FF",
                 fg="#333333").pack(pady=15)

        if not inventory:
            tk.Label(inventory_window, text="There are no cars in the inventory.", font=("Arial", 12), bg="#F0F8FF",
                     fg="red").pack(pady=10)
        else:
            # Use Treeview for better tabular display
            tree = ttk.Treeview(inventory_window, columns=("Make", "Model", "Year", "Price"), show="headings")
            tree.heading("Make", text="Make")
            tree.heading("Model", text="Model")
            tree.heading("Year", text="Year")
            tree.heading("Price", text="Price")

            # Adjust column widths
            tree.column("Make", width=120)
            tree.column("Model", width=120)
            tree.column("Year", width=80)
            tree.column("Price", width=100)

            for i, car in enumerate(inventory):
                tree.insert("", "end", iid=i, values=(car.make, car.model, car.year, f"${car.price:,.2f}"))

            tree.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

            # Add a scrollbar
            scrollbar = ttk.Scrollbar(inventory_window, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            tree.pack(side="left", fill="both", expand=True)

    def show_inventory_customer(self):
        # Create a new window for inventory display
        inventory_window = tk.Toplevel(self.master)
        inventory_window.title("Available Cars")
        inventory_window.geometry("700x500")
        inventory_window.configure(bg="#F0FFFF")  # Azure background

        tk.Label(inventory_window, text="Available Cars", font=("Arial", 18, "bold"), bg="#F0FFFF", fg="#333333").pack(
            pady=15)

        if not inventory:
            tk.Label(inventory_window, text="Sorry, no cars are currently available.", font=("Arial", 12), bg="#F0FFFF",
                     fg="red").pack(pady=10)
        else:
            tree = ttk.Treeview(inventory_window, columns=("Make", "Model", "Year", "Price"), show="headings")
            tree.heading("Make", text="Make")
            tree.heading("Model", text="Model")
            tree.heading("Year", text="Year")
            tree.heading("Price", text="Price")

            tree.column("Make", width=120)
            tree.column("Model", width=120)
            tree.column("Year", width=80)
            tree.column("Price", width=100)

            for i, car in enumerate(inventory):
                tree.insert("", "end", iid=i, values=(car.make, car.model, car.year, f"${car.price:,.2f}"))

            tree.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

            scrollbar = ttk.Scrollbar(inventory_window, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            tree.pack(side="left", fill="both", expand=True)

    def add_car_gui(self):
        add_window = tk.Toplevel(self.master)
        add_window.title("Add New Car")
        add_window.geometry("400x300")
        add_window.configure(bg="#FFFACD")  # Lemon Chiffon

        tk.Label(add_window, text="Add New Car Details", font=("Arial", 16, "bold"), bg="#FFFACD", fg="#333333").pack(
            pady=10)

        form_frame = tk.Frame(add_window, bg="#FFFACD")
        form_frame.pack(pady=10)

        labels = ["Make:", "Model:", "Year:", "Price:"]
        entries = {}

        for i, text in enumerate(labels):
            tk.Label(form_frame, text=text, bg="#FFFACD", font=("Arial", 12)).grid(row=i, column=0, padx=5, pady=5,
                                                                                   sticky="w")
            entry = tk.Entry(form_frame, width=30, font=("Arial", 12))
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[text.replace(":", "").strip().lower()] = entry

        def save_new_car():
            make = entries["make"].get().strip()
            model = entries["model"].get().strip()
            year_str = entries["year"].get().strip()
            price_str = entries["price"].get().strip()

            if not all([make, model, year_str, price_str]):
                messagebox.showerror("Input Error", "All fields are required!")
                return

            try:
                year = int(year_str)
                price = float(price_str)
                if year <= 1900 or price <= 0:
                    messagebox.showerror("Input Error", "Year must be greater than 1900 and Price must be positive.")
                    return
            except ValueError:
                messagebox.showerror("Input Error", "Year and Price must be valid numbers.")
                return

            new_car = Car(make, model, year, price)
            inventory.append(new_car)
            save_inventory()
            messagebox.showinfo("Success", f"{new_car.year} {new_car.make} {new_car.model} added successfully!")
            add_window.destroy()

        tk.Button(add_window, text="Add Car", command=save_new_car, bg="#4CAF50", fg="white", font=("Arial", 14),
                  relief=tk.RAISED, bd=3).pack(pady=15)

    def remove_car_gui(self):
        if not inventory:
            messagebox.showinfo("Info", "There are no cars to remove.")
            return

        remove_window = tk.Toplevel(self.master)
        remove_window.title("Remove Car")
        remove_window.geometry("600x400")
        remove_window.configure(bg="#FFDAB9")  # Peach Puff

        tk.Label(remove_window, text="Select a Car to Remove", font=("Arial", 16, "bold"), bg="#FFDAB9",
                 fg="#333333").pack(pady=10)

        # Use Listbox for selection
        listbox_frame = tk.Frame(remove_window, bg="#FFDAB9")
        listbox_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        car_listbox = tk.Listbox(listbox_frame, width=70, height=15, font=("Arial", 12), yscrollcommand=scrollbar.set)
        for i, car in enumerate(inventory):
            car_listbox.insert(tk.END, f"{i + 1}. {car.display_details()}")
        car_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=car_listbox.yview)

        def perform_remove():
            selected_indices = car_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("No Selection", "Please select a car to remove.")
                return

            index_to_remove = selected_indices[0]  # Get the first selected item

            # Confirm removal
            confirm = messagebox.askyesno("Confirm Removal",
                                          f"Are you sure you want to remove:\n{inventory[index_to_remove].display_details()}?")
            if confirm:
                removed_car = inventory.pop(index_to_remove)
                save_inventory()
                messagebox.showinfo("Success", f"Removed: {removed_car.display_details()}")
                remove_window.destroy()  # Close the removal window
                # Refresh the list if it was open somewhere else (optional)
                # self.show_inventory_manager() # If you want to auto-refresh main inventory view

        tk.Button(remove_window, text="Remove Selected Car", command=perform_remove, bg="#FF4500", fg="white",
                  font=("Arial", 14), relief=tk.RAISED, bd=3).pack(pady=15)

    def show_purchases_history(self):
        purchases_window = tk.Toplevel(self.master)
        purchases_window.title("Purchase History")
        purchases_window.geometry("800x600")
        purchases_window.configure(bg="#F0FFF0")  # Honeydew background

        tk.Label(purchases_window, text="Car Purchase History", font=("Arial", 18, "bold"), bg="#F0FFF0",
                 fg="#333333").pack(pady=15)

        if not purchases:
            tk.Label(purchases_window, text="No purchase records found.", font=("Arial", 12), bg="#F0FFF0",
                     fg="red").pack(pady=10)
        else:
            tree = ttk.Treeview(purchases_window, columns=("Date", "Customer", "Car", "Payment Method"),
                                show="headings")
            tree.heading("Date", text="Date")
            tree.heading("Customer", text="Customer Name")
            tree.heading("Car", text="Car Details")
            tree.heading("Payment Method", text="Payment Method")

            tree.column("Date", width=150)
            tree.column("Customer", width=150)
            tree.column("Car", width=250)
            tree.column("Payment Method", width=120)

            for i, purchase in enumerate(purchases):
                customer_name = purchase.customer.name
                car_details = f"{purchase.car.year} {purchase.car.make} {purchase.car.model} (${purchase.car.price:,.2f})"
                tree.insert("", "end", iid=i,
                            values=(purchase.purchase_date, customer_name, car_details, purchase.payment_method))

            tree.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

            scrollbar = ttk.Scrollbar(purchases_window, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            tree.pack(side="left", fill="both", expand=True)

    def purchase_car_gui(self):
        global current_customer
        if not inventory:
            messagebox.showinfo("Info", "The inventory is empty. Nothing to purchase.")
            return

        if current_customer is None:
            # Prompt for customer info
            customer_name = simpledialog.askstring("Customer Info", "Enter your name:")
            if not customer_name: return  # User cancelled
            customer_address = simpledialog.askstring("Customer Info", "Enter your address:")
            if not customer_address: return
            customer_phone = simpledialog.askstring("Customer Info", "Enter your phone number:")
            if not customer_phone: return

            current_customer = Customer(customer_name, customer_address, customer_phone)
            messagebox.showinfo("Your Information",
                                f"Welcome, {current_customer.name}!\nYour details have been saved for this session.")

        purchase_window = tk.Toplevel(self.master)
        purchase_window.title("Purchase a Car")
        purchase_window.geometry("700x500")
        purchase_window.configure(bg="#E0FFFF")  # Light Cyan

        tk.Label(purchase_window, text="Select a Car to Purchase", font=("Arial", 16, "bold"), bg="#E0FFFF",
                 fg="#333333").pack(pady=10)

        if not inventory:
            tk.Label(purchase_window, text="No cars available for purchase.", font=("Arial", 12), bg="#E0FFFF",
                     fg="red").pack(pady=10)
            return

        # Use Listbox for selection
        listbox_frame = tk.Frame(purchase_window, bg="#E0FFFF")
        listbox_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        car_listbox = tk.Listbox(listbox_frame, width=70, height=15, font=("Arial", 12), yscrollcommand=scrollbar.set)
        for i, car in enumerate(inventory):
            car_listbox.insert(tk.END, f"{i + 1}. {car.display_details()}")
        car_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=car_listbox.yview)

        def process_purchase():
            selected_indices = car_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("No Selection", "Please select a car to purchase.")
                return

            index_to_purchase = selected_indices[0]
            car_to_purchase = inventory[index_to_purchase]

            payment_method = simpledialog.askstring("Payment Method",
                                                    "Enter your payment method (e.g., Credit Card, Bank Transfer, Cash):")
            if not payment_method:
                return  # User cancelled

            confirm = messagebox.askyesno("Confirm Purchase",
                                          f"Confirm purchase of:\n{car_to_purchase.display_details()}\nPayment Method: {payment_method}?")
            if confirm:
                # Remove the car from inventory
                purchased_car = inventory.pop(index_to_purchase)

                # Record the purchase
                new_purchase = Purchase(current_customer, purchased_car, payment_method)
                purchases.append(new_purchase)

                save_purchases()
                save_inventory()
                messagebox.showinfo("Purchase Successful",
                                    f"You have successfully purchased:\n{purchased_car.display_details()}")
                purchase_window.destroy()  # Close the purchase window
                # Refresh inventory views if open elsewhere (optional)

        tk.Button(purchase_window, text="Purchase Selected Car", command=process_purchase, bg="#28A745", fg="white",
                  font=("Arial", 14), relief=tk.RAISED, bd=3).pack(pady=15)

    def exit_app(self):
        if messagebox.askyesno("Exit", "Do you want to save data before exiting?"):
            save_inventory()
            save_purchases()
        self.master.destroy()


# Main application execution
if __name__ == "__main__":
    root = tk.Tk()
    app = CarDealershipApp(root)
    root.mainloop()