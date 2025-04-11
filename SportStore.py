import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry

def create_database():
    conn = sqlite3.connect('sports_store.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, 
                  price REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  product_id INTEGER, 
                  quantity INTEGER, 
                  status TEXT,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, 
                  address TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS clients
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  phone TEXT,
                  email TEXT)''')
    conn.commit()
    conn.close()

create_database()

class SportsStoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Спортивный Магазин")
        self.root.geometry("1000x700")
        self.cart = []
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        self.tabs = {
            'Товары': ttk.Frame(self.notebook),
            'Заказы': ttk.Frame(self.notebook),
            'Клиенты': ttk.Frame(self.notebook),
            'Отчеты': ttk.Frame(self.notebook),
            'Настройки': ttk.Frame(self.notebook)
        }

        for name, tab in self.tabs.items():
            self.notebook.add(tab, text=name)

        self.init_products_tab()
        self.init_orders_tab()
        self.init_clients_tab()
        self.init_reports_tab()
        self.init_settings_tab()

    def configure_styles(self):
        self.style.configure('TFrame', background='#F0F8FF')
        self.style.configure('TButton', font=('Arial', 10), padding=5, borderwidth=1)
        self.style.configure('TLabel', font=('Arial', 11), background='#F0F8FF', foreground='#2F4F4F')
        self.style.configure('Header.TLabel', font=('Arial', 14, 'bold'), foreground='#2F4F4F')
        self.style.configure('Treeview', background='#E6E6FA', fieldbackground='#E6E6FA')
        self.style.map('TButton',
            foreground=[('active', 'white'), ('!active', '#2F4F4F')],
            background=[('active', '#4682B4'), ('!active', '#87CEEB')]
        )

    def init_products_tab(self):
        frame = ttk.Frame(self.tabs['Товары'])
        frame.pack(padx=20, pady=20, fill='both', expand=True)

        ttk.Label(frame, text="Управление товарами", style='Header.TLabel').pack(pady=10)
        
        self.products_tree = ttk.Treeview(frame, columns=('name', 'price'), show='headings')
        self.products_tree.heading('name', text='Название')
        self.products_tree.heading('price', text='Цена')
        self.products_tree.pack(fill='both', expand=True)

        control_frame = ttk.Frame(frame)
        control_frame.pack(pady=10)
        
        ttk.Label(control_frame, text="Название:").pack(side='left')
        self.product_name = ttk.Entry(control_frame, width=20)
        self.product_name.pack(side='left', padx=5)
        
        ttk.Label(control_frame, text="Цена:").pack(side='left')
        self.product_price = ttk.Entry(control_frame, width=10)
        self.product_price.pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="Добавить", command=self.add_product).pack(side='left', padx=5)
        self.load_products()

    def init_orders_tab(self):
        frame = ttk.Frame(self.tabs['Заказы'])
        frame.pack(padx=20, pady=20, fill='both', expand=True)

        ttk.Label(frame, text="Создание заказа", style='Header.TLabel').pack(pady=10)
        
        order_frame = ttk.Frame(frame)
        order_frame.pack(fill='x', pady=10)
        
        ttk.Label(order_frame, text="Товар:").pack(side='left')
        self.order_product = ttk.Combobox(order_frame, state="readonly", width=25)
        self.order_product.pack(side='left', padx=5)
        
        ttk.Label(order_frame, text="Количество:").pack(side='left')
        self.order_quantity = ttk.Entry(order_frame, width=5)
        self.order_quantity.insert(0, '1')
        self.order_quantity.pack(side='left', padx=5)
        
        ttk.Button(order_frame, text="Добавить в корзину", command=self.add_to_cart).pack(side='left', padx=5)
        
        ttk.Label(frame, text="Корзина", style='Header.TLabel').pack(pady=10)
        self.cart_tree = ttk.Treeview(frame, columns=('product', 'quantity'), show='headings', height=4)
        self.cart_tree.heading('product', text='Товар')
        self.cart_tree.heading('quantity', text='Количество')
        self.cart_tree.pack(fill='x')
        
        ttk.Button(frame, text="Оформить заказ", command=self.create_order).pack(pady=10)
        
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

    def init_clients_tab(self):
        frame = ttk.Frame(self.tabs['Клиенты'])
        frame.pack(padx=20, pady=20, fill='both', expand=True)

        ttk.Label(frame, text="Управление клиентами", style='Header.TLabel').pack(pady=10)
        
        self.clients_tree = ttk.Treeview(frame, columns=('name', 'phone', 'email'), show='headings')
        self.clients_tree.heading('name', text='Имя')
        self.clients_tree.heading('phone', text='Телефон')
        self.clients_tree.heading('email', text='Email')
        self.clients_tree.pack(fill='both', expand=True)

        control_frame = ttk.Frame(frame)
        control_frame.pack(pady=10)
        
        ttk.Label(control_frame, text="Имя:").pack(side='left')
        self.client_name = ttk.Entry(control_frame, width=20)
        self.client_name.pack(side='left', padx=5)
        
        ttk.Label(control_frame, text="Телефон:").pack(side='left')
        self.client_phone = ttk.Entry(control_frame, width=15)
        self.client_phone.pack(side='left', padx=5)
        
        ttk.Label(control_frame, text="Email:").pack(side='left')
        self.client_email = ttk.Entry(control_frame, width=20)
        self.client_email.pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="Добавить", command=self.add_client).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Удалить", command=self.delete_client).pack(side='left', padx=5)
        self.load_clients()

    def init_reports_tab(self):
        frame = ttk.Frame(self.tabs['Отчеты'])
        frame.pack(padx=20, pady=20, fill='both', expand=True)

        ttk.Label(frame, text="Генерация отчетов", style='Header.TLabel').pack(pady=10)
        
        date_frame = ttk.Frame(frame)
        date_frame.pack(pady=10)
        
        ttk.Label(date_frame, text="С:").pack(side='left')
        self.start_date = DateEntry(date_frame)
        self.start_date.pack(side='left', padx=5)
        
        ttk.Label(date_frame, text="По:").pack(side='left', padx=5)
        self.end_date = DateEntry(date_frame)
        self.end_date.pack(side='left', padx=5)
        
        ttk.Button(frame, text="Сгенерировать отчет", command=self.generate_report).pack(pady=5)
        
        self.report_text = tk.Text(frame, height=10, width=60, bg='#F5F5F5')
        self.report_text.pack(pady=10)

    def init_settings_tab(self):
        frame = ttk.Frame(self.tabs['Настройки'])
        frame.pack(padx=20, pady=20, fill='both', expand=True)

        ttk.Label(frame, text="Настройки магазина", style='Header.TLabel').pack(pady=10)
        
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill='x')
        
        ttk.Label(input_frame, text="Название:", width=10, anchor='e').grid(row=0, column=0, sticky='e')
        self.setting_name = ttk.Entry(input_frame, width=30)
        self.setting_name.grid(row=0, column=1, padx=5, pady=2, sticky='w')
        
        ttk.Label(input_frame, text="Адрес:", width=10, anchor='e').grid(row=1, column=0, sticky='e')
        self.setting_address = ttk.Entry(input_frame, width=30)
        self.setting_address.grid(row=1, column=1, padx=5, pady=2, sticky='w')
        
        ttk.Button(input_frame, text="Сохранить", command=self.save_settings).grid(row=2, column=1, pady=10, sticky='w')
        
        ttk.Label(frame, text="История настроек", style='Header.TLabel').pack(pady=10)
        self.settings_tree = ttk.Treeview(frame, columns=('id', 'name', 'address'), show='headings')
        self.settings_tree.heading('id', text='ID')
        self.settings_tree.heading('name', text='Название')
        self.settings_tree.heading('address', text='Адрес')
        self.settings_tree.pack(fill='both', expand=True)
        self.load_settings()

    def load_products(self):
        for i in self.products_tree.get_children():
            self.products_tree.delete(i)
        conn = sqlite3.connect('sports_store.db')
        c = conn.cursor()
        c.execute("SELECT * FROM products")
        for row in c.fetchall():
            self.products_tree.insert('', 'end', values=(row[1], f"{row[2]} руб."))
        conn.close()

    def add_product(self):
        name = self.product_name.get()
        price = self.product_price.get()
        if name and price:
            try:
                conn = sqlite3.connect('sports_store.db')
                c = conn.cursor()
                c.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, float(price)))
                conn.commit()
                self.load_products()
                self.product_name.delete(0, 'end')
                self.product_price.delete(0, 'end')
                self.update_order_products()
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат цены")
            finally:
                conn.close()
        else:
            messagebox.showwarning("Ошибка", "Заполните все поля")

    def update_order_products(self):
        conn = sqlite3.connect('sports_store.db')
        c = conn.cursor()
        c.execute("SELECT name FROM products")
        products = [row[0] for row in c.fetchall()]
        self.order_product['values'] = products
        if products:
            self.order_product.current(0)
        conn.close()

    def add_to_cart(self):
        product = self.order_product.get()
        quantity = self.order_quantity.get()
        if product and quantity:
            try:
                quantity = int(quantity)
                self.cart.append((product, quantity))
                self.cart_tree.insert('', 'end', values=(product, quantity))
            except ValueError:
                messagebox.showerror("Ошибка", "Неверное количество")
        else:
            messagebox.showwarning("Ошибка", "Выберите товар и количество")

    def create_order(self):
        if not self.cart:
            messagebox.showwarning("Ошибка", "Корзина пуста")
            return
            
        try:
            conn = sqlite3.connect('sports_store.db')
            c = conn.cursor()
            for item in self.cart:
                product_name, quantity = item
                c.execute("SELECT id FROM products WHERE name = ?", (product_name,))
                product_id = c.fetchone()[0]
                c.execute("INSERT INTO orders (product_id, quantity, status) VALUES (?, ?, 'Новый')", 
                         (product_id, quantity))
            conn.commit()
            conn.close()
            self.cart.clear()
            self.cart_tree.delete(*self.cart_tree.get_children())
            self.load_orders()
            messagebox.showinfo("Успех", "Заказ оформлен")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def load_orders(self):
        for i in self.orders_tree.get_children():
            self.orders_tree.delete(i)
        conn = sqlite3.connect('sports_store.db')
        c = conn.cursor()
        c.execute('''SELECT orders.id, products.name, orders.quantity, orders.status, 
                    strftime('%d.%m.%Y %H:%M', orders.created_at)
                 FROM orders 
                 JOIN products ON orders.product_id = products.id''')
        for row in c.fetchall():
            self.orders_tree.insert('', 'end', values=row)
        conn.close()

    def load_clients(self):
        for i in self.clients_tree.get_children():
            self.clients_tree.delete(i)
        conn = sqlite3.connect('sports_store.db')
        c = conn.cursor()
        c.execute("SELECT name, phone, email FROM clients")
        for row in c.fetchall():
            self.clients_tree.insert('', 'end', values=row)
        conn.close()

    def add_client(self):
        name = self.client_name.get()
        phone = self.client_phone.get()
        email = self.client_email.get()
        if name and phone:
            conn = sqlite3.connect('sports_store.db')
            c = conn.cursor()
            c.execute("INSERT INTO clients (name, phone, email) VALUES (?, ?, ?)",
                     (name, phone, email))
            conn.commit()
            conn.close()
            self.load_clients()
            self.client_name.delete(0, 'end')
            self.client_phone.delete(0, 'end')
            self.client_email.delete(0, 'end')
        else:
            messagebox.showwarning("Ошибка", "Заполните обязательные поля")

    def delete_client(self):
        selected = self.clients_tree.selection()
        if selected:
            item = self.clients_tree.item(selected[0])
            name = item['values'][0]
            conn = sqlite3.connect('sports_store.db')
            c = conn.cursor()
            c.execute("DELETE FROM clients WHERE name = ?", (name,))
            conn.commit()
            conn.close()
            self.load_clients()

    def generate_report(self):
        start = self.start_date.get_date()
        end = self.end_date.get_date()
        
        conn = sqlite3.connect('sports_store.db')
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

    def load_settings(self):
        for i in self.settings_tree.get_children():
            self.settings_tree.delete(i)
        conn = sqlite3.connect('sports_store.db')
        c = conn.cursor()
        c.execute("SELECT * FROM settings")
        for row in c.fetchall():
            self.settings_tree.insert('', 'end', values=row)
            self.setting_name.delete(0, 'end')
            self.setting_name.insert(0, row[1])
            self.setting_address.delete(0, 'end')
            self.setting_address.insert(0, row[2])
        conn.close()

    def save_settings(self):
        name = self.setting_name.get()
        address = self.setting_address.get()
        if name and address:
            conn = sqlite3.connect('sports_store.db')
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO settings (id, name, address) VALUES (1, ?, ?)", 
                     (name, address))
            conn.commit()
            conn.close()
            self.load_settings()
            messagebox.showinfo("Успех", "Настройки сохранены")
        else:
            messagebox.showwarning("Ошибка", "Заполните все поля")

if __name__ == "__main__":
    root = tk.Tk()
    app = SportsStoreApp(root)
    root.mainloop()
