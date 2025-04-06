import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime
from tkcalendar import DateEntry

class ModernMotoSalon:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern MotoSalon")
        self.root.geometry("1280x800")
        self.root.minsize(1024, 600)
        
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.colors = {
            'primary': '#2A3F54',
            'secondary': '#F7F7F7',
            'accent': '#1ABB9C',
            'text': '#333333'
        }
        
        self.style.configure('TNotebook', background=self.colors['secondary'])
        self.style.configure('TNotebook.Tab', 
                           font=('Segoe UI', 11, 'bold'),
                           padding=[15, 5],
                           background=self.colors['primary'],
                           foreground='white')
        self.style.map('TNotebook.Tab', 
                      background=[('selected', self.colors['accent'])])
        
        self.style.configure('TFrame', background=self.colors['secondary'])
        self.style.configure('TLabel', 
                           font=('Segoe UI', 10),
                           background=self.colors['secondary'],
                           foreground=self.colors['text'])
        self.style.configure('TButton', 
                           font=('Segoe UI', 10, 'bold'),
                           background=self.colors['accent'],
                           foreground='white',
                           padding=10)
        self.style.map('TButton', 
                      background=[('active', '#169F85')])
        
        self.style.configure('Treeview', 
                           font=('Segoe UI', 10),
                           rowheight=25,
                           background='white',
                           fieldbackground='white')
        self.style.configure('Treeview.Heading', 
                           font=('Segoe UI', 11, 'bold'),
                           background=self.colors['primary'],
                           foreground='white')
        self.style.map('Treeview', 
                     background=[('selected', self.colors['accent'])])
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_tables()
        self.create_clients_tab()
        self.create_motorcycles_tab()
        self.create_sales_tab()
        self.create_stats_tab()
        
    def create_tables(self):
        self.conn = sqlite3.connect("moto_salon.db")
        self.cursor = self.conn.cursor()
        
        tables = [
            '''CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                reg_date TEXT NOT NULL)''',
            
            '''CREATE TABLE IF NOT EXISTS motorcycles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model TEXT NOT NULL,
                year INTEGER NOT NULL,
                price REAL NOT NULL,
                status TEXT NOT NULL)''',
            
            '''CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                bike_id INTEGER NOT NULL,
                sale_date TEXT NOT NULL,
                amount REAL NOT NULL,
                FOREIGN KEY(client_id) REFERENCES clients(id),
                FOREIGN KEY(bike_id) REFERENCES motorcycles(id))'''
        ]
        
        for table in tables:
            self.cursor.execute(table)
        self.conn.commit()

    def create_input_form(self, parent, fields):
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.X, padx=20, pady=10)
        
        entries = {}
        for i, (field, label) in enumerate(fields.items()):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            entry = ttk.Entry(form_frame)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky='ew')
            entries[field] = entry
        
        if 'status' in fields:
            entries['status'] = ttk.Combobox(form_frame, values=["В наличии", "Продан"])
            entries['status'].grid(row=len(fields)-1, column=1, padx=5, pady=5, sticky='ew')
        
        return entries

    def create_clients_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Клиенты")
        
        fields = {
            'name': 'ФИО:',
            'phone': 'Телефон:'
        }
        self.client_entries = self.create_input_form(tab, fields)
        
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Добавить клиента", command=self.add_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Обновить", command=self.update_clients_list).pack(side=tk.LEFT, padx=5)
        
        columns = ("ID", "ФИО", "Телефон", "Дата регистрации")
        self.clients_tree = ttk.Treeview(tab, columns=columns, show="headings", height=12)
        
        for col in columns:
            self.clients_tree.heading(col, text=col)
            self.clients_tree.column(col, width=120, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.clients_tree.yview)
        self.clients_tree.configure(yscroll=scrollbar.set)
        
        self.clients_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.update_clients_list()

    def create_motorcycles_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Мотоциклы")
        
        fields = {
            'model': 'Модель:',
            'year': 'Год выпуска:',
            'price': 'Цена:',
            'status': 'Статус:'
        }
        self.bike_entries = self.create_input_form(tab, fields)
        
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Добавить мотоцикл", command=self.add_motorcycle).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Обновить", command=self.update_bikes_list).pack(side=tk.LEFT, padx=5)
        
        columns = ("ID", "Модель", "Год", "Цена", "Статус")
        self.bikes_tree = ttk.Treeview(tab, columns=columns, show="headings", height=12)
        
        for col in columns:
            self.bikes_tree.heading(col, text=col)
            self.bikes_tree.column(col, width=120, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.bikes_tree.yview)
        self.bikes_tree.configure(yscroll=scrollbar.set)
        
        self.bikes_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.update_bikes_list()

    def create_sales_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Продажи")
        
        form_frame = ttk.Frame(tab)
        form_frame.pack(fill=tk.X, padx=20, pady=10)
        
        fields = [
            ('client_id', 'Клиент (ID):'),
            ('bike_id', 'Мотоцикл (ID):'),
            ('amount', 'Сумма:')
        ]
        
        self.sale_entries = {}
        for i, (field, label) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            entry = ttk.Entry(form_frame)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky='ew')
            self.sale_entries[field] = entry
        
        ttk.Label(form_frame, text="Дата продажи:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.sale_date = DateEntry(form_frame, date_pattern="yyyy-mm-dd")
        self.sale_date.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Оформить продажу", command=self.add_sale).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Обновить", command=self.update_sales_list).pack(side=tk.LEFT, padx=5)
        
        columns = ("ID", "Клиент", "Мотоцикл", "Дата", "Сумма")
        self.sales_tree = ttk.Treeview(tab, columns=columns, show="headings", height=12)
        
        for col in columns:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=120, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.sales_tree.yview)
        self.sales_tree.configure(yscroll=scrollbar.set)
        
        self.sales_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.update_sales_list()

    def create_stats_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Статистика")
        
        stats_frame = ttk.Frame(tab)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        stats = [
            ("Всего клиентов:", "clients"),
            ("Мотоциклов в наличии:", "motorcycles WHERE status='В наличии'"),
            ("Проданных мотоциклов:", "motorcycles WHERE status='Продан'"),
            ("Общая сумма продаж:", "sales")
        ]
        
        self.stats_labels = {}
        for i, (label, query) in enumerate(stats):
            frame = ttk.Frame(stats_frame)
            frame.grid(row=i//2, column=i%2, padx=10, pady=10, sticky='nsew')
            
            ttk.Label(frame, text=label, font=('Segoe UI', 12, 'bold')).pack(pady=5)
            value_label = ttk.Label(frame, text="0", font=('Segoe UI', 14))
            value_label.pack()
            self.stats_labels[query] = value_label
        
        self.update_stats()

    def update_stats(self):
        queries = {
            "clients": "SELECT COUNT(*) FROM clients",
            "motorcycles WHERE status='В наличии'": "SELECT COUNT(*) FROM motorcycles WHERE status='В наличии'",
            "motorcycles WHERE status='Продан'": "SELECT COUNT(*) FROM motorcycles WHERE status='Продан'",
            "sales": "SELECT SUM(amount) FROM sales"
        }
        
        for query, label in self.stats_labels.items():
            self.cursor.execute(queries[query])
            result = self.cursor.fetchone()[0] or 0
            label.config(text=f"{result:,.2f}" if query == "sales" else result)
        
        self.root.after(5000, self.update_stats)

    def add_client(self):
        self.cursor.execute("INSERT INTO clients (name, phone, reg_date) VALUES (?, ?, ?)",
                          (self.client_entries['name'].get(),
                           self.client_entries['phone'].get(),
                           datetime.now().strftime("%Y-%m-%d")))
        self.conn.commit()
        self.update_clients_list()

    def update_clients_list(self):
        self.clients_tree.delete(*self.clients_tree.get_children())
        for row in self.cursor.execute("SELECT * FROM clients"):
            self.clients_tree.insert("", tk.END, values=row)

    def add_motorcycle(self):
        self.cursor.execute("INSERT INTO motorcycles (model, year, price, status) VALUES (?, ?, ?, ?)",
                          (self.bike_entries['model'].get(),
                           self.bike_entries['year'].get(),
                           self.bike_entries['price'].get(),
                           self.bike_entries['status'].get()))
        self.conn.commit()
        self.update_bikes_list()

    def update_bikes_list(self):
        self.bikes_tree.delete(*self.bikes_tree.get_children())
        for row in self.cursor.execute("SELECT * FROM motorcycles"):
            self.bikes_tree.insert("", tk.END, values=row)

    def add_sale(self):
        self.cursor.execute("INSERT INTO sales (client_id, bike_id, sale_date, amount) VALUES (?, ?, ?, ?)",
                          (self.sale_entries['client_id'].get(),
                           self.sale_entries['bike_id'].get(),
                           self.sale_date.get_date(),
                           self.sale_entries['amount'].get()))
        self.conn.commit()
        self.update_sales_list()

    def update_sales_list(self):
        self.sales_tree.delete(*self.sales_tree.get_children())
        query = '''SELECT sales.id, clients.name, motorcycles.model, sales.sale_date, sales.amount 
                   FROM sales 
                   JOIN clients ON sales.client_id = clients.id
                   JOIN motorcycles ON sales.bike_id = motorcycles.id'''
        for row in self.cursor.execute(query):
            self.sales_tree.insert("", tk.END, values=row)

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernMotoSalon(root)
    root.mainloop()
