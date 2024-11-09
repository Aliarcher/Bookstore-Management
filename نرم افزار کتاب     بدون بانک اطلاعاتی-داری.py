import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class Book:
    def __init__(self, title, author, price, stock):
        self.title = title
        self.author = author
        self.price = price
        self.stock = stock
        self.sold = 0
        self.discount = 0

    def add_stock(self, quantity):
        self.stock += quantity

    def sell_book(self, quantity):
        if self.stock >= quantity:
            self.stock -= quantity
            self.sold += quantity
        else:
            raise ValueError("موجودی کافی نیست.")

    def apply_discount(self, discount_percentage):
        self.discount = discount_percentage

    def get_discounted_price(self):
        return self.price * (1 - self.discount / 100)

    def __str__(self):
        return f"عنوان: {self.title}, نویسنده: {self.author}, قیمت: {self.price}, تخفیف: {self.discount}%, قیمت نهایی: {self.get_discounted_price()}, موجودی: {self.stock}, فروخته شده: {self.sold}"


class SalesTracker:
    def __init__(self):
        self.sales = []

    def record_sale(self, book, quantity):
        if book.stock >= quantity:
            book.sell_book(quantity)
            self.sales.append((book.title, quantity, book.get_discounted_price() * quantity))
        else:
            raise ValueError("موجودی کافی نیست.")

    def total_sales(self):
        total_books = sum(sale[1] for sale in self.sales)
        total_income = sum(sale[2] for sale in self.sales)
        return total_books, total_income


class BookstoreGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("مدیریت کتاب‌فروشی")
        self.root.geometry("800x600")

        self.books = []
        self.tracker = SalesTracker()
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
        """Load books for the current page."""
        self.table.delete(*self.table.get_children())
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        for book in self.books[start:end]:
            self.table.insert("", "end", values=(book.title, book.author, book.price, book.stock, book.get_discounted_price()))          

    def add_book(self):
        title = self.title_entry.get()
        author = self.author_entry.get()
        try:
            price = float(self.price_entry.get())
            stock = int(self.stock_entry.get())
            if title and author:
                book = Book(title, author, price, stock)
                self.books.append(book)
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
            book = self.search_books(title=title)
            if book:
                quantity = simpledialog.askinteger("فروش کتاب", f"تعداد را برای فروش {book[0].title} وارد کنید:")
                if quantity:
                    try:
                        self.tracker.record_sale(book[0], quantity)
                        self.load_books()
                    except ValueError as e:
                        messagebox.showerror("خطا", str(e))
            else:
                messagebox.showinfo("اطلاع", f"کتاب '{title}' پیدا نشد.")

    def apply_discount(self):
        title = simpledialog.askstring("اعمال تخفیف", "عنوان کتاب را برای تخفیف وارد کنید:")
        if title:
            book = self.search_books(title=title)
            if book:
                try:
                    discount = float(simpledialog.askstring("تخفیف", "درصد تخفیف را وارد کنید:"))
                    book[0].apply_discount(discount)
                    self.load_books()
                except ValueError:
                    messagebox.showwarning("ورودی نامعتبر", "درصد تخفیف معتبر وارد کنید.")

    def show_sales_report(self):
        total_books, total_income = self.tracker.total_sales()
        report = f"کل کتاب‌های فروخته شده: {total_books}\nکل درآمد حاصله: {total_income}"
        messagebox.showinfo("گزارش فروش", report)

    def search_books(self, title=None, author=None):
        """Search for books based on title or author."""
        results = []
        for book in self.books:
            if (title and title.lower() in book.title.lower()) or (author and author.lower() in book.author.lower()):
                results.append(book)
        return results

    def search_books_button(self):
        """Prompt the user for a title to search and display the results."""
        title = simpledialog.askstring("جستجوی کتاب", "عنوان کتاب را وارد کنید:")
        if title:
            results = self.search_books(title=title)
            if results:
                result_str = "\n".join(str(book) for book in results)
                messagebox.showinfo("نتایج جستجو", result_str)
            else:
                messagebox.showinfo("نتایج جستجو", "کتابی با این عنوان پیدا نشد.")

    def edit_book(self):
        selected_item = self.table.selection()
        if selected_item:
            title = self.table.item(selected_item, "values")[0]
            book = self.search_books(title=title)
            if book:
                # Prompt for new details, pre-filling with the existing values
                new_title = simpledialog.askstring("ویرایش کتاب", f"عنوان جدید را برای {book[0].title} وارد کنید:", initialvalue=book[0].title)
                new_author = simpledialog.askstring("ویرایش کتاب", f"نویسنده جدید را برای {book[0].author} وارد کنید:", initialvalue=book[0].author)
                try:
                    new_price = float(simpledialog.askstring("ویرایش کتاب", f"قیمت جدید را برای {book[0].title} وارد کنید:", initialvalue=str(book[0].price)))
                    new_stock = int(simpledialog.askstring("ویرایش کتاب", f"موجودی جدید را برای {book[0].title} وارد کنید:", initialvalue=str(book[0].stock)))
                    
                    # Update the book details
                    book[0].title = new_title
                    book[0].author = new_author
                    book[0].price = new_price
                    book[0].stock = new_stock

                    # Refresh the table
                    self.load_books()
                except ValueError:
                    messagebox.showwarning("ورودی نامعتبر", "لطفا مقادیر معتبر برای قیمت و موجودی وارد کنید.")

    def delete_book(self):
        selected_item = self.table.selection()
        if selected_item:
            title = self.table.item(selected_item, "values")[0]
            book = self.search_books(title=title)
            if book:
                self.books.remove(book[0])
                self.load_books()

    def next_page(self):
        if (self.current_page + 1) * self.items_per_page < len(self.books):
            self.current_page += 1
            self.load_books()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_books()


# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = BookstoreGUI(root)
    root.mainloop()
