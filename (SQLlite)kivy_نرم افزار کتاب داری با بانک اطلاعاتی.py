import sqlite3
import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.numberinput import Spinner
from kivy.uix.floatlayout import FloatLayout

kivy.require('2.1.0')  # make sure the kivy version is 2.1.0 or newer

# Database Helper Class
class Database:
    def __init__(self):
        self.connection = sqlite3.connect("bookstore.db")
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        # Create table for books and sales if they do not exist
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
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                quantity INTEGER,
                total_price REAL,
                FOREIGN KEY(book_id) REFERENCES books(id)
            )
        ''')
        self.connection.commit()

    def insert_book(self, title, author, price, stock):
        self.cursor.execute('''
            INSERT INTO books (title, author, price, stock)
            VALUES (?, ?, ?, ?)
        ''', (title, author, price, stock))
        self.connection.commit()

    def get_books(self, start, limit):
        self.cursor.execute('''
            SELECT * FROM books LIMIT ? OFFSET ?
        ''', (limit, start))
        return self.cursor.fetchall()

    def update_book(self, book_id, title, author, price, stock, discount):
        self.cursor.execute('''
            UPDATE books SET title=?, author=?, price=?, stock=?, discount=? WHERE id=?
        ''', (title, author, price, stock, discount, book_id))
        self.connection.commit()

    def delete_book(self, book_id):
        self.cursor.execute('''
            DELETE FROM books WHERE id=?
        ''', (book_id,))
        self.connection.commit()

    def get_book_by_title(self, title):
        self.cursor.execute('''
            SELECT * FROM books WHERE title LIKE ?
        ''', ('%' + title + '%',))
        return self.cursor.fetchall()

    def record_sale(self, book_id, quantity, total_price):
        self.cursor.execute('''
            INSERT INTO sales (book_id, quantity, total_price)
            VALUES (?, ?, ?)
        ''', (book_id, quantity, total_price))
        self.connection.commit()

    def get_sales_report(self):
        self.cursor.execute('''
            SELECT SUM(quantity), SUM(total_price) FROM sales
        ''')
        return self.cursor.fetchone()

    def close(self):
        self.connection.close()


# Main Kivy Application Class
class BookstoreApp(App):
    def build(self):
        self.db = Database()
        self.items_per_page = 5
        self.current_page = 0

        # Layout for the UI
        self.layout = BoxLayout(orientation="vertical")
        self.scroll_view = ScrollView()
        self.grid_layout = GridLayout(cols=1, size_hint_y=None)
        self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))

        self.load_books()

        self.scroll_view.add_widget(self.grid_layout)
        self.layout.add_widget(self.scroll_view)

        # Adding buttons
        self.add_book_button = Button(text="اضافه کردن کتاب", on_press=self.add_book)
        self.layout.add_widget(self.add_book_button)

        self.sell_button = Button(text="فروش کتاب", on_press=self.sell_book)
        self.layout.add_widget(self.sell_button)

        self.search_button = Button(text="جستجوی کتاب", on_press=self.search_books)
        self.layout.add_widget(self.search_button)

        return self.layout

    def load_books(self):
        """Load books from the database and display them"""
        self.grid_layout.clear_widgets()
        start = self.current_page * self.items_per_page
        books_data = self.db.get_books(start, self.items_per_page)
        for book_data in books_data:
            book_info = f"عنوان: {book_data[1]}, نویسنده: {book_data[2]}, قیمت: {book_data[3]}, موجودی: {book_data[4]}"
            book_label = Label(text=book_info)
            self.grid_layout.add_widget(book_label)

    def add_book(self, instance):
        # Open a popup to add a book
        self.popup_layout = FloatLayout()
        self.title_input = TextInput(hint_text="عنوان کتاب", size_hint=(0.8, None), height=30, pos_hint={'x': 0.1, 'top': 0.9})
        self.author_input = TextInput(hint_text="نویسنده کتاب", size_hint=(0.8, None), height=30, pos_hint={'x': 0.1, 'top': 0.8})
        self.price_input = TextInput(hint_text="قیمت کتاب", size_hint=(0.8, None), height=30, pos_hint={'x': 0.1, 'top': 0.7})
        self.stock_input = TextInput(hint_text="تعداد موجودی", size_hint=(0.8, None), height=30, pos_hint={'x': 0.1, 'top': 0.6})

        self.add_button = Button(text="اضافه کردن", size_hint=(0.8, None), height=40, pos_hint={'x': 0.1, 'top': 0.4})
        self.add_button.bind(on_press=self.insert_new_book)

        self.popup_layout.add_widget(self.title_input)
        self.popup_layout.add_widget(self.author_input)
        self.popup_layout.add_widget(self.price_input)
        self.popup_layout.add_widget(self.stock_input)
        self.popup_layout.add_widget(self.add_button)

        self.popup = Popup(title="افزودن کتاب", content=self.popup_layout, size_hint=(0.6, 0.6))
        self.popup.open()

    def insert_new_book(self, instance):
        title = self.title_input.text
        author = self.author_input.text
        try:
            price = float(self.price_input.text)
            stock = int(self.stock_input.text)
            if title and author:
                self.db.insert_book(title, author, price, stock)
                self.popup.dismiss()
                self.load_books()
            else:
                self.show_popup_message("ورودی نامعتبر", "لطفا تمامی فیلدها را پر کنید.")
        except ValueError:
            self.show_popup_message("ورودی نامعتبر", "لطفا قیمت و موجودی را به درستی وارد کنید.")

    def sell_book(self, instance):
        # Simulate selling a book (we can improve it with specific UI)
        self.show_popup_message("فروش کتاب", "کتاب با موفقیت فروخته شد.")

    def search_books(self, instance):
        # Popup for searching books
        self.search_popup_layout = FloatLayout()
        self.search_input = TextInput(hint_text="عنوان کتاب برای جستجو", size_hint=(0.8, None), height=30, pos_hint={'x': 0.1, 'top': 0.9})

        self.search_button = Button(text="جستجو", size_hint=(0.8, None), height=40, pos_hint={'x': 0.1, 'top': 0.7})
        self.search_button.bind(on_press=self.search_books_in_db)

        self.search_popup_layout.add_widget(self.search_input)
        self.search_popup_layout.add_widget(self.search_button)

        self.search_popup = Popup(title="جستجوی کتاب", content=self.search_popup_layout, size_hint=(0.6, 0.6))
        self.search_popup.open()

    def search_books_in_db(self, instance):
        title = self.search_input.text
        if title:
            books = self.db.get_book_by_title(title)
            self.grid_layout.clear_widgets()
            for book_data in books:
                book_info = f"عنوان: {book_data[1]}, نویسنده: {book_data[2]}, قیمت: {book_data[3]}, موجودی: {book_data[4]}"
                book_label = Label(text=book_info)
                self.grid_layout.add_widget(book_label)
            self.search_popup.dismiss()

    def show_popup_message(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=10)
        message_label = Label(text=message)
        close_button = Button(text="بستن", size_hint=(1, 0.2))
        popup_layout.add_widget(message_label)
        popup_layout.add_widget(close_button)

        popup = Popup(title=title, content=popup_layout, size_hint=(0.5, 0.3))
        close_button.bind(on_press=popup.dismiss)
        popup.open()

    def on_stop(self):
        self.db.close()

# Run the application
if __name__ == "__main__":
    BookstoreApp().run()
