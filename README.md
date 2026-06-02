# 🛠️ Side Projects

A collection of personal projects built while learning and practising software development. The repo spans Python desktop apps, vanilla JavaScript web apps, and a browser-based game — covering a range of domains from inventory management to restaurant operations.

---

## 📁 Project Index

| Project | Type | Tech Stack |
|---|---|---|
| [CAR SHOP](#-car-shop) | Python CLI/OOP | Python, JSON |
| [CARS](#-cars-web) | Web App | HTML, CSS, JavaScript |
| [Finance System](#-finance-system) | Web App | HTML, CSS, JavaScript |
| [Food Sells](#-food-sells) | Desktop GUI | Python, Tkinter |
| [Car Racing Game](#-car-racing-game) | Browser Game | HTML, CSS, JavaScript |
| [IMPROVED Book](#-improved-book) | Desktop GUI | Python, Tkinter |
| [Inventory](#-inventory) | Web App | HTML, CSS, JavaScript |
| [Pro Job — User Manager Pro](#-pro-job--user-manager-pro) | Desktop App | Python, CustomTkinter |
| [Pro Job — Archer Enterprise](#-pro-job--archer-enterprise) | Desktop + Web | Python, CustomTkinter, Flask |
| [Restaurant](#-restaurant-web) | Web App | HTML, CSS, JavaScript |
| [Restaurant Improvements](#-restaurant-improvements) | Desktop GUI | Python, Tkinter |
| [Ship.py](#-shippy) | Python CLI | Python |
| [SmartPlanner](#-smartplanner) | Web App | HTML, CSS, JavaScript |
| [Food 2 — Orion Kitchen](#-food-2--orion-kitchen) | Web App | HTML, CSS, JavaScript |

---

## 🚗 CAR SHOP

**`/CAR SHOP`**

A Python command-line application for managing a car dealership. Uses object-oriented programming with classes for `Car`, `Customer`, and `Purchase`. Data is persisted to JSON files.

**Features**
- Browse and manage car inventory
- Register customer details
- Record purchases with payment method tracking
- Persistent storage via `inventory-Cars.json` and `purchases.json`

**Run**
```bash
cd "CAR SHOP"
python CARS.py
```

---

## 🌐 CARS Web

**`/CARS`**

A web-based car dealership application with separate views for customers and managers.

**Features**
- Customer view: browse available cars and make purchases
- Manager view: add, remove, and manage inventory (password-protected)
- Persistent state via `localStorage`
- Clean landing page and login flow

**Run** — Open `index.html` in a browser.

---

## 💰 Finance System

**`/Finance System`**

A browser-based personal finance manager with user authentication.

**Features**
- Register and login with username/password
- Dashboard for tracking income and expenses
- Secure login screen before accessing financial data

**Run** — Open `Index.html` in a browser.

---

## 🍔 Food Sells

**`/Food Sells`**

A Python desktop GUI application for managing food sales, built with Tkinter.

**Features**
- Menu management loaded from `menu.json`
- Sales recording and reporting
- Configuration via `config.json`
- Role-based security (`security.py`)
- Data persistence handled by `datastore.py`

**Requirements**
```bash
pip install tkinter
```

**Run**
```bash
cd "Food Sells"
python main.py
```

---

## 🏎️ Car Racing Game

**`/Games/Car racing`**

A browser-based 2D car racing game built with vanilla JavaScript.

**Features**
- Player-controlled car with obstacle avoidance
- Level configuration system (`LevelConfig.js`)
- Power-ups and particle effects
- Animated road stripes and game objects

**Run** — Open `index.html` in a browser.

---

## 📚 IMPROVED Book

**`/IMPROVED Book`**

A Python desktop application for managing a bookstore/library, built with Tkinter.

**Features**
- Add, search, and remove books (stored on a virtual shelf)
- Borrow and return system with due dates
- Admin password protection via `config.JSON`
- UUID-based book IDs for reliable tracking
- Persistent storage via `shelf.json` and `borrowed.json`

**Run**
```bash
cd "IMPROVED Book"
python book1.py
```

---

## 📦 Inventory

**`/Inventory`**

A web-based inventory management system with role-based access.

**Features**
- Manager and staff roles (password-protected)
- Add, edit, and delete inventory items
- Low stock alerts (threshold: 5 units)
- All data persisted in `localStorage`

**Run** — Open `index.html` in a browser.

---

## 👥 Pro Job — User Manager Pro

**`/Pro Job/user_manager_pro.py`**

A full-featured desktop user management application built with CustomTkinter.

**Features**
- Live dashboard with user stats
- Add, edit, delete, search, and filter users
- Promotion request and approval workflow
- Import from JSON/CSV; export to JSON/CSV/Excel
- Dark/Light mode toggle
- Auto-save on every write

**Requirements**
```bash
pip install customtkinter openpyxl
```

**Run**
```bash
cd "Pro Job"
python user_manager_pro.py
```

---

## 🏢 Pro Job — Archer Enterprise

**`/Pro Job/Archer`**

A corporate management system available in both desktop and web editions. Both editions share the same `archer_data.json` data file.

**Features**
- Employee and department management
- HR workflows and manager access levels
- Matplotlib charts (desktop edition)
- Web edition accessible from a browser

**Default Accounts**
| Username | Password | Role |
|---|---|---|
| admin | admin123 | Admin |
| hr_manager | hr123 | HR Manager |
| manager1 | mgr123 | Manager |
| staff1 | staff123 | Staff |

**Requirements**
```bash
pip install customtkinter openpyxl matplotlib
```

**Run (Desktop)**
```bash
cd "Pro Job/Archer"
python archer_desktop.py
```

**Run (Web)**
```bash
cd "Pro Job/Archer"
python archer_web.py
```

---

## 🍽️ Restaurant Web

**`/Resturant`**

A web-based restaurant ordering and management system.

**Features**
- Customer ordering interface
- Manager dashboard for menu and order management
- Menu loaded from `menu.json`
- Styled with a dedicated `style.css`

**Run** — Open `index.html` in a browser.

---

## 🍽️ Restaurant Improvements

**`/Resturant Improvements`**

An upgraded Python desktop version of the restaurant system, rebuilt with Tkinter and a persistent SQLite database.

**Features**
- Full GUI for order taking and menu management
- Sales history stored in `sales.db` (SQLite)
- Role-based security
- Configuration via `config.json`

**Run**
```bash
cd "Resturant Improvements"
python main.py
```

---

## 🚢 Ship.py

**`/Ship.py`**

A Python command-line shipment tracker.

**Features**
- Add new shipments with origin, destination, weight, and payment method
- Display all shipments in a formatted table
- Update shipment status (Pending → In Transit → Delivered)

**Run**
```bash
python Ship.py
```

---

## 📅 SmartPlanner

**`/SmartPlannerSplit 1`**

A browser-based productivity and task management dashboard with user authentication.

**Features**
- User registration and login
- Task creation, completion tracking, and deletion
- Visual progress ring showing task completion percentage
- Motivational imagery and encouraging UI
- Settings panel
- Data persisted via `localStorage`

**Run** — Open `login.html` in a browser.

---

## 🍜 Food 2 — Orion Kitchen

**`/food 2`**

A polished web app for a restaurant called **Orion Kitchen**, with separate customer and manager experiences.

**Features**
- Customer view: browse menu and place orders
- Manager view: manage menu items and view sales
- Preferences and sales data stored in `localStorage`
- Default manager password: `admin123`

**Run** — Open `index.html` in a browser.

---

## 🧰 Tech Overview

| Technology | Used In |
|---|---|
| **Python** | CAR SHOP, Food Sells, IMPROVED Book, Restaurant Improvements, Pro Job, Ship.py |
| **Tkinter / CustomTkinter** | Food Sells, IMPROVED Book, Restaurant Improvements, User Manager Pro, Archer |
| **HTML / CSS / JavaScript** | CARS, Finance System, Car Racing Game, Inventory, Restaurant Web, SmartPlanner, Orion Kitchen |
| **JSON** | All projects (config and data storage) |
| **SQLite** | Restaurant Improvements |
| **openpyxl / Matplotlib** | User Manager Pro, Archer Enterprise |

---

## 🚀 Getting Started

Clone the repository and navigate to any project folder:

```bash
git clone https://github.com/ADRIAN-ESE/Side-Projects.git
cd Side-Projects
```

For Python projects, install dependencies as noted in each section above, then run the relevant `.py` file. For web projects, open the `index.html` (or equivalent entry point) directly in your browser — no build step required.
