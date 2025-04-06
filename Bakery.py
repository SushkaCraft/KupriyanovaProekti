import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry

def create_database():
    conn = sqlite3.connect('bakery.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS menu
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, 
                  price REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  item_id INTEGER, 
                  quantity INTEGER, 
                  status TEXT,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, 
                  address TEXT)''')
    conn.commit()
    conn.close()

create_database()

class BakeryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Пекарня Премиум")
        self.root.geometry("1000x700")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        self.tabs = {
            'Меню': ttk.Frame(self.notebook),
            'Заказы': ttk.Frame(self.notebook),
            'Отчеты': ttk.Frame(self.notebook),
            'Настройки': ttk.Frame(self.notebook)
        }

        for name, tab in self.tabs.items():
            self.notebook.add(tab, text=name)

        self.init_menu_tab()
        self.init_orders_tab()
        self.init_reports_tab()
        self.init_settings_tab()

    def configure_styles(self):
        self.style.configure('TFrame', background='#F5F5F5')
        self.style.configure('TButton', font=('Arial', 10), padding=6, background='#4CAF50', foreground='white')
        self.style.configure('TLabel', font=('Arial', 11), background='#F5F5F5', foreground='#333333')
        self.style.configure('Header.TLabel', font=('Arial', 14, 'bold'), background='#607D8B', foreground='white')
        self.style.configure('Treeview.Heading', font=('Arial', 11, 'bold'), background='#B0BEC5')
        self.style.configure('Treeview', font=('Arial', 11), rowheight=25)
        self.style.map('TButton',
            background=[('active', '#45A049'), ('disabled', '#C8E6C9')],
            foreground=[('disabled', '#757575')]
        )

    def init_menu_tab(self):
        frame = ttk.Frame(self.tabs['Меню'], padding=15)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Управление меню", style='Header.TLabel').pack(fill='x', pady=(0, 15))
        
        self.menu_tree = ttk.Treeview(frame, columns=('name', 'price'), show='headings')
        self.menu_tree.heading('name', text='Название')
        self.menu_tree.heading('price', text='Цена', anchor='center')
        self.menu_tree.column('price', width=120, anchor='center')
        self.menu_tree.pack(fill='both', expand=True)

        control_frame = ttk.Frame(frame)
        control_frame.pack(pady=15)
        
        ttk.Label(control_frame, text="Название:").grid(row=0, column=0, padx=5, sticky='e')
        self.item_name = ttk.Entry(control_frame, width=30)
        self.item_name.grid(row=0, column=1, padx=5)
        
        ttk.Label(control_frame, text="Цена:").grid(row=0, column=2, padx=5, sticky='e')
        self.item_price = ttk.Entry(control_frame, width=15)
        self.item_price.grid(row=0, column=3, padx=5)
        
        ttk.Button(control_frame, text="Добавить", command=self.add_item).grid(row=0, column=4, padx=10)
        self.load_menu()

    def init_orders_tab(self):
        frame = ttk.Frame(self.tabs['Заказы'], padding=15)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Создание заказа", style='Header.TLabel').pack(fill='x', pady=(0, 15))
        
        order_frame = ttk.Frame(frame)
        order_frame.pack(fill='x', pady=10)
        
        ttk.Label(order_frame, text="Товар:").pack(side='left', padx=5)
        self.order_item = ttk.Combobox(order_frame, state="readonly", width=30)
        self.order_item.pack(side='left', padx=5)
        
        ttk.Label(order_frame, text="Количество:").pack(side='left', padx=5)
        self.order_quantity = ttk.Entry(order_frame, width=15)
        self.order_quantity.pack(side='left', padx=5)
        
        ttk.Button(order_frame, text="Создать заказ", command=self.create_order).pack(side='left', padx=10)
        
        ttk.Label(frame, text="История заказов", style='Header.TLabel').pack(fill='x', pady=(20, 10))
        
        self.orders_tree = ttk.Treeview(frame, columns=('id', 'item', 'quantity', 'status', 'time'), show='headings')
        self.orders_tree.heading('id', text='ID')
        self.orders_tree.heading('item', text='Товар')
        self.orders_tree.heading('quantity', text='Количество')
        self.orders_tree.heading('status', text='Статус')
        self.orders_tree.heading('time', text='Время заказа')
        self.orders_tree.column('id', width=50, anchor='center')
        self.orders_tree.column('quantity', width=100, anchor='center')
        self.orders_tree.pack(fill='both', expand=True)
        
        self.load_orders()
        self.update_order_items()

    def init_reports_tab(self):
        frame = ttk.Frame(self.tabs['Отчеты'], padding=15)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Генерация отчетов", style='Header.TLabel').pack(fill='x', pady=(0, 15))
        
        date_frame = ttk.Frame(frame)
        date_frame.pack(pady=10)
        
        ttk.Label(date_frame, text="С:").pack(side='left', padx=5)
        self.start_date = DateEntry(date_frame, width=12)
        self.start_date.pack(side='left', padx=5)
        
        ttk.Label(date_frame, text="По:").pack(side='left', padx=5)
        self.end_date = DateEntry(date_frame, width=12)
        self.end_date.pack(side='left', padx=5)
        
        ttk.Button(frame, text="Сгенерировать отчет", command=self.generate_report).pack(pady=10)
        
        self.report_text = tk.Text(frame, height=12, width=80, font=('Arial', 11), padx=10, pady=10)
        self.report_text.pack(fill='both', expand=True)

    def init_settings_tab(self):
        frame = ttk.Frame(self.tabs['Настройки'], padding=15)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Настройки пекарни", style='Header.TLabel').pack(fill='x', pady=(0, 15))
        
        form_frame = ttk.Frame(frame)
        form_frame.pack(fill='x', pady=10)
        
        ttk.Label(form_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.setting_name = ttk.Entry(form_frame, width=40)
        self.setting_name.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(form_frame, text="Адрес:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.setting_address = ttk.Entry(form_frame, width=40)
        self.setting_address.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        form_frame.columnconfigure(1, weight=1)
        
        ttk.Button(frame, text="Сохранить", command=self.save_settings).pack(pady=10)
        
        ttk.Label(frame, text="Сохраненные настройки", style='Header.TLabel').pack(fill='x', pady=(20, 10))
        
        self.settings_tree = ttk.Treeview(frame, columns=('id', 'name', 'address'), show='headings')
        self.settings_tree.heading('id', text='ID')
        self.settings_tree.heading('name', text='Название')
        self.settings_tree.heading('address', text='Адрес')
        self.settings_tree.column('id', width=50, anchor='center')
        self.settings_tree.pack(fill='both', expand=True)
        
        self.load_settings()

    def load_menu(self):
        for i in self.menu_tree.get_children():
            self.menu_tree.delete(i)
        conn = sqlite3.connect('bakery.db')
        c = conn.cursor()
        c.execute("SELECT * FROM menu")
        for row in c.fetchall():
            self.menu_tree.insert('', 'end', values=(row[1], f"{row[2]} руб."))
        conn.close()

    def add_item(self):
        name = self.item_name.get()
        price = self.item_price.get()
        if name and price:
            try:
                conn = sqlite3.connect('bakery.db')
                c = conn.cursor()
                c.execute("INSERT INTO menu (name, price) VALUES (?, ?)", (name, float(price)))
                conn.commit()
                self.load_menu()
                self.item_name.delete(0, 'end')
                self.item_price.delete(0, 'end')
                self.update_order_items()
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат цены")
            finally:
                conn.close()
        else:
            messagebox.showwarning("Ошибка", "Заполните все поля")

    def update_order_items(self):
        conn = sqlite3.connect('bakery.db')
        c = conn.cursor()
        c.execute("SELECT name FROM menu")
        items = [row[0] for row in c.fetchall()]
        self.order_item['values'] = items
        if items:
            self.order_item.current(0)
        conn.close()

    def create_order(self):
        item_name = self.order_item.get()
        quantity = self.order_quantity.get()
        if item_name and quantity:
            try:
                quantity = int(quantity)
                conn = sqlite3.connect('bakery.db')
                c = conn.cursor()
                c.execute("SELECT id FROM menu WHERE name = ?", (item_name,))
                item_id = c.fetchone()[0]
                c.execute("INSERT INTO orders (item_id, quantity, status) VALUES (?, ?, 'Новый')", 
                         (item_id, quantity))
                conn.commit()
                conn.close()
                self.load_orders()
                self.order_quantity.delete(0, 'end')
                messagebox.showinfo("Успех", "Заказ создан")
            except ValueError:
                messagebox.showerror("Ошибка", "Неверное количество")
        else:
            messagebox.showwarning("Ошибка", "Заполните все поля")

    def load_orders(self):
        for i in self.orders_tree.get_children():
            self.orders_tree.delete(i)
        conn = sqlite3.connect('bakery.db')
        c = conn.cursor()
        c.execute('''SELECT orders.id, menu.name, orders.quantity, orders.status, 
                    strftime('%d.%m.%Y %H:%M', orders.created_at)
                 FROM orders 
                 JOIN menu ON orders.item_id = menu.id''')
        for row in c.fetchall():
            self.orders_tree.insert('', 'end', values=row)
        conn.close()

    def generate_report(self):
        start = self.start_date.get_date()
        end = self.end_date.get_date()
        
        conn = sqlite3.connect('bakery.db')
        c = conn.cursor()
        
        c.execute('''SELECT COUNT(*) FROM orders 
                  WHERE date(created_at) BETWEEN ? AND ?''',
                  (start, end))
        total_orders = c.fetchone()[0]
        
        c.execute('''SELECT SUM(menu.price * orders.quantity) 
                  FROM orders 
                  JOIN menu ON orders.item_id = menu.id 
                  WHERE date(orders.created_at) BETWEEN ? AND ?''',
                  (start, end))
        total_revenue = c.fetchone()[0] or 0
        
        c.execute('''SELECT menu.name, SUM(orders.quantity) 
                  FROM orders 
                  JOIN menu ON orders.item_id = menu.id 
                  WHERE date(orders.created_at) BETWEEN ? AND ?
                  GROUP BY menu.name 
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
        conn = sqlite3.connect('bakery.db')
        c = conn.cursor()
        c.execute("SELECT * FROM settings")
        
        for row in self.settings_tree.get_children():
            self.settings_tree.delete(row)
            
        for settings in c.fetchall():
            self.settings_tree.insert('', 'end', values=settings)
        
        c.execute("SELECT * FROM settings WHERE id = 1")
        settings = c.fetchone()
        if settings:
            self.setting_name.delete(0, 'end')
            self.setting_name.insert(0, settings[1])
            self.setting_address.delete(0, 'end')
            self.setting_address.insert(0, settings[2])
        conn.close()

    def save_settings(self):
        name = self.setting_name.get()
        address = self.setting_address.get()
        if name and address:
            conn = sqlite3.connect('bakery.db')
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
    app = BakeryApp(root)
    root.mainloop()
