from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QTableWidget, QTableWidgetItem, QHBoxLayout, QDialog, QFormLayout, QMessageBox

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


class AddBookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("اضافه کردن کتاب")
        self.setGeometry(200, 200, 400, 300)

        layout = QFormLayout()

        self.title_input = QLineEdit(self)
        self.author_input = QLineEdit(self)
        self.price_input = QLineEdit(self)
        self.stock_input = QLineEdit(self)

        layout.addRow("عنوان کتاب:", self.title_input)
        layout.addRow("نویسنده:", self.author_input)
        layout.addRow("قیمت:", self.price_input)
        layout.addRow("تعداد موجودی:", self.stock_input)

        self.add_button = QPushButton("اضافه کردن", self)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

        self.add_button.clicked.connect(self.add_book)

    def add_book(self):
        title = self.title_input.text()
        author = self.author_input.text()
        try:
            price = float(self.price_input.text())
            stock = int(self.stock_input.text())
            if title and author:
                book = Book(title, author, price, stock)
                self.parent().add_book_to_list(book)
                self.accept()
            else:
                self.show_message("لطفا تمامی فیلدها را پر کنید.")
        except ValueError:
            self.show_message("قیمت و تعداد موجودی باید عددی باشند.")

    def show_message(self, message):
        msg = QLabel(message)
        self.layout().addWidget(msg)


class BookstoreApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("فروشگاه کتاب")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout(self)

        self.books = []  # لیست کتاب‌ها

        # Buttons
        self.add_book_button = QPushButton("اضافه کردن کتاب", self)
        self.search_button = QPushButton("جستجو کردن کتاب", self)
        self.show_books_button = QPushButton("نمایش کتاب‌ها", self)

        self.layout.addWidget(self.add_book_button)
        self.layout.addWidget(self.search_button)
        self.layout.addWidget(self.show_books_button)

        # Table for displaying books
        self.books_table = QTableWidget(self)
        self.books_table.setRowCount(0)
        self.books_table.setColumnCount(5)
        self.books_table.setHorizontalHeaderLabels(["ID", "عنوان", "نویسنده", "قیمت", "موجودی"])
        self.layout.addWidget(self.books_table)

        # Connect buttons to actions
        self.add_book_button.clicked.connect(self.open_add_book_dialog)
        self.search_button.clicked.connect(self.search_books)
        self.show_books_button.clicked.connect(self.show_books)

    def add_book_to_list(self, book):
        """کتاب جدید به لیست اضافه می‌شود"""
        self.books.append(book)
        self.show_books()

    def open_add_book_dialog(self):
        dialog = AddBookDialog(self)
        dialog.exec_()

    def show_books(self):
        self.books_table.setRowCount(len(self.books))
        for row, book in enumerate(self.books):
            self.books_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))  # ID
            self.books_table.setItem(row, 1, QTableWidgetItem(book.title))
            self.books_table.setItem(row, 2, QTableWidgetItem(book.author))
            self.books_table.setItem(row, 3, QTableWidgetItem(str(book.price)))
            self.books_table.setItem(row, 4, QTableWidgetItem(str(book.stock)))

    def search_books(self):
        title = self.search_input.text()
        results = [book for book in self.books if title.lower() in book.title.lower()]
        self.books_table.setRowCount(len(results))
        for row, book in enumerate(results):
            self.books_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))  # ID
            self.books_table.setItem(row, 1, QTableWidgetItem(book.title))
            self.books_table.setItem(row, 2, QTableWidgetItem(book.author))
            self.books_table.setItem(row, 3, QTableWidgetItem(str(book.price)))
            self.books_table.setItem(row, 4, QTableWidgetItem(str(book.stock)))


if __name__ == "__main__":
    app = QApplication([])
    window = BookstoreApp()
    window.show()
    app.exec_()
