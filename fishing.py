import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

class FishingShopApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Магазин рыболовных товаров")
        self.geometry("1000x700")
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.configure_style()
        self.create_db()
        self.create_widgets()

    def configure_style(self):
        self.style.configure("TNotebook", background="#f0f0f0")
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TButton", padding=6, font=('Arial', 10))
        self.style.map("TButton", background=[('active', '#ddd')])

    def create_db(self):
        self.conn = sqlite3.connect("shop.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS products 
                            (id INTEGER PRIMARY KEY, 
                             name TEXT, 
                             price REAL, 
                             quantity INTEGER,
                             supplier_id INTEGER)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS customers 
                            (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, email TEXT)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS orders 
                            (id INTEGER PRIMARY KEY, 
                             customer_id INTEGER, 
                             product_id INTEGER, 
                             quantity INTEGER, 
                             date TEXT)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS suppliers 
                            (id INTEGER PRIMARY KEY, 
                             name TEXT, 
                             contact TEXT)""")
        self.conn.commit()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        
        self.tab_products = ttk.Frame(self.notebook)
        self.tab_customers = ttk.Frame(self.notebook)
        self.tab_orders = ttk.Frame(self.notebook)
        self.tab_suppliers = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_products, text="Товары")
        self.notebook.add(self.tab_customers, text="Клиенты")
        self.notebook.add(self.tab_orders, text="Заказы")
        self.notebook.add(self.tab_suppliers, text="Поставщики")
        self.notebook.pack(expand=True, fill="both")

        self.create_products_tab()
        self.create_customers_tab()
        self.create_orders_tab()
        self.create_suppliers_tab()

    def create_products_tab(self):
        frame = ttk.Frame(self.tab_products)
        frame.pack(pady=10)

        # Поля ввода для товаров
        ttk.Label(frame, text="Название:").grid(row=0, column=0, padx=5)
        self.product_name = ttk.Entry(frame, width=25)
        self.product_name.grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Цена:").grid(row=0, column=2, padx=5)
        self.product_price = ttk.Entry(frame, width=10)
        self.product_price.grid(row=0, column=3, padx=5)

        ttk.Label(frame, text="Количество:").grid(row=0, column=4, padx=5)
        self.product_quantity = ttk.Entry(frame, width=10)
        self.product_quantity.grid(row=0, column=5, padx=5)

        ttk.Label(frame, text="Поставщик:").grid(row=0, column=6, padx=5)
        self.product_supplier = ttk.Combobox(frame, state="readonly", width=20)
        self.product_supplier.grid(row=0, column=7, padx=5)

        ttk.Button(frame, text="Добавить", command=self.add_product).grid(row=0, column=8, padx=5)
        ttk.Button(frame, text="Удалить", command=self.delete_product).grid(row=0, column=9, padx=5)

        # Таблица товаров
        columns = ("id", "name", "price", "quantity", "supplier")
        self.products_tree = ttk.Treeview(self.tab_products, columns=columns, show="headings")
        self.products_tree.heading("id", text="ID")
        self.products_tree.heading("name", text="Название")
        self.products_tree.heading("price", text="Цена")
        self.products_tree.heading("quantity", text="Количество")
        self.products_tree.heading("supplier", text="Поставщик")
        self.products_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.update_products_tree()
        self.update_suppliers_combobox()

    def add_product(self):
        supplier_name = self.product_supplier.get()
        supplier_id = self.cursor.execute("SELECT id FROM suppliers WHERE name=?", (supplier_name,)).fetchone()
        
        if not supplier_id:
            messagebox.showerror("Ошибка", "Выберите поставщика из списка")
            return
            
        self.cursor.execute("""INSERT INTO products 
                            (name, price, quantity, supplier_id) 
                            VALUES (?, ?, ?, ?)""",
                            (self.product_name.get(), 
                             float(self.product_price.get()), 
                             int(self.product_quantity.get()),
                             supplier_id[0]))
        self.conn.commit()
        self.update_products_tree()

    def delete_product(self):
        selected = self.products_tree.selection()
        if selected:
            self.cursor.execute("DELETE FROM products WHERE id=?", 
                               (self.products_tree.item(selected[0], "values")[0],))
            self.conn.commit()
            self.update_products_tree()

    def update_products_tree(self):
        for row in self.products_tree.get_children():
            self.products_tree.delete(row)
            
        query = """SELECT p.id, p.name, p.price, p.quantity, s.name 
                 FROM products p 
                 LEFT JOIN suppliers s ON p.supplier_id = s.id"""
        for row in self.cursor.execute(query):
            self.products_tree.insert("", "end", values=row)

    def create_suppliers_tab(self):
        frame = ttk.Frame(self.tab_suppliers)
        frame.pack(pady=10)

        # Поля ввода для поставщиков
        ttk.Label(frame, text="Название:").grid(row=0, column=0, padx=5)
        self.supplier_name = ttk.Entry(frame, width=25)
        self.supplier_name.grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Контакты:").grid(row=0, column=2, padx=5)
        self.supplier_contact = ttk.Entry(frame, width=30)
        self.supplier_contact.grid(row=0, column=3, padx=5)

        ttk.Button(frame, text="Добавить", command=self.add_supplier).grid(row=0, column=4, padx=5)
        ttk.Button(frame, text="Удалить", command=self.delete_supplier).grid(row=0, column=5, padx=5)

        # Таблица поставщиков
        columns = ("id", "name", "contact")
        self.suppliers_tree = ttk.Treeview(self.tab_suppliers, columns=columns, show="headings")
        self.suppliers_tree.heading("id", text="ID")
        self.suppliers_tree.heading("name", text="Название")
        self.suppliers_tree.heading("contact", text="Контакты")
        self.suppliers_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.update_suppliers_tree()

    def add_supplier(self):
        self.cursor.execute("INSERT INTO suppliers (name, contact) VALUES (?, ?)",
                           (self.supplier_name.get(), self.supplier_contact.get()))
        self.conn.commit()
        self.update_suppliers_tree()
        self.update_suppliers_combobox()

    def delete_supplier(self):
        selected = self.suppliers_tree.selection()
        if selected:
            self.cursor.execute("DELETE FROM suppliers WHERE id=?", 
                               (self.suppliers_tree.item(selected[0], "values")[0],))
            self.conn.commit()
            self.update_suppliers_tree()
            self.update_suppliers_combobox()

    def update_suppliers_tree(self):
        for row in self.suppliers_tree.get_children():
            self.suppliers_tree.delete(row)
        for row in self.cursor.execute("SELECT * FROM suppliers"):
            self.suppliers_tree.insert("", "end", values=row)

    def update_suppliers_combobox(self):
        suppliers = [row[1] for row in self.cursor.execute("SELECT * FROM suppliers")]
        self.product_supplier["values"] = suppliers

    # Остальные методы (для клиентов и заказов) остаются без изменений
    def create_customers_tab(self):
        frame = ttk.Frame(self.tab_customers)
        frame.pack(pady=10)

        ttk.Label(frame, text="Имя:").grid(row=0, column=0, padx=5)
        self.customer_name = ttk.Entry(frame, width=20)
        self.customer_name.grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Телефон:").grid(row=0, column=2, padx=5)
        self.customer_phone = ttk.Entry(frame, width=15)
        self.customer_phone.grid(row=0, column=3, padx=5)

        ttk.Label(frame, text="Email:").grid(row=0, column=4, padx=5)
        self.customer_email = ttk.Entry(frame, width=25)
        self.customer_email.grid(row=0, column=5, padx=5)

        ttk.Button(frame, text="Добавить", command=self.add_customer).grid(row=0, column=6, padx=5)
        ttk.Button(frame, text="Удалить", command=self.delete_customer).grid(row=0, column=7, padx=5)

        columns = ("id", "name", "phone", "email")
        self.customers_tree = ttk.Treeview(self.tab_customers, columns=columns, show="headings")
        self.customers_tree.heading("id", text="ID")
        self.customers_tree.heading("name", text="Имя")
        self.customers_tree.heading("phone", text="Телефон")
        self.customers_tree.heading("email", text="Email")
        self.customers_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.update_customers_tree()

    def add_customer(self):
        self.cursor.execute("INSERT INTO customers (name, phone, email) VALUES (?, ?, ?)",
                           (self.customer_name.get(), self.customer_phone.get(), self.customer_email.get()))
        self.conn.commit()
        self.update_customers_tree()
        self.update_comboboxes()

    def delete_customer(self):
        selected = self.customers_tree.selection()
        if selected:
            self.cursor.execute("DELETE FROM customers WHERE id=?", (self.customers_tree.item(selected[0], "values")[0],))
            self.conn.commit()
            self.update_customers_tree()

    def update_customers_tree(self):
        for row in self.customers_tree.get_children():
            self.customers_tree.delete(row)
        for row in self.cursor.execute("SELECT * FROM customers"):
            self.customers_tree.insert("", "end", values=row)

    def create_orders_tab(self):
        frame = ttk.Frame(self.tab_orders)
        frame.pack(pady=10)

        ttk.Label(frame, text="Клиент:").grid(row=0, column=0, padx=5)
        self.order_customer = ttk.Combobox(frame, state="readonly")
        self.order_customer.grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Товар:").grid(row=0, column=2, padx=5)
        self.order_product = ttk.Combobox(frame, state="readonly")
        self.order_product.grid(row=0, column=3, padx=5)

        ttk.Label(frame, text="Количество:").grid(row=0, column=4, padx=5)
        self.order_quantity = ttk.Entry(frame, width=10)
        self.order_quantity.grid(row=0, column=5, padx=5)

        ttk.Button(frame, text="Создать заказ", command=self.create_order).grid(row=0, column=6, padx=5)
        self.update_comboboxes()

        columns = ("id", "customer", "product", "quantity", "date")
        self.orders_tree = ttk.Treeview(self.tab_orders, columns=columns, show="headings")
        self.orders_tree.heading("id", text="ID")
        self.orders_tree.heading("customer", text="Клиент")
        self.orders_tree.heading("product", text="Товар")
        self.orders_tree.heading("quantity", text="Количество")
        self.orders_tree.heading("date", text="Дата")
        self.orders_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.update_orders_tree()

    def update_comboboxes(self):
        customers = [row[1] for row in self.cursor.execute("SELECT * FROM customers")]
        products = [row[1] for row in self.cursor.execute("SELECT * FROM products")]
        self.order_customer["values"] = customers
        self.order_product["values"] = products

    def create_order(self):
        customer_id = self.cursor.execute("SELECT id FROM customers WHERE name=?", (self.order_customer.get(),)).fetchone()[0]
        product_id = self.cursor.execute("SELECT id FROM products WHERE name=?", (self.order_product.get(),)).fetchone()[0]
        self.cursor.execute("INSERT INTO orders (customer_id, product_id, quantity, date) VALUES (?, ?, ?, datetime('now'))",
                           (customer_id, product_id, int(self.order_quantity.get())))
        self.conn.commit()
        self.update_orders_tree()

    def update_orders_tree(self):
        for row in self.orders_tree.get_children():
            self.orders_tree.delete(row)
        query = """SELECT o.id, c.name, p.name, o.quantity, o.date 
                 FROM orders o 
                 JOIN customers c ON o.customer_id = c.id 
                 JOIN products p ON o.product_id = p.id"""
        for row in self.cursor.execute(query):
            self.orders_tree.insert("", "end", values=row)

if __name__ == "__main__":
    app = FishingShopApp()
    app.mainloop()
