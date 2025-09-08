import json
from datetime import datetime

class Car:
    def __init__(self, make, model, year, price):
        self.make = make
        self.model = model
        self.year = year
        self.price = price

    def display_details(self):
        print(f"{self.year} {self.make} {self.model} - ${self.price:,.2f}")

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
        print(f"Name: {self.name}")
        print(f"Address: {self.address}")
        print(f"Phone: {self.phone}")

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

# Initialize an empty car inventory list, customer, and purchases list
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
    print("Inventory saved successfully!")

def save_purchases():
    data = [purchase.to_dict() for purchase in purchases]
    with open(PURCHASES_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print("Purchases saved successfully!")

def manager_menu():
    print("\nManager Menu:")
    print("1. View Inventory")
    print("2. Add Car")
    print("3. Remove Car")
    print("4. Save Inventory")
    print("5. Back to Main Menu")
    choice = input("Enter your choice: ")
    return choice

def customer_menu():
    print("\nCustomer Menu:")
    print("1. View Inventory")
    print("2. Purchase Car")
    print("3. Back to Main Menu")
    choice = input("Enter your choice: ")
    return choice

def view_inventory():
    if not inventory:
        print("There are no cars in the inventory.")
    else:
        print("\nCurrent Inventory:")
        for index, car in enumerate(inventory):
            print(f"{index + 1}. ", end="")
            car.display_details()

def add_car():
    make = input("Enter car make: ")
    model = input("Enter car model: ")
    try:
        year = int(input("Enter car year: "))
    except ValueError:
        print("Invalid year. Please enter a number.")
        return
    try:
        price = float(input("Enter car price: "))
    except ValueError:
        print("Invalid price. Please enter a number.")
        return
    new_car = Car(make, model, year, price)
    inventory.append(new_car)
    print(f"{new_car.year} {new_car.make} {new_car.model} added to inventory.")

def remove_car():
    if not inventory:
        print("There are no cars to remove.")
        return
    view_inventory()
    try:
        choice = int(input("Enter the number of the car to remove (or 0 to cancel): "))
    except ValueError:
        print("Invalid input. Please enter a number.")
        return
    if choice == 0:
        return
    if 1 <= choice <= len(inventory):
        removed_car = inventory.pop(choice - 1)
        print(f"\nRemoved: {removed_car.year} {removed_car.make} {removed_car.model}")
    else:
        print("Invalid choice. Please select a car from the list.")

def get_customer_info():
    name = input("Enter your name: ")
    address = input("Enter your address: ")
    phone = input("Enter your phone number: ")
    return Customer(name, address, phone)

def purchase_car():
    global current_customer
    if not inventory:
        print("The inventory is empty. Nothing to purchase.")
        return

    if current_customer is None:
        print("\nPlease enter your information first:")
        current_customer = get_customer_info()
        print("\nYour information:")
        current_customer.display_info()

    view_inventory()
    try:
        choice = int(input("Enter the number of the car you want to purchase (or 0 to cancel): "))
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    if choice == 0:
        return

    if 1 <= choice <= len(inventory):
        car_to_purchase = inventory.pop(choice - 1)  # Remove the car from inventory immediately
        print("\nCar purchased:")
        car_to_purchase.display_details()

        payment_method = input("Enter your payment method (e.g., Credit Card, Bank Transfer, Cash): ")
        print(f"\nProcessing purchase of {car_to_purchase.year} {car_to_purchase.make} {car_to_purchase.model} for ${car_to_purchase.price:,.2f} using {payment_method}.")
        print("Purchase successful!")

        # Record the purchase
        purchase = Purchase(current_customer, car_to_purchase, payment_method)
        purchases.append(purchase)
        save_purchases()  # Save the purchase immediately
        save_inventory()  # Save the updated inventory
    else:
        print("Invalid choice. Please select a car from the list.")

def main_menu():
    print("\nWelcome to the Car Dealership!")
    print("1. Manager Access")
    print("2. Customer Access")
    print("3. Exit")
    choice = input("Enter your choice: ")
    return choice

# Main program loop
if __name__ == "__main__":
    load_inventory()
    load_purchases()
    while True:
        main_choice = main_menu()
        if main_choice == '1':
            while True:
                manager_choice = manager_menu()
                if manager_choice == '1':
                    view_inventory()
                elif manager_choice == '2':
                    add_car()
                elif manager_choice == '3':
                    remove_car()
                elif manager_choice == '4':
                    save_inventory()
                elif manager_choice == '5':
                    break
                else:
                    print("Invalid choice. Please try again.")
        elif main_choice == '2':
            while True:
                customer_choice = customer_menu()
                if customer_choice == '1':
                    view_inventory()
                elif customer_choice == '2':
                    purchase_car()
                elif customer_choice == '3':
                    break
                else:
                    print("Invalid choice. Please try again.")
        elif main_choice == '3':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please try again.")
