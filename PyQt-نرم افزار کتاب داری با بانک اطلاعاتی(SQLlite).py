import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QTableWidget, QTableWidgetItem, QHBoxLayout, QDialog, QFormLayout

# Database Helper Class
class Database:
    def __init__(self):
        self.connection = sqlite3.connect("bookstore.db")
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        # Create books table if not exists
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL,
                sold INTEGER DEFAULT 0,
                discount REAL DEFAULT 0
            )
        ''')
        self.connection.commit()

    def insert_book(self, title, author, price, stock):
        self.cursor.execute('''
            INSERT INTO books (title, author, price, stock)
            VALUES (?, ?, ?, ?)
        ''', (title, author, price, stock))
        self.connection.commit()

    def get_books(self):
        self.cursor.execute('SELECT * FROM books')
        return self.cursor.fetchall()

    def get_book_by_title(self, title):
        self.cursor.execute('''
            SELECT * FROM books WHERE title LIKE ?
        ''', ('%' + title + '%',))
        return self.cursor.fetchall()

    def close(self):
        self.connection.close()


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
                db.insert_book(title, author, price, stock)
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

    def open_add_book_dialog(self):
        dialog = AddBookDialog(self)
        dialog.exec_()

    def show_books(self):
        books = db.get_books()
        self.books_table.setRowCount(len(books))
        for row, book in enumerate(books):
            for col, value in enumerate(book):
                self.books_table.setItem(row, col, QTableWidgetItem(str(value)))

    def search_books(self):
        title = self.search_input.text()
        books = db.get_book_by_title(title)
        self.books_table.setRowCount(len(books))
        for row, book in enumerate(books):
            for col, value in enumerate(book):
                self.books_table.setItem(row, col, QTableWidgetItem(str(value)))


if __name__ == "__main__":
    app = QApplication([])
    db = Database()  # Create database connection
    window = BookstoreApp()
    window.show()
    app.exec_()

    db.close()
