import uuid
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, simpledialog


# ---------------- Load Config ----------------
def load_config(config_file="config.json"):
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
            return config.get("admin_password", "admin123")
    except (FileNotFoundError, json.JSONDecodeError):
        return "admin123"


# ---------------- Book Dataclass ----------------
@dataclass
class Book:
    title: str
    author: str
    genre: str
    price: float
    stock: int
    book_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])  # Short ID if not provided

    def __str__(self):
        return f"[{self.book_id}] {self.title} by {self.author} | {self.genre} | ${self.price} | Stock: {self.stock}"

    def to_dict(self):
        return asdict(self)


# ---------------- Backend Logic ----------------
class OnlineBookstore:
    def __init__(self, shelf_file="shelf.json", borrow_file="borrowed.json"):
        self.books = {}
        self.borrowed = {}
        self.shelf_file = shelf_file
        self.borrow_file = borrow_file
        self.load_shelf()
        self.load_borrowed()

    def load_shelf(self):
        try:
            with open(self.shelf_file, "r") as f:
                data = json.load(f)
                for book_data in data:
                    book = Book(**{k: v for k, v in book_data.items() if k != "book_id"})
                    book.book_id = book_data.get("book_id", str(uuid.uuid4())[:8])
                    self.books[book.book_id] = book
        except (FileNotFoundError, json.JSONDecodeError):
            self.save_shelf()

    def save_shelf(self):
        data = [book.to_dict() for book in self.books.values()]
        with open(self.shelf_file, "w") as f:
            json.dump(data, f, indent=4)

    def load_borrowed(self):
        try:
            with open(self.borrow_file, "r") as f:
                self.borrowed = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.borrowed = {}
            self.save_borrowed()

    def save_borrowed(self):
        with open(self.borrow_file, "w") as f:
            json.dump(self.borrowed, f, indent=4)

    # ---------------- Utility ----------------
    def find_book(self, identifier):
        """Find a book by ID or exact title (case-insensitive)."""
        # Check by ID
        if identifier in self.books:
            return self.books[identifier]

        # Check by Title
        for book in self.books.values():
            if book.title.lower() == identifier.lower():
                return book
        return None

    # ---------------- Book Operations ----------------
    def add_book(self, title, author, genre, price, stock):
        if stock < 0 or price < 0:
            return "❌ Price and stock must be non-negative."
        book = Book(title, author, genre, price, stock)
        self.books[book.book_id] = book
        self.save_shelf()
        return f"✅ Book '{book.title}' added successfully with ID: {book.book_id}"

    def list_books(self):
        return list(self.books.values())

    def search_book(self, query):
        return [
            book for book in self.books.values()
            if query.lower() in book.title.lower()
            or query.lower() in book.author.lower()
            or query.lower() in book.genre.lower()
        ]

    # ---------------- Borrow System ----------------
    def borrow_book(self, identifier, borrower):
        book = self.find_book(identifier)
        if not book:
            return "❌ Book not found."
        if book.stock <= 0:
            return f"❌ '{book.title}' is out of stock."

        book.stock -= 1
        borrow_date = datetime.now().strftime("%Y-%m-%d")
        due_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

        self.borrowed.setdefault(book.book_id, []).append({
            "borrower": borrower,
            "borrow_date": borrow_date,
            "due_date": due_date
        })
        self.save_shelf()
        self.save_borrowed()
        return f"✅ '{book.title}' borrowed by {borrower}. Due on {due_date}."

    def return_book(self, identifier, borrower):
        book = self.find_book(identifier)
        if not book:
            return "❌ Book not found."

        book_id = book.book_id
        if book_id not in self.borrowed:
            return "❌ This book was not borrowed."

        records = self.borrowed[book_id]
        for record in records:
            if record["borrower"] == borrower:
                records.remove(record)
                book.stock += 1
                if not records:
                    del self.borrowed[book_id]
                self.save_shelf()
                self.save_borrowed()
                return f"✅ '{book.title}' returned by {borrower}."
        return "❌ This borrower did not borrow this book."

    def view_borrowed(self, borrower=None):
        results = []
        for book_id, records in self.borrowed.items():
            book = self.books.get(book_id)
            if not book:
                continue
            for record in records:
                if borrower and record["borrower"] != borrower:
                    continue
                due_date = datetime.strptime(record["due_date"], "%Y-%m-%d")
                overdue = datetime.now() > due_date
                results.append({
                    "title": book.title,
                    "borrower": record["borrower"],
                    "borrow_date": record["borrow_date"],
                    "due_date": record["due_date"],
                    "overdue": overdue
                })
        return results


# ---------------- Tkinter GUI ----------------
class BookstoreUI:
    THEMES = {
        "Light": {"bg": "#d0e6fa", "btn_bg": "#5DADE2", "text_bg": "#ffffff", "text_fg": "#2C3E50"},
        "Dark": {"bg": "#2C3E50", "btn_bg": "#34495E", "text_bg": "#1C2833", "text_fg": "#ECF0F1"},
        "Green": {"bg": "#dff0d8", "btn_bg": "#27AE60", "text_bg": "#fefefe", "text_fg": "#145A32"}
    }

    def __init__(self, root, bookstore, is_admin=False):
        self.root = root
        self.bookstore = bookstore
        self.is_admin = is_admin
        self.root.title("📚 Online Bookstore")

        # default theme
        self.current_theme = "Light"
        self.apply_theme()

        # Buttons
        tk.Button(root, text="List All Books", command=self.list_books, bg=self.theme["btn_bg"], fg="white").pack(fill="x", pady=2)
        tk.Button(root, text="Search Book", command=self.search_book, bg=self.theme["btn_bg"], fg="white").pack(fill="x", pady=2)
        tk.Button(root, text="Borrow Book", command=self.borrow_book, bg=self.theme["btn_bg"], fg="white").pack(fill="x", pady=2)
        tk.Button(root, text="Return Book", command=self.return_book, bg=self.theme["btn_bg"], fg="white").pack(fill="x", pady=2)
        tk.Button(root, text="View Borrowed", command=self.view_borrowed, bg=self.theme["btn_bg"], fg="white").pack(fill="x", pady=2)

        if self.is_admin:
            tk.Button(root, text="➕ Add Book (Admin)", command=self.add_book, bg="#27AE60", fg="white").pack(fill="x", pady=2)

        # Theme switch
        tk.Button(root, text="🎨 Change Theme", command=self.change_theme, bg="#8E44AD", fg="white").pack(fill="x", pady=2)

        tk.Button(root, text="Exit", command=root.quit, bg="#E74C3C", fg="white").pack(fill="x", pady=2)

        # Text area
        self.text_area = tk.Text(root, wrap="word", height=20, width=80)
        self.text_area.pack(padx=10, pady=10)
        self.apply_theme()

    def apply_theme(self):
        self.theme = self.THEMES[self.current_theme]
        self.root.configure(bg=self.theme["bg"])
        if hasattr(self, "text_area"):
            self.text_area.config(bg=self.theme["text_bg"], fg=self.theme["text_fg"])

    def change_theme(self):
        themes = list(self.THEMES.keys())
        current_index = themes.index(self.current_theme)
        self.current_theme = themes[(current_index + 1) % len(themes)]
        self.apply_theme()

    def show_message(self, message):
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, message)

    def list_books(self):
        books = self.bookstore.list_books()
        if not books:
            self.show_message("No books available.")
            return
        text = "\n".join(str(book) for book in books)
        self.show_message(text)

    def search_book(self):
        query = simpledialog.askstring("Search Book", "Enter title/author/genre:")
        if not query:
            return
        results = self.bookstore.search_book(query)
        if results:
            text = "\n".join(str(book) for book in results)
        else:
            text = "No books found."
        self.show_message(text)

    def borrow_book(self):
        identifier = simpledialog.askstring("Borrow Book", "Enter Book ID or Title:")
        borrower = simpledialog.askstring("Borrow Book", "Enter your name:")
        if identifier and borrower:
            result = self.bookstore.borrow_book(identifier, borrower)
            messagebox.showinfo("Borrow Book", result)

    def return_book(self):
        identifier = simpledialog.askstring("Return Book", "Enter Book ID or Title:")
        borrower = simpledialog.askstring("Return Book", "Enter your name:")
        if identifier and borrower:
            result = self.bookstore.return_book(identifier, borrower)
            messagebox.showinfo("Return Book", result)

    def view_borrowed(self):
        borrower = simpledialog.askstring("View Borrowed", "Enter your name (leave blank for all):")
        records = self.bookstore.view_borrowed(borrower if borrower else None)
        if not records:
            self.show_message("No borrowed books.")
            return
        lines = []
        for r in records:
            status = "❌ Overdue" if r["overdue"] else "✅ On Time"
            lines.append(f"{r['title']} | Borrower: {r['borrower']} | Borrowed: {r['borrow_date']} | Due: {r['due_date']} | {status}")
        self.show_message("\n".join(lines))

    def add_book(self):
        title = simpledialog.askstring("Add Book", "Enter Title:")
        author = simpledialog.askstring("Add Book", "Enter Author:")
        genre = simpledialog.askstring("Add Book", "Enter Genre:")

        try:
            price = float(simpledialog.askstring("Add Book", "Enter Price:"))
            stock = int(simpledialog.askstring("Add Book", "Enter Stock:"))
        except (TypeError, ValueError):
            messagebox.showerror("Error", "❌ Invalid input for price/stock.")
            return

        result = self.bookstore.add_book(title, author, genre, price, stock)
        messagebox.showinfo("Add Book", result)


# ---------------- Main ----------------
def main():
    bookstore = OnlineBookstore()
    admin_password = load_config()

    root = tk.Tk()
    root.withdraw()
    user_type = simpledialog.askstring("Login", "Enter role (admin/user):")

    is_admin = False
    if user_type and user_type.lower() == "admin":
        password = simpledialog.askstring("Admin Login", "Enter admin password:", show="*")
        if password == admin_password:
            is_admin = True
            messagebox.showinfo("Login", "✅ Admin login successful!")
        else:
            messagebox.showerror("Login", "❌ Incorrect password. Logging in as User.")
    elif user_type and user_type.lower() == "user":
        messagebox.showinfo("Login", "✅ Logged in as User.")
    else:
        messagebox.showerror("Login", "❌ Invalid role. Defaulting to User.")

    root.deiconify()
    app = BookstoreUI(root, bookstore, is_admin=is_admin)
    root.mainloop()


if __name__ == "__main__":
    main()
