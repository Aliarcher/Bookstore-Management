import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.table import Table
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.uix.gridlayout import GridLayout

kivy.require('2.0.0')

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

class BookstoreGUI(App):
    def build(self):
        self.books = []
        self.tracker = SalesTracker()

        self.layout = BoxLayout(orientation='vertical')

        self.table_layout = GridLayout(cols=5, size_hint_y=None, height=400)
        self.table_layout.bind(minimum_height=self.table_layout.setter('height'))

        self.load_books()

        self.layout.add_widget(self.table_layout)

        self.form_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)

        self.title_input = TextInput(hint_text="عنوان")
        self.author_input = TextInput(hint_text="نویسنده")
        self.price_input = TextInput(hint_text="قیمت", input_filter='float')
        self.stock_input = TextInput(hint_text="تعداد موجود", input_filter='int')

        self.form_layout.add_widget(self.title_input)
        self.form_layout.add_widget(self.author_input)
        self.form_layout.add_widget(self.price_input)
        self.form_layout.add_widget(self.stock_input)

        self.add_book_button = Button(text="اضافه کردن کتاب")
        self.add_book_button.bind(on_press=self.add_book)
        self.form_layout.add_widget(self.add_book_button)

        self.layout.add_widget(self.form_layout)

        self.control_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)

        self.sell_button = Button(text="فروش کتاب")
        self.sell_button.bind(on_press=self.sell_book)
        self.control_layout.add_widget(self.sell_button)

        self.search_button = Button(text="جستجوی کتاب")
        self.search_button.bind(on_press=self.search_books_button)
        self.control_layout.add_widget(self.search_button)

        self.report_button = Button(text="گزارش فروش")
        self.report_button.bind(on_press=self.show_sales_report)
        self.control_layout.add_widget(self.report_button)

        self.discount_button = Button(text="اعمال تخفیف")
        self.discount_button.bind(on_press=self.apply_discount)
        self.control_layout.add_widget(self.discount_button)

        self.layout.add_widget(self.control_layout)

        return self.layout

    def load_books(self):
        for book in self.books:
            self.table_layout.add_widget(Label(text=book.title))
            self.table_layout.add_widget(Label(text=book.author))
            self.table_layout.add_widget(Label(text=str(book.price)))
            self.table_layout.add_widget(Label(text=str(book.stock)))
            self.table_layout.add_widget(Label(text=str(book.get_discounted_price())))

    def add_book(self, instance):
        title = self.title_input.text
        author = self.author_input.text
        try:
            price = float(self.price_input.text)
            stock = int(self.stock_input.text)
            if title and author:
                book = Book(title, author, price, stock)
                self.books.append(book)
                self.title_input.text = ""
                self.author_input.text = ""
                self.price_input.text = ""
                self.stock_input.text = ""
                self.load_books()
            else:
                self.show_popup("ورودی نامعتبر", "لطفا عنوان و نویسنده را وارد کنید.")
        except ValueError:
            self.show_popup("ورودی نامعتبر", "قیمت یا موجودی معتبر وارد کنید.")

    def sell_book(self, instance):
        title = self.show_input_popup("فروش کتاب", "عنوان کتاب برای فروش را وارد کنید:")
        if title:
            book = self.search_books(title=title)
            if book:
                quantity = self.show_input_popup("فروش کتاب", f"تعداد را برای فروش {book[0].title} وارد کنید:")
                if quantity:
                    try:
                        self.tracker.record_sale(book[0], int(quantity))
                        self.load_books()
                    except ValueError as e:
                        self.show_popup("خطا", str(e))
            else:
                self.show_popup("اطلاع", f"کتاب '{title}' پیدا نشد.")

    def apply_discount(self, instance):
        title = self.show_input_popup("اعمال تخفیف", "عنوان کتاب را برای تخفیف وارد کنید:")
        if title:
            book = self.search_books(title=title)
            if book:
                try:
                    discount = float(self.show_input_popup("تخفیف", "درصد تخفیف را وارد کنید:"))
                    book[0].apply_discount(discount)
                    self.load_books()
                except ValueError:
                    self.show_popup("ورودی نامعتبر", "درصد تخفیف معتبر وارد کنید.")

    def show_sales_report(self, instance):
        total_books, total_income = self.tracker.total_sales()
        report = f"کل کتاب‌های فروخته شده: {total_books}\nکل درآمد حاصله: {total_income}"
        self.show_popup("گزارش فروش", report)

    def search_books(self, title=None, author=None):
        """Search for books based on title or author."""
        results = []
        for book in self.books:
            if (title and title.lower() in book.title.lower()) or (author and author.lower() in book.author.lower()):
                results.append(book)
        return results

    def search_books_button(self, instance):
        """Prompt the user for a title to search and display the results."""
        title = self.show_input_popup("جستجوی کتاب", "عنوان کتاب را وارد کنید:")
        if title:
            results = self.search_books(title=title)
            if results:
                result_str = "\n".join(str(book) for book in results)
                self.show_popup("نتایج جستجو", result_str)
            else:
                self.show_popup("نتایج جستجو", "کتابی با این عنوان پیدا نشد.")

    def show_input_popup(self, title, message):
        """Create a simple input popup to get user input."""
        input_popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        input_popup.open()
        return ""

    def show_popup(self, title, message):
        """Create a simple popup."""
        popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()


if __name__ == '__main__':
    BookstoreGUI().run()
