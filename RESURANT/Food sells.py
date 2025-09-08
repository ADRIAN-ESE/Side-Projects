import json

class FoodSalesApp:
    def __init__(self, menu_file="menu.json", sales_file="sales.json"):
        self.menu_file = menu_file
        self.sales_file = sales_file
        self.inventory = self.load_data(self.menu_file)
        self.sales = self.load_data(self.sales_file)
        self.order = []

    def load_data(self, filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_data(self, data, filename):
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    def display_inventory(self):
        print("\n--- Inventory ---")  # Displayed as Inventory
        for item, details in self.inventory.items():
            print(f"{item}: Quantity - {details['quantity']}, Price - ${details['price']:.2f}")

    def add_item(self, item, quantity, price):
        if item in self.inventory:
            self.inventory[item]["quantity"] += quantity
        else:
            self.inventory[item] = {"quantity": quantity, "price": price}
        self.save_data(self.inventory, self.menu_file)
        print(f"{quantity} {item}(s) added to inventory.") # Displayed as inventory

    def update_item_price(self, item, price):
        if item in self.inventory:
            self.inventory[item]["price"] = price
            self.save_data(self.inventory, self.menu_file)
            print(f"{item} price updated to ${price:.2f}")
        else:
            print(f"{item} not found in inventory.") #Displayed as inventory

    def sell_item(self, item, quantity):
        if item in self.inventory and self.inventory[item]["quantity"] >= quantity:
            self.inventory[item]["quantity"] -= quantity
            total_price = self.inventory[item]["price"] * quantity
            if item not in self.sales:
                self.sales[item] = 0
            self.sales[item] += total_price
            self.save_data(self.inventory, self.menu_file)
            self.save_data(self.sales, self.sales_file)
            print(f"{quantity} {item}(s) sold for ${total_price:.2f}.")
        else:
            print(f"Insufficient stock or item not found.")

    def display_sales(self):
        print("\n--- Sales ---")
        total_sales = 0
        for item, sales_amount in self.sales.items():
            print(f"{item}: ${sales_amount:.2f}")
            total_sales += sales_amount
        print(f"Total Sales: ${total_sales:.2f}")

    def display_order(self):
        if self.order:
            print("\nYour Order:")
            total = 0
            for item, quantity in self.order:
                print(f"{quantity} x {item} - ${self.inventory[item]['price'] * quantity:.2f}")
                total += self.inventory[item]['price'] * quantity
            print(f"Total: ${total:.2f}")
        else:
            print("\nYour order is empty.")

    def add_to_order(self, item, quantity):
        if item in self.inventory and self.inventory[item]["quantity"] >= quantity:
            self.order.append((item, quantity))
            print(f"{quantity} {item}(s) added to your order.")
        else:
            print(f"Insufficient stock or item not found.")

    def remove_from_order(self, item):
        if not self.order:
            print("Your order is empty!")
        else:
            found = False
            for i, (order_item, _) in enumerate(self.order):
                if order_item == item:
                    del self.order[i]
                    found = True
                    print(f"{item} removed from your order.")
                    break
            if not found:
                print(f"{item} not found in your order.")

    def checkout(self):
        if not self.order:
            print("Your order is empty!")
        else:
            total = 0
            print("\n--- Receipt ---")
            for item, quantity in self.order:
                price = self.inventory[item]["price"]
                print(f"{quantity} x {item} - ${price * quantity:.2f}")
                total += price * quantity
            print(f"Total: ${total:.2f}")
            payment_method = input("Choose payment method (cash, card, online): ").lower()
            if payment_method in ["cash", "card", "online"]:
                print(f"Payment successful via {payment_method}.")
                for item, quantity in self.order:
                    self.sell_item(item, quantity)
                print("Thank you for your order!")
                self.order.clear()
            else:
                print("Invalid payment method.")

    def manager_menu(self):
        while True:
            print("\n--- Manager Menu ---")
            print("1. Display Inventory")
            print("2. Add Item to Inventory")
            print("3. Update Item Price")
            print("4. Display Sales")
            print("5. Back to Main Menu")

            choice = input("Enter your choice: ")

            if choice == "1":
                self.display_inventory()
            elif choice == "2":
                item = input("Enter item name: ")
                quantity = int(input("Enter quantity: "))
                price = float(input("Enter price: "))
                self.add_item(item, quantity, price)
            elif choice == "3":
                item = input("Enter item name: ")
                price = float(input("Enter new price: "))
                self.update_item_price(item, price)
            elif choice == "4":
                self.display_sales()
            elif choice == "5":
                break
            else:
                print("Invalid choice. Please try again.")

    def customer_menu(self):
        while True:
            print("\n--- Customer Menu ---")
            print("1. Add item to order")
            print("2. Remove item from order")
            print("3. Checkout")
            print("4. Display order")
            print("5. Back to Main Menu")

            choice = input("Enter your choice: ")


            if choice == "1":
                item = input("Enter item name: ").lower()
                quantity = int(input(f"How many {item}s do you want? "))
                self.add_to_order(item, quantity)
            elif choice == "2":
                item = input("Enter the item you want to remove: ").lower()
                self.remove_from_order(item)
            elif choice == "3":
                self.checkout()
            elif choice == "4":
                self.display_order()
            elif choice == "5":
                break
            else:
                print("Invalid choice. Please try again.")

    def run(self):
        while True:
            print("\n--- Food Sales App ---")
            print("1. Manager Menu")
            print("2. Customer Menu")
            print("3. Exit")

            choice = input("Enter your choice: ")

            if choice == "1":
                self.manager_menu()
            elif choice == "2":
                self.customer_menu()
            elif choice == "3":
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    app = FoodSalesApp()
    if not app.inventory:
        app.inventory = {
            "Pizza": {"quantity": 10, "price": 25.00},
            "Burger": {"quantity": 10, "price": 12.50},
            "Fries": {"quantity": 10, "price": 11.25},
            "Soda": {"quantity": 10, "price": 5.50},
            "Chicken wings": {"quantity": 10, "price": 11.75},
            "Steak": {"quantity": 10, "price": 50.25},
            "HotDogs":{"quantity": 40, "price": 22.00},
        }
        app.save_data(app.inventory, app.menu_file)
    app.run()