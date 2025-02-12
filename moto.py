import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime
from tkintermapview import TkinterMapView
from tkcalendar import DateEntry

class MotoSalonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Мотосалон")
        self.root.geometry("1200x800")
        self.root.minsize(1080, 640)
        self.root.configure(bg="#f0f0f0")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.style.configure("TNotebook", background="#f0f0f0", padding=10)
        self.style.configure("TNotebook.Tab", font=('Arial', 12, 'bold'), padding=[10, 5], background="#d9d9d9", foreground="#333333")
        self.style.map("TNotebook.Tab", background=[("selected", "#f0f0f0")], foreground=[("selected", "#000000")])

        self.style.configure("TButton", font=('Arial', 12), padding=8, background="#4CAF50", foreground="white")
        self.style.map("TButton", background=[("active", "#45a049")])

        self.style.configure("TLabel", font=('Arial', 12), background="#f0f0f0", foreground="#333333")
        self.style.configure("TEntry", font=('Arial', 12), padding=5, foreground="#333333", fieldbackground="white")

        self.style.configure("Treeview", font=('Arial', 11), background="white", foreground="#333333", fieldbackground="white")
        self.style.configure("Treeview.Heading", font=('Arial', 12, 'bold'), background="#4CAF50", foreground="white")
        self.style.map("Treeview", background=[("selected", "#45a049")], foreground=[("selected", "white")])

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_tables()
        self.create_clients_tab()
        self.create_motorcycles_tab()
        self.create_sales_tab()
        self.create_map_tab()

    def create_tables(self):
        self.conn = sqlite3.connect("moto_salon.db")
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                reg_date TEXT NOT NULL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS motorcycles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model TEXT NOT NULL,
                year INTEGER NOT NULL,
                price REAL NOT NULL,
                status TEXT NOT NULL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                bike_id INTEGER NOT NULL,
                sale_date TEXT NOT NULL,
                amount REAL NOT NULL,
                FOREIGN KEY(client_id) REFERENCES clients(id),
                FOREIGN KEY(bike_id) REFERENCES motorcycles(id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL
            )
        ''')

    def create_clients_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Клиенты")
        
        frame = ttk.Frame(tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(3, weight=1)  
        
        ttk.Label(frame, text="ФИО:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.client_name_entry = ttk.Entry(frame)
        self.client_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Телефон:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.client_phone_entry = ttk.Entry(frame)
        self.client_phone_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Button(frame, text="Добавить клиента", command=self.add_client).grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")
        
        columns = ("ID", "ФИО", "Телефон", "Дата регистрации")
        self.clients_tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.clients_tree.heading(col, text=col)
            self.clients_tree.column(col, stretch=True)

        self.clients_tree.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.clients_tree.yview)
        self.clients_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=3, column=2, sticky="ns")
        
        ttk.Button(frame, text="Обновить", command=self.update_clients_list).grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")
        self.update_clients_list()

    def create_motorcycles_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Мотоциклы")
        
        frame = ttk.Frame(tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(3, weight=1)  
        
        ttk.Label(frame, text="Модель:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.bike_model_entry = ttk.Entry(frame)
        self.bike_model_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Год выпуска:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.bike_year_entry = ttk.Entry(frame)
        self.bike_year_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Цена:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.bike_price_entry = ttk.Entry(frame)
        self.bike_price_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Статус:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.bike_status_combobox = ttk.Combobox(frame, values=["В наличии", "Продан"])
        self.bike_status_combobox.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Button(frame, text="Добавить мотоцикл", command=self.add_motorcycle).grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")
        
        columns = ("ID", "Модель", "Год", "Цена", "Статус")
        self.bikes_tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.bikes_tree.heading(col, text=col)
            self.bikes_tree.column(col, stretch=True)

        self.bikes_tree.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.bikes_tree.yview)
        self.bikes_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=5, column=2, sticky="ns")
        
        ttk.Button(frame, text="Обновить", command=self.update_bikes_list).grid(row=6, column=0, columnspan=2, pady=5, sticky="ew")
        self.update_bikes_list()

    def create_sales_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Продажи")
        
        frame = ttk.Frame(tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(3, weight=1)  
        
        ttk.Label(frame, text="Клиент (ID):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.sale_client_entry = ttk.Entry(frame)
        self.sale_client_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Мотоцикл (ID):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.sale_bike_entry = ttk.Entry(frame)
        self.sale_bike_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Дата продажи:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.sale_date_entry = DateEntry(frame, date_pattern="yyyy-mm-dd")
        self.sale_date_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Сумма:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.sale_amount_entry = ttk.Entry(frame)
        self.sale_amount_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Button(frame, text="Оформить продажу", command=self.add_sale).grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")
        
        columns = ("ID", "Клиент", "Мотоцикл", "Дата", "Сумма")
        self.sales_tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, stretch=True)
        self.sales_tree.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.sales_tree.yview)
        self.sales_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=5, column=2, sticky="ns")
        
        ttk.Button(frame, text="Обновить", command=self.update_sales_list).grid(row=6, column=0, columnspan=2, pady=5, sticky="ew")
        self.update_sales_list()

    def create_map_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Карта")
        
        frame = ttk.Frame(tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(2, weight=1)  
        
        ttk.Label(frame, text="Название точки:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.location_name_entry = ttk.Entry(frame)
        self.location_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Широта:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.location_lat_entry = ttk.Entry(frame)
        self.location_lat_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Долгота:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.location_lon_entry = ttk.Entry(frame)
        self.location_lon_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Button(frame, text="Добавить точку", command=self.add_location).grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")
        
        self.map_widget = TkinterMapView(frame, width=800, height=500)
        self.map_widget.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.map_widget.set_position(55.7558, 37.6176)
        self.map_widget.set_zoom(10)
        self.update_map_markers()

    def add_client(self):
        self.cursor.execute("INSERT INTO clients (name, phone, reg_date) VALUES (?, ?, ?)",
                          (self.client_name_entry.get(),
                           self.client_phone_entry.get(),
                           datetime.now().strftime("%Y-%m-%d")))
        self.conn.commit()
        self.update_clients_list()

    def update_clients_list(self):
        self.clients_tree.delete(*self.clients_tree.get_children())
        for row in self.cursor.execute("SELECT * FROM clients"):
            self.clients_tree.insert("", tk.END, values=row)

    def add_motorcycle(self):
        self.cursor.execute("INSERT INTO motorcycles (model, year, price, status) VALUES (?, ?, ?, ?)",
                          (self.bike_model_entry.get(),
                           self.bike_year_entry.get(),
                           self.bike_price_entry.get(),
                           self.bike_status_combobox.get()))
        self.conn.commit()
        self.update_bikes_list()

    def update_bikes_list(self):
        self.bikes_tree.delete(*self.bikes_tree.get_children())
        for row in self.cursor.execute("SELECT * FROM motorcycles"):
            self.bikes_tree.insert("", tk.END, values=row)

    def add_sale(self):
        self.cursor.execute("INSERT INTO sales (client_id, bike_id, sale_date, amount) VALUES (?, ?, ?, ?)",
                          (self.sale_client_entry.get(),
                           self.sale_bike_entry.get(),
                           self.sale_date_entry.get_date(),
                           self.sale_amount_entry.get()))
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

    def add_location(self):
        self.cursor.execute("INSERT INTO locations (name, latitude, longitude) VALUES (?, ?, ?)",
                          (self.location_name_entry.get(),
                           self.location_lat_entry.get(),
                           self.location_lon_entry.get()))
        self.conn.commit()
        self.update_map_markers()

    def update_map_markers(self):
        self.map_widget.delete_all_marker()
        for row in self.cursor.execute("SELECT * FROM locations"):
            self.map_widget.set_marker(row[2], row[3], text=row[1])

if __name__ == "__main__":
    root = tk.Tk()
    app = MotoSalonApp(root)
    root.mainloop()