import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
from datetime import datetime

class MusicStoreApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Управление музыкальным магазином")
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("TLabel", background="white", foreground="black")
        self.style.configure("TFrame", background="white")
        self.style.configure("TButton", background="gray", foreground="black")
        self.style.configure("Treeview", background="white", foreground="black", fieldbackground="white")
        self.style.map("Treeview", background=[('selected', 'gray')])

        self.create_database()

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(padx=10, pady=10, expand=True, fill='both')

        self.create_products_tab()
        self.create_customers_tab()
        self.create_sales_tab()
        self.create_stats_tab()

    def create_database(self):
        self.conn = sqlite3.connect('music_store.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS products (
                            id INTEGER PRIMARY KEY,
                            name TEXT,
                            price REAL,
                            quantity INTEGER)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS customers (
                            id INTEGER PRIMARY KEY,
                            name TEXT,
                            contact TEXT)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS sales (
                            id INTEGER PRIMARY KEY,
                            product_id INTEGER,
                            customer_id INTEGER,
                            date TEXT,
                            quantity INTEGER,
                            total REAL)''')
        self.conn.commit()

    def create_products_tab(self):
        self.products_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.products_frame, text="Товары")

        ttk.Label(self.products_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5)
        self.product_name = ttk.Entry(self.products_frame)
        self.product_name.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(self.products_frame, text="Цена:").grid(row=1, column=0, padx=5, pady=5)
        self.product_price = ttk.Entry(self.products_frame)
        self.product_price.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(self.products_frame, text="Количество:").grid(row=2, column=0, padx=5, pady=5)
        self.product_quantity = ttk.Entry(self.products_frame)
        self.product_quantity.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        ttk.Button(self.products_frame, text="Добавить", command=self.add_product).grid(row=3, column=0, padx=5, pady=5)
        ttk.Button(self.products_frame, text="Удалить", command=self.delete_product).grid(row=3, column=1, padx=5, pady=5)

        self.products_tree = ttk.Treeview(self.products_frame, columns=('ID', 'Name', 'Price', 'Quantity'), show='headings')
        self.products_tree.heading('ID', text='ID')
        self.products_tree.heading('Name', text='Название')
        self.products_tree.heading('Price', text='Цена')
        self.products_tree.heading('Quantity', text='Количество')
        for col in ('ID', 'Name', 'Price', 'Quantity'):
            self.products_tree.column(col, anchor='center')
        self.products_tree.grid(row=4, column=0, columnspan=2, padx=5, pady=10, sticky='nsew')

        self.products_frame.columnconfigure(1, weight=1)
        self.products_frame.rowconfigure(4, weight=1)

        self.update_products_list()

    def create_customers_tab(self):
        self.customers_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.customers_frame, text="Клиенты")

        ttk.Label(self.customers_frame, text="Имя:").grid(row=0, column=0, padx=5, pady=5)
        self.customer_name = ttk.Entry(self.customers_frame)
        self.customer_name.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(self.customers_frame, text="Контакты:").grid(row=1, column=0, padx=5, pady=5)
        self.customer_contact = ttk.Entry(self.customers_frame)
        self.customer_contact.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        ttk.Button(self.customers_frame, text="Добавить", command=self.add_customer).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(self.customers_frame, text="Удалить", command=self.delete_customer).grid(row=2, column=1, padx=5, pady=5)

        self.customers_tree = ttk.Treeview(self.customers_frame, columns=('ID', 'Name', 'Contact'), show='headings')
        self.customers_tree.heading('ID', text='ID')
        self.customers_tree.heading('Name', text='Имя')
        self.customers_tree.heading('Contact', text='Контакты')
        for col in ('ID', 'Name', 'Contact'):
            self.customers_tree.column(col, anchor='center')
        self.customers_tree.grid(row=3, column=0, columnspan=2, padx=5, pady=10, sticky='nsew')

        self.customers_frame.columnconfigure(1, weight=1)
        self.customers_frame.rowconfigure(3, weight=1)

        self.update_customers_list()

    def create_sales_tab(self):
        self.sales_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sales_frame, text="Продажи")

        ttk.Label(self.sales_frame, text="Товар:").grid(row=0, column=0, padx=5, pady=5)
        self.product_combo = ttk.Combobox(self.sales_frame)
        self.product_combo.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(self.sales_frame, text="Клиент:").grid(row=1, column=0, padx=5, pady=5)
        self.customer_combo = ttk.Combobox(self.sales_frame)
        self.customer_combo.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(self.sales_frame, text="Кол-во:").grid(row=2, column=0, padx=5, pady=5)
        self.sale_quantity = ttk.Entry(self.sales_frame)
        self.sale_quantity.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        ttk.Button(self.sales_frame, text="Оформить продажу", command=self.make_sale).grid(row=3, column=0, columnspan=2, padx=5, pady=10)

        self.sales_tree = ttk.Treeview(self.sales_frame, columns=('ID', 'Product', 'Customer', 'Date', 'Quantity', 'Total'), show='headings')
        self.sales_tree.heading('ID', text='ID')
        self.sales_tree.heading('Product', text='Товар')
        self.sales_tree.heading('Customer', text='Клиент')
        self.sales_tree.heading('Date', text='Дата')
        self.sales_tree.heading('Quantity', text='Количество')
        self.sales_tree.heading('Total', text='Сумма')
        for col in ('ID', 'Product', 'Customer', 'Date', 'Quantity', 'Total'):
            self.sales_tree.column(col, anchor='center')
        self.sales_tree.grid(row=4, column=0, columnspan=2, padx=5, pady=10, sticky='nsew')

        self.sales_frame.columnconfigure(1, weight=1)
        self.sales_frame.rowconfigure(4, weight=1)

        self.update_sales_list()
        self.update_combos()

    def create_stats_tab(self):
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Статистика")

        ttk.Label(self.stats_frame, text="Общая выручка:").grid(row=0, column=0, padx=5, pady=5)
        self.total_revenue = ttk.Label(self.stats_frame, text="0")
        self.total_revenue.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.stats_frame, text="Самый популярный товар:").grid(row=1, column=0, padx=5, pady=5)
        self.popular_product = ttk.Label(self.stats_frame, text="-")
        self.popular_product.grid(row=1, column=1, padx=5, pady=5)

        self.sales_summary_tree = ttk.Treeview(self.stats_frame, columns=('Product', 'Total Sales', 'Revenue'), show='headings')
        self.sales_summary_tree.heading('Product', text='Товар')
        self.sales_summary_tree.heading('Total Sales', text='Кол-во продаж')
        self.sales_summary_tree.heading('Revenue', text='Выручка')
        for col in ('Product', 'Total Sales', 'Revenue'):
            self.sales_summary_tree.column(col, anchor='center')
        self.sales_summary_tree.grid(row=2, column=0, columnspan=2, padx=5, pady=10, sticky='nsew')

        self.stats_frame.rowconfigure(2, weight=1)
        self.stats_frame.columnconfigure(1, weight=1)

        self.update_stats()

    def add_product(self):
        name = self.product_name.get()
        price = self.product_price.get()
        quantity = self.product_quantity.get()
        if name and price and quantity:
            try:
                self.c.execute("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)", (name, float(price), int(quantity)))
                self.conn.commit()
                self.update_products_list()
                self.update_combos()
                self.product_name.delete(0, 'end')
                self.product_price.delete(0, 'end')
                self.product_quantity.delete(0, 'end')
            except:
                pass

    def delete_product(self):
        selected = self.products_tree.selection()
        if selected:
            product_id = self.products_tree.item(selected[0], 'values')[0]
            self.c.execute("DELETE FROM products WHERE id=?", (product_id,))
            self.conn.commit()
            self.update_products_list()
            self.update_combos()

    def update_products_list(self):
        for row in self.products_tree.get_children():
            self.products_tree.delete(row)
        self.c.execute("SELECT * FROM products")
        for row in self.c.fetchall():
            self.products_tree.insert('', 'end', values=row)

    def add_customer(self):
        name = self.customer_name.get()
        contact = self.customer_contact.get()
        if name and contact:
            self.c.execute("INSERT INTO customers (name, contact) VALUES (?, ?)", (name, contact))
            self.conn.commit()
            self.update_customers_list()
            self.update_combos()
            self.customer_name.delete(0, 'end')
            self.customer_contact.delete(0, 'end')

    def delete_customer(self):
        selected = self.customers_tree.selection()
        if selected:
            customer_id = self.customers_tree.item(selected[0], 'values')[0]
            self.c.execute("DELETE FROM customers WHERE id=?", (customer_id,))
            self.conn.commit()
            self.update_customers_list()
            self.update_combos()

    def update_customers_list(self):
        for row in self.customers_tree.get_children():
            self.customers_tree.delete(row)
        self.c.execute("SELECT * FROM customers")
        for row in self.c.fetchall():
            self.customers_tree.insert('', 'end', values=row)

    def make_sale(self):
        product = self.product_combo.get()
        customer = self.customer_combo.get()
        quantity = self.sale_quantity.get()
        if product and customer and quantity:
            try:
                product_id = product.split(':')[0]
                customer_id = customer.split(':')[0]
                quantity = int(quantity)
                self.c.execute("SELECT quantity, price FROM products WHERE id=?", (product_id,))
                stock, price = self.c.fetchone()
                if quantity <= stock:
                    total = quantity * price
                    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.c.execute("INSERT INTO sales (product_id, customer_id, date, quantity, total) VALUES (?, ?, ?, ?, ?)",
                                  (product_id, customer_id, date, quantity, total))
                    self.c.execute("UPDATE products SET quantity = quantity - ? WHERE id=?", (quantity, product_id))
                    self.conn.commit()
                    self.update_sales_list()
                    self.update_products_list()
                    self.update_stats()
                    self.sale_quantity.delete(0, 'end')
            except:
                pass

    def update_sales_list(self):
        for row in self.sales_tree.get_children():
            self.sales_tree.delete(row)
        self.c.execute('''SELECT sales.id, products.name, customers.name, sales.date, sales.quantity, sales.total 
                          FROM sales 
                          JOIN products ON sales.product_id = products.id
                          JOIN customers ON sales.customer_id = customers.id''')
        for row in self.c.fetchall():
            self.sales_tree.insert('', 'end', values=row)

    def update_combos(self):
        self.c.execute("SELECT id, name FROM products")
        self.product_combo['values'] = [f"{r[0]}: {r[1]}" for r in self.c.fetchall()]
        self.c.execute("SELECT id, name FROM customers")
        self.customer_combo['values'] = [f"{r[0]}: {r[1]}" for r in self.c.fetchall()]

    def update_stats(self):
        self.c.execute("SELECT SUM(total) FROM sales")
        total = self.c.fetchone()[0] or 0
        self.total_revenue.config(text=f"{total:.2f} руб.")

        self.c.execute('''SELECT products.name, SUM(sales.quantity) FROM sales 
                          JOIN products ON sales.product_id = products.id 
                          GROUP BY product_id 
                          ORDER BY SUM(sales.quantity) DESC LIMIT 1''')
        result = self.c.fetchone()
        self.popular_product.config(text=f"{result[0]} ({result[1]} шт.)" if result else "-")

        for row in self.sales_summary_tree.get_children():
            self.sales_summary_tree.delete(row)
        self.c.execute('''SELECT products.name, SUM(sales.quantity), SUM(sales.total) FROM sales 
                          JOIN products ON sales.product_id = products.id 
                          GROUP BY product_id ORDER BY SUM(sales.total) DESC''')
        for row in self.c.fetchall():
            self.sales_summary_tree.insert('', 'end', values=row)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x600")
    app = MusicStoreApp(root)
    root.mainloop()
