import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry

def create_database():
    conn = sqlite3.connect('jewelry.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, 
                  price REAL,
                  description TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  product_id INTEGER, 
                  quantity INTEGER, 
                  status TEXT,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS addresses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  address TEXT)''')
    conn.commit()
    conn.close()

create_database()

class JewelryStoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ювелирный магазин")
        self.root.geometry("1280x640")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        self.tabs = {
            'Товары': ttk.Frame(self.notebook),
            'Заказы': ttk.Frame(self.notebook),
            'Отчеты': ttk.Frame(self.notebook),
            'Настройки': ttk.Frame(self.notebook)
        }

        for name, tab in self.tabs.items():
            self.notebook.add(tab, text=name)

        self.init_products_tab()
        self.init_orders_tab()
        self.init_reports_tab()
        self.init_settings_tab()

    def configure_styles(self):
        self.style.configure('TFrame', background='#F8F9FA')
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('TLabel', font=('Arial', 11), background='#F8F9FA')
        self.style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
        self.style.map('TButton',
            foreground=[('active', '!disabled', 'white'), ('!active', 'black')],
            background=[('active', '#0056b3'), ('!active', '#007BFF')]
        )

    def init_products_tab(self):
        frame = ttk.Frame(self.tabs['Товары'])
        frame.pack(padx=20, pady=20, fill='both', expand=True)

        ttk.Label(frame, text="Управление товарами", style='Header.TLabel').pack(pady=10)
        
        self.products_tree = ttk.Treeview(frame, columns=('name', 'price', 'description'), show='headings')
        self.products_tree.heading('name', text='Название')
        self.products_tree.heading('price', text='Цена')
        self.products_tree.heading('description', text='Описание')
        self.products_tree.pack(fill='both', expand=True)

        control_frame = ttk.Frame(frame)
        control_frame.pack(pady=10)
        
        ttk.Label(control_frame, text="Название:").pack(side='left')
        self.product_name = ttk.Entry(control_frame, width=20)
        self.product_name.pack(side='left', padx=5)
        
        ttk.Label(control_frame, text="Цена:").pack(side='left')
        self.product_price = ttk.Entry(control_frame, width=10)
        self.product_price.pack(side='left', padx=5)
        
        ttk.Label(control_frame, text="Описание:").pack(side='left')
        self.product_description = ttk.Entry(control_frame, width=30)
        self.product_description.pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="Добавить", command=self.add_product).pack(side='left', padx=5)
        self.load_products()

    def init_orders_tab(self):
        frame = ttk.Frame(self.tabs['Заказы'])
        frame.pack(padx=20, pady=20, fill='both', expand=True)

        ttk.Label(frame, text="Оформление заказа", style='Header.TLabel').pack(pady=10)
        
        order_frame = ttk.Frame(frame)
        order_frame.pack(fill='x', pady=10)
        
        ttk.Label(order_frame, text="Товар:").pack(side='left')
        self.order_product = ttk.Combobox(order_frame, state="readonly")
        self.order_product.pack(side='left', padx=5)
        
        ttk.Label(order_frame, text="Количество:").pack(side='left')
        self.order_quantity = ttk.Entry(order_frame, width=10)
        self.order_quantity.pack(side='left', padx=5)
        
        ttk.Button(order_frame, text="Оформить заказ", command=self.create_order).pack(side='left', padx=5)
        
        ttk.Label(frame, text="История заказов", style='Header.TLabel').pack(pady=10)
        
        self.orders_tree = ttk.Treeview(frame, columns=('id', 'product', 'quantity', 'status', 'time'), show='headings')
        self.orders_tree.heading('id', text='ID')
        self.orders_tree.heading('product', text='Товар')
        self.orders_tree.heading('quantity', text='Количество')
        self.orders_tree.heading('status', text='Статус')
        self.orders_tree.heading('time', text='Время заказа')
        self.orders_tree.pack(fill='both', expand=True)
        
        self.load_orders()
        self.update_order_products()

    def init_reports_tab(self):
        frame = ttk.Frame(self.tabs['Отчеты'])
        frame.pack(padx=20, pady=20, fill='both', expand=True)

        ttk.Label(frame, text="Финансовые отчеты", style='Header.TLabel').pack(pady=10)
        
        date_frame = ttk.Frame(frame)
        date_frame.pack(pady=10)
        
        ttk.Label(date_frame, text="С:").pack(side='left')
        self.start_date = DateEntry(date_frame)
        self.start_date.pack(side='left', padx=5)
        
        ttk.Label(date_frame, text="По:").pack(side='left', padx=5)
        self.end_date = DateEntry(date_frame)
        self.end_date.pack(side='left', padx=5)
        
        ttk.Button(frame, text="Сгенерировать отчет", command=self.generate_report).pack(pady=5)
        
        self.report_text = tk.Text(frame, height=10, width=60)
        self.report_text.pack(pady=10)

    def init_settings_tab(self):
        frame = ttk.Frame(self.tabs['Настройки'])
        frame.pack(padx=20, pady=20, fill='both', expand=True)

        ttk.Label(frame, text="Управление адресами", style='Header.TLabel').pack(pady=10)
        
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill='x', pady=5)
        
        ttk.Label(input_frame, text="Адрес:").pack(side='left')
        self.address_entry = ttk.Entry(input_frame, width=40)
        self.address_entry.pack(side='left', padx=5)
        ttk.Button(input_frame, text="Добавить адрес", command=self.add_address).pack(side='left', padx=5)
        
        self.addresses_tree = ttk.Treeview(frame, columns=('address'), show='headings')
        self.addresses_tree.heading('address', text='Адрес')
        self.addresses_tree.pack(fill='both', expand=True, pady=10)
        
        ttk.Button(frame, text="Удалить выбранный адрес", command=self.delete_address).pack(pady=5)
        
        self.load_addresses()

    def load_products(self):
        for i in self.products_tree.get_children():
            self.products_tree.delete(i)
        conn = sqlite3.connect('jewelry.db')
        c = conn.cursor()
        c.execute("SELECT * FROM products")
        for row in c.fetchall():
            self.products_tree.insert('', 'end', values=(row[1], f"{row[2]} руб.", row[3]))
        conn.close()

    def add_product(self):
        name = self.product_name.get()
        price = self.product_price.get()
        description = self.product_description.get()
        if name and price:
            try:
                conn = sqlite3.connect('jewelry.db')
                c = conn.cursor()
                c.execute("INSERT INTO products (name, price, description) VALUES (?, ?, ?)", 
                         (name, float(price), description))
                conn.commit()
                self.load_products()
                self.product_name.delete(0, 'end')
                self.product_price.delete(0, 'end')
                self.product_description.delete(0, 'end')
                self.update_order_products()
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат цены")
            finally:
                conn.close()
        else:
            messagebox.showwarning("Ошибка", "Заполните все поля")

    def update_order_products(self):
        conn = sqlite3.connect('jewelry.db')
        c = conn.cursor()
        c.execute("SELECT name FROM products")
        products = [row[0] for row in c.fetchall()]
        self.order_product['values'] = products
        if products:
            self.order_product.current(0)
        conn.close()

    def create_order(self):
        product_name = self.order_product.get()
        quantity = self.order_quantity.get()
        if product_name and quantity:
            try:
                quantity = int(quantity)
                conn = sqlite3.connect('jewelry.db')
                c = conn.cursor()
                c.execute("SELECT id FROM products WHERE name = ?", (product_name,))
                product_id = c.fetchone()[0]
                c.execute("INSERT INTO orders (product_id, quantity, status) VALUES (?, ?, 'Новый')", 
                         (product_id, quantity))
                conn.commit()
                conn.close()
                self.load_orders()
                self.order_quantity.delete(0, 'end')
                messagebox.showinfo("Успех", "Заказ оформлен")
            except ValueError:
                messagebox.showerror("Ошибка", "Неверное количество")
        else:
            messagebox.showwarning("Ошибка", "Заполните все поля")

    def load_orders(self):
        for i in self.orders_tree.get_children():
            self.orders_tree.delete(i)
        conn = sqlite3.connect('jewelry.db')
        c = conn.cursor()
        c.execute('''SELECT orders.id, products.name, orders.quantity, orders.status, 
                    strftime('%d.%m.%Y %H:%M', orders.created_at)
                 FROM orders 
                 JOIN products ON orders.product_id = products.id''')
        for row in c.fetchall():
            self.orders_tree.insert('', 'end', values=row)
        conn.close()

    def generate_report(self):
        start = self.start_date.get_date()
        end = self.end_date.get_date()
        
        conn = sqlite3.connect('jewelry.db')
        c = conn.cursor()
        
        c.execute('''SELECT COUNT(*) FROM orders 
                  WHERE date(created_at) BETWEEN ? AND ?''',
                  (start, end))
        total_orders = c.fetchone()[0]
        
        c.execute('''SELECT SUM(products.price * orders.quantity) 
                  FROM orders 
                  JOIN products ON orders.product_id = products.id 
                  WHERE date(orders.created_at) BETWEEN ? AND ?''',
                  (start, end))
        total_revenue = c.fetchone()[0] or 0
        
        c.execute('''SELECT products.name, SUM(orders.quantity) 
                  FROM orders 
                  JOIN products ON orders.product_id = products.id 
                  WHERE date(orders.created_at) BETWEEN ? AND ?
                  GROUP BY products.name 
                  ORDER BY 2 DESC LIMIT 3''',
                  (start, end))
        popular_items = c.fetchall()
        
        report = f"Отчет за период с {start} по {end}:\n\n"
        report += f"Всего заказов: {total_orders}\n"
        report += f"Общая выручка: {total_revenue:.2f} руб.\n\n"
        report += "Самые популярные товары:\n"
        for item in popular_items:
            report += f"- {item[0]}: {item[1]} шт.\n"
        
        self.report_text.delete(1.0, 'end')
        self.report_text.insert('end', report)
        conn.close()

    def add_address(self):
        address = self.address_entry.get()
        if address:
            conn = sqlite3.connect('jewelry.db')
            c = conn.cursor()
            c.execute("INSERT INTO addresses (address) VALUES (?)", (address,))
            conn.commit()
            conn.close()
            self.address_entry.delete(0, 'end')
            self.load_addresses()
        else:
            messagebox.showwarning("Ошибка", "Введите адрес")

    def delete_address(self):
        selected = self.addresses_tree.selection()
        if selected:
            item = self.addresses_tree.item(selected[0])
            address = item['values'][0]
            conn = sqlite3.connect('jewelry.db')
            c = conn.cursor()
            c.execute("DELETE FROM addresses WHERE address=?", (address,))
            conn.commit()
            conn.close()
            self.load_addresses()
        else:
            messagebox.showwarning("Ошибка", "Выберите адрес для удаления")

    def load_addresses(self):
        for i in self.addresses_tree.get_children():
            self.addresses_tree.delete(i)
        conn = sqlite3.connect('jewelry.db')
        c = conn.cursor()
        c.execute("SELECT address FROM addresses")
        for row in c.fetchall():
            self.addresses_tree.insert('', 'end', values=row)
        conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = JewelryStoreApp(root)
    root.mainloop()
