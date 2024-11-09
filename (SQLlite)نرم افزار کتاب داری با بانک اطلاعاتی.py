import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3

class BookstoreDatabase:
    def __init__(self):
        self.connection = sqlite3.connect("bookstore.db")
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        # Create books table if it doesn't exist
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS books (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                title TEXT,
                                author TEXT,
                                price REAL,
                                stock INTEGER,
                                sold INTEGER DEFAULT 0,
                                discount REAL DEFAULT 0)''')
        # Create sales table if it doesn't exist
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS sales (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                book_id INTEGER,
                                quantity INTEGER,
                                total_price REAL,
                                FOREIGN KEY(book_id) REFERENCES books(id))''')
        self.connection.commit()

    def add_book(self, title, author, price, stock):
        self.cursor.execute('''INSERT INTO books (title, author, price, stock) 
                               VALUES (?, ?, ?, ?)''', (title, author, price, stock))
        self.connection.commit()

    def get_books(self, start, limit):
        self.cursor.execute('''SELECT * FROM books LIMIT ? OFFSET ?''', (limit, start))
        return self.cursor.fetchall()

    def get_book_by_title(self, title):
        self.cursor.execute('''SELECT * FROM books WHERE title LIKE ?''', ('%' + title + '%',))
        return self.cursor.fetchall()

    def update_book(self, book_id, title, author, price, stock):
        self.cursor.execute('''UPDATE books SET title = ?, author = ?, price = ?, stock = ? WHERE id = ?''', 
                            (title, author, price, stock, book_id))
        self.connection.commit()

    def delete_book(self, book_id):
        self.cursor.execute('''DELETE FROM books WHERE id = ?''', (book_id,))
        self.connection.commit()

    def record_sale(self, book_id, quantity, total_price):
        self.cursor.execute('''INSERT INTO sales (book_id, quantity, total_price) 
                               VALUES (?, ?, ?)''', (book_id, quantity, total_price))
        self.connection.commit()

    def get_total_sales(self):
        self.cursor.execute('''SELECT SUM(quantity), SUM(total_price) FROM sales''')
        return self.cursor.fetchone()

    def apply_discount(self, book_id, discount_percentage):
        self.cursor.execute('''UPDATE books SET discount = ? WHERE id = ?''', (discount_percentage, book_id))
        self.connection.commit()

class BookstoreGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("مدیریت کتاب‌فروشی")
        self.root.geometry("800x600")

        self.db = BookstoreDatabase()
        self.items_per_page = 5
        self.current_page = 0

        # Table (Treeview) setup for displaying books
        self.table = ttk.Treeview(root, columns=("Title", "Author", "Price", "Stock", "Discounted Price"), show="headings")
        self.table.heading("Title", text="عنوان")
        self.table.heading("Author", text="نویسنده")
        self.table.heading("Price", text="قیمت")
        self.table.heading("Stock", text="تعداد موجود")
        self.table.heading("Discounted Price", text="قیمت با تخفیف")
        self.table.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        # Form for adding a new book
        self.title_entry = ttk.Entry(root)
        self.author_entry = ttk.Entry(root)
        self.price_entry = ttk.Entry(root)
        self.stock_entry = ttk.Entry(root)
        ttk.Label(root, text="عنوان:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ttk.Label(root, text="نویسنده:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        ttk.Label(root, text="قیمت:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        ttk.Label(root, text="تعداد موجود:").grid(row=2, column=2, padx=5, pady=5, sticky="e")
        self.title_entry.grid(row=1, column=1, padx=5, pady=5)
        self.author_entry.grid(row=2, column=1, padx=5, pady=5)
        self.price_entry.grid(row=1, column=3, padx=5, pady=5)
        self.stock_entry.grid(row=2, column=3, padx=5, pady=5)
        ttk.Button(root, text="اضافه کردن کتاب", command=self.add_book).grid(row=3, columnspan=4, pady=10)

        # Pagination controls
        self.prev_button = ttk.Button(root, text="قبلی", command=self.prev_page)
        self.next_button = ttk.Button(root, text="بعدی", command=self.next_page)
        self.prev_button.grid(row=4, column=1, pady=10, sticky="e")
        self.next_button.grid(row=4, column=2, pady=10, sticky="w")

        # Additional buttons
        self.sell_button = ttk.Button(root, text="فروش کتاب", command=self.sell_book)
        self.search_button = ttk.Button(root, text="جستجوی کتاب", command=self.search_books_button)
        self.report_button = ttk.Button(root, text="گزارش فروش", command=self.show_sales_report)
        self.discount_button = ttk.Button(root, text="اعمال تخفیف", command=self.apply_discount)
        self.edit_button = ttk.Button(root, text="ویرایش کتاب", command=self.edit_book)
        self.delete_button = ttk.Button(root, text="حذف کتاب", command=self.delete_book)
        self.sell_button.grid(row=5, column=0, pady=5)
        self.search_button.grid(row=5, column=1, pady=5)
        self.report_button.grid(row=5, column=2, pady=5)
        self.discount_button.grid(row=5, column=3, pady=5)
        self.edit_button.grid(row=6, column=0, pady=5)
        self.delete_button.grid(row=6, column=1, pady=5)

        self.load_books()

    def load_books(self):
        """Load books for the current page from the database."""
        self.table.delete(*self.table.get_children())
        start = self.current_page * self.items_per_page
        books = self.db.get_books(start, self.items_per_page)
        for book in books:
            title, author, price, stock, sold, discount = book[1], book[2], book[3], book[4], book[5], book[6]
            discounted_price = price * (1 - discount / 100)
            self.table.insert("", "end", values=(title, author, price, stock, discounted_price))

    def add_book(self):
        title = self.title_entry.get()
        author = self.author_entry.get()
        try:
            price = float(self.price_entry.get())
            stock = int(self.stock_entry.get())
            if title and author:
                self.db.add_book(title, author, price, stock)
                self.title_entry.delete(0, tk.END)
                self.author_entry.delete(0, tk.END)
                self.price_entry.delete(0, tk.END)
                self.stock_entry.delete(0, tk.END)
                self.load_books()
            else:
                messagebox.showwarning("ورودی نامعتبر", "لطفا عنوان و نویسنده را وارد کنید.")
        except ValueError:
            messagebox.showwarning("ورودی نامعتبر", "قیمت یا موجودی معتبر وارد کنید.")

    def sell_book(self):
        title = simpledialog.askstring("فروش کتاب", "عنوان کتاب برای فروش را وارد کنید:")
        if title:
            books = self.db.get_book_by_title(title)
            if books:
                book = books[0]  # Assuming we only get one book with that title
                quantity = simpledialog.askinteger("فروش کتاب", f"تعداد را برای فروش {book[1]} وارد کنید:")
                if quantity:
                    try:
                        total_price = book[3] * quantity * (1 - book[6] / 100)  # Price with discount
                        self.db.record_sale(book[0], quantity, total_price)
                        self.load_books()
                    except ValueError as e:
                        messagebox.showerror("خطا", str(e))
            else:
                messagebox.showinfo("اطلاع", f"کتاب '{title}' پیدا نشد.")

    def apply_discount(self):
        title = simpledialog.askstring("اعمال تخفیف", "عنوان کتاب را برای تخفیف وارد کنید:")
        if title:
            books = self.db.get_book_by_title(title)
            if books:
                book = books[0]  # Assuming we only get one book with that title
                discount_percentage = simpledialog.askfloat("اعمال تخفیف", f"درصد تخفیف برای {book[1]} وارد کنید:")
                if discount_percentage is not None:
                    self.db.apply_discount(book[0], discount_percentage)
                    self.load_books()
            else:
                messagebox.showinfo("اطلاع", f"کتاب '{title}' پیدا نشد.")

    def edit_book(self):
        title = simpledialog.askstring("ویرایش کتاب", "عنوان کتاب را برای ویرایش وارد کنید:")
        if title:
            books = self.db.get_book_by_title(title)
            if books:
                book = books[0]  # Assuming we only get one book with that title
                new_title = simpledialog.askstring("ویرایش کتاب", "عنوان جدید را وارد کنید:", initialvalue=book[1])
                new_author = simpledialog.askstring("ویرایش کتاب", "نویسنده جدید را وارد کنید:", initialvalue=book[2])
                new_price = simpledialog.askfloat("ویرایش کتاب", "قیمت جدید را وارد کنید:", initialvalue=book[3])
                new_stock = simpledialog.askinteger("ویرایش کتاب", "موجودی جدید را وارد کنید:", initialvalue=book[4])
                if new_title and new_author and new_price is not None and new_stock is not None:
                    self.db.update_book(book[0], new_title, new_author, new_price, new_stock)
                    self.load_books()
            else:
                messagebox.showinfo("اطلاع", f"کتاب '{title}' پیدا نشد.")

    def delete_book(self):
        title = simpledialog.askstring("حذف کتاب", "عنوان کتاب را برای حذف وارد کنید:")
        if title:
            books = self.db.get_book_by_title(title)
            if books:
                book = books[0]
                self.db.delete_book(book[0])
                self.load_books()
            else:
                messagebox.showinfo("اطلاع", f"کتاب '{title}' پیدا نشد.")

    def show_sales_report(self):
        total_sales = self.db.get_total_sales()
        if total_sales:
            total_quantity, total_price = total_sales
            messagebox.showinfo("گزارش فروش", f"مجموع فروش: {total_quantity} کتاب\nمجموع درآمد: {total_price} تومان")
        else:
            messagebox.showinfo("گزارش فروش", "هیچ فروشی ثبت نشده است.")

    def search_books_button(self):
        title = simpledialog.askstring("جستجوی کتاب", "عنوان کتاب را وارد کنید:")
        if title:
            books = self.db.get_book_by_title(title)
            self.table.delete(*self.table.get_children())
            for book in books:
                title, author, price, stock, sold, discount = book[1], book[2], book[3], book[4], book[5], book[6]
                discounted_price = price * (1 - discount / 100)
                self.table.insert("", "end", values=(title, author, price, stock, discounted_price))

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_books()

    def next_page(self):
        self.current_page += 1
        self.load_books()

# Create the Tkinter window
root = tk.Tk()
bookstore_gui = BookstoreGUI(root)
root.mainloop()
