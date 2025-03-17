import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime
from tkintermapview import TkinterMapView
from tkcalendar import DateEntry

class AutoSalonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Автосалон")
        self.root.geometry("1200x800")
        self.root.minsize(1080, 640)
        self.root.configure(bg="#f0f0f0")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.style.configure("TNotebook", background="#2c3e50", padding=0)
        self.style.configure("TNotebook.Tab", font=('Arial', 12, 'bold'), padding=[15, 5], 
                           background="#34495e", foreground="white")
        self.style.map("TNotebook.Tab", background=[("selected", "#2c3e50")], 
                     foreground=[("selected", "white")])

        self.style.configure("TButton", font=('Arial', 12), padding=8, 
                           background="#3498db", foreground="white")
        self.style.map("TButton", background=[("active", "#2980b9")])

        self.style.configure("TLabel", font=('Arial', 12), background="#ecf0f1", 
                           foreground="#2c3e50")
        self.style.configure("TEntry", font=('Arial', 12), padding=5, 
                           foreground="#2c3e50", fieldbackground="white")

        self.style.configure("Treeview", font=('Arial', 11), background="white", 
                           foreground="#2c3e50", fieldbackground="white")
        self.style.configure("Treeview.Heading", font=('Arial', 12, 'bold'), 
                           background="#34495e", foreground="white")
        self.style.map("Treeview", background=[("selected", "#3498db")], 
                     foreground=[("selected", "white")])

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.create_tables()
        self.create_clients_tab()
        self.create_cars_tab()
        self.create_sales_tab()
        self.create_map_tab()

    def create_tables(self):
        self.conn = sqlite3.connect("auto_salon.db")
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
            CREATE TABLE IF NOT EXISTS cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                year INTEGER NOT NULL,
                color TEXT NOT NULL,
                engine_type TEXT NOT NULL,
                mileage INTEGER NOT NULL,
                trim_level TEXT NOT NULL,
                price REAL NOT NULL,
                status TEXT NOT NULL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                car_id INTEGER NOT NULL,
                sale_date TEXT NOT NULL,
                amount REAL NOT NULL,
                FOREIGN KEY(client_id) REFERENCES clients(id),
                FOREIGN KEY(car_id) REFERENCES cars(id)
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
        
        main_frame = ttk.Frame(tab, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)

        ttk.Label(input_frame, text="ФИО:").grid(row=0, column=0, padx=5, sticky="w")
        self.client_name_entry = ttk.Entry(input_frame, width=25)
        self.client_name_entry.grid(row=0, column=1, padx=5, sticky="w")

        ttk.Label(input_frame, text="Телефон:").grid(row=0, column=2, padx=5, sticky="w")
        self.client_phone_entry = ttk.Entry(input_frame, width=18)
        self.client_phone_entry.grid(row=0, column=3, padx=5, sticky="w")

        ttk.Button(input_frame, text="Добавить клиента", command=self.add_client, width=15
                  ).grid(row=0, column=4, padx=10)

        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("ID", "ФИО", "Телефон", "Дата регистрации")
        self.clients_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for col in columns:
            self.clients_tree.heading(col, text=col)
            self.clients_tree.column(col, width=150, anchor=tk.W)
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.clients_tree.yview)
        self.clients_tree.configure(yscrollcommand=vsb.set)
        
        self.clients_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.update_clients_list()

    def create_cars_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Автомобили")
        
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        input_frame = ttk.Frame(main_frame, padding=10)
        input_frame.grid(row=0, column=0, sticky="nswe")

        entries = [
            ("Марка:", "car_brand_entry", 0),
            ("Модель:", "car_model_entry", 1),
            ("Год:", "car_year_entry", 2),
            ("Цвет:", "car_color_entry", 3),
            ("Двигатель:", "car_engine_entry", 4),
            ("Пробег:", "car_mileage_entry", 5),
            ("Цена:", "car_price_entry", 6)
        ]

        for i, (label_text, attr, row) in enumerate(entries):
            ttk.Label(input_frame, text=label_text).grid(row=row, column=0, padx=5, pady=2, sticky="w")
            entry = ttk.Entry(input_frame, width=18)
            setattr(self, attr, entry)
            entry.grid(row=row, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(input_frame, text="Комплектация:").grid(row=7, column=0, padx=5, pady=2, sticky="w")
        self.car_trim_combobox = ttk.Combobox(input_frame, values=["Базовая", "Расширенная", "Полная"], width=16)
        self.car_trim_combobox.grid(row=7, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(input_frame, text="Статус:").grid(row=8, column=0, padx=5, pady=2, sticky="w")
        self.car_status_combobox = ttk.Combobox(input_frame, values=["В наличии", "Продан"], width=16)
        self.car_status_combobox.grid(row=8, column=1, padx=5, pady=2, sticky="w")

        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=9, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Добавить", command=self.add_car, width=12
                  ).pack(side=tk.TOP, pady=2)
        ttk.Button(btn_frame, text="Обновить", command=self.update_cars_list, width=12
                  ).pack(side=tk.TOP, pady=2)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_car, width=12
                  ).pack(side=tk.TOP, pady=2)

        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=0, column=1, sticky="nswe")

        columns = ("ID", "Марка", "Модель", "Год", "Цвет", "Двигатель", "Пробег", "Комплектация", "Цена", "Статус")
        self.cars_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for col in columns:
            self.cars_tree.heading(col, text=col)
            self.cars_tree.column(col, width=100, anchor=tk.W, stretch=True)
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.cars_tree.yview)
        self.cars_tree.configure(yscrollcommand=vsb.set)
        
        self.cars_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.update_cars_list()

    def create_sales_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Продажи")
        
        main_frame = ttk.Frame(tab, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)

        ttk.Label(input_frame, text="Клиент:").grid(row=0, column=0, padx=5, sticky="w")
        self.client_combobox = ttk.Combobox(input_frame, width=35)
        self.client_combobox.grid(row=0, column=1, padx=5, sticky="w")

        ttk.Label(input_frame, text="Автомобиль:").grid(row=0, column=2, padx=5, sticky="w")
        self.car_combobox = ttk.Combobox(input_frame, width=35)
        self.car_combobox.grid(row=0, column=3, padx=5, sticky="w")

        ttk.Label(input_frame, text="Дата:").grid(row=1, column=0, padx=5, sticky="w")
        self.sale_date_entry = DateEntry(input_frame, width=12, date_pattern="yyyy-mm-dd")
        self.sale_date_entry.grid(row=1, column=1, padx=5, sticky="w")

        ttk.Label(input_frame, text="Сумма:").grid(row=1, column=2, padx=5, sticky="w")
        self.sale_amount_entry = ttk.Entry(input_frame, width=15)
        self.sale_amount_entry.grid(row=1, column=3, padx=5, sticky="w")

        ttk.Button(input_frame, text="Оформить продажу", command=self.add_sale, width=18
                  ).grid(row=1, column=4, padx=10)

        self.update_comboboxes()

        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("ID", "Клиент", "Автомобиль", "Комплектация", "Дата", "Сумма")
        self.sales_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for col in columns:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=150, anchor=tk.W)
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=vsb.set)
        
        self.sales_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.update_sales_list()

    def create_map_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Карта")
        
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(main_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        input_frame = ttk.Frame(left_frame, padding=10)
        input_frame.pack(fill=tk.X)

        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, padx=5, sticky="w")
        self.location_name_entry = ttk.Entry(input_frame)
        self.location_name_entry.grid(row=0, column=1, padx=5, sticky="ew")

        ttk.Label(input_frame, text="Широта:").grid(row=1, column=0, padx=5, sticky="w")
        self.location_lat_entry = ttk.Entry(input_frame)
        self.location_lat_entry.grid(row=1, column=1, padx=5, sticky="ew")

        ttk.Label(input_frame, text="Долгота:").grid(row=2, column=0, padx=5, sticky="w")
        self.location_lon_entry = ttk.Entry(input_frame)
        self.location_lon_entry.grid(row=2, column=1, padx=5, sticky="ew")

        ttk.Button(input_frame, text="Добавить точку", command=self.add_location
                  ).grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

        table_frame = ttk.Frame(left_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("ID", "Название", "Широта", "Долгота")
        self.locations_tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.locations_tree.heading(col, text=col)
            self.locations_tree.column(col, width=70, anchor=tk.W)
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.locations_tree.yview)
        self.locations_tree.configure(yscrollcommand=vsb.set)
        
        self.locations_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.update_locations_list()

        self.map_widget = TkinterMapView(main_frame, width=900, height=800)
        self.map_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
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
        self.update_comboboxes()

    def update_clients_list(self):
        self.clients_tree.delete(*self.clients_tree.get_children())
        for row in self.cursor.execute("SELECT * FROM clients"):
            self.clients_tree.insert("", tk.END, values=row)

    def add_car(self):
        self.cursor.execute('''
            INSERT INTO cars 
            (brand, model, year, color, engine_type, mileage, trim_level, price, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (self.car_brand_entry.get(),
                           self.car_model_entry.get(),
                           self.car_year_entry.get(),
                           self.car_color_entry.get(),
                           self.car_engine_entry.get(),
                           self.car_mileage_entry.get(),
                           self.car_trim_combobox.get(),
                           self.car_price_entry.get(),
                           self.car_status_combobox.get()))
        self.conn.commit()
        self.update_cars_list()
        self.update_comboboxes()

    def delete_car(self):
        selected_item = self.cars_tree.selection()
        if selected_item:
            car_id = self.cars_tree.item(selected_item)['values'][0]
            self.cursor.execute("DELETE FROM cars WHERE id=?", (car_id,))
            self.conn.commit()
            self.update_cars_list()
            self.update_comboboxes()

    def update_cars_list(self):
        self.cars_tree.delete(*self.cars_tree.get_children())
        for row in self.cursor.execute("SELECT * FROM cars"):
            self.cars_tree.insert("", tk.END, values=row)

    def add_sale(self):
        client_id = self.client_combobox.get().split(":")[0]
        car_id = self.car_combobox.get().split(":")[0]
        
        self.cursor.execute("INSERT INTO sales (client_id, car_id, sale_date, amount) VALUES (?, ?, ?, ?)",
                          (client_id,
                           car_id,
                           self.sale_date_entry.get_date(),
                           self.sale_amount_entry.get()))
        self.conn.commit()
        self.update_sales_list()

    def update_sales_list(self):
        self.sales_tree.delete(*self.sales_tree.get_children())
        query = '''SELECT sales.id, clients.name, cars.model, cars.trim_level, sales.sale_date, sales.amount 
                   FROM sales 
                   JOIN clients ON sales.client_id = clients.id
                   JOIN cars ON sales.car_id = cars.id'''
        for row in self.cursor.execute(query):
            self.sales_tree.insert("", tk.END, values=row)

    def update_comboboxes(self):
        clients = [f"{row[0]}: {row[1]}" for row in self.cursor.execute("SELECT id, name FROM clients")]
        self.client_combobox['values'] = clients
        
        cars = [f"{row[0]}: {row[1]} {row[2]} ({row[3]})" 
               for row in self.cursor.execute("SELECT id, brand, model, year FROM cars WHERE status='В наличии'")]
        self.car_combobox['values'] = cars

    def add_location(self):
        try:
            lat = float(self.location_lat_entry.get())
            lon = float(self.location_lon_entry.get())
            self.cursor.execute("INSERT INTO locations (name, latitude, longitude) VALUES (?, ?, ?)",
                              (self.location_name_entry.get(), lat, lon))
            self.conn.commit()
            self.update_map_markers()
            self.update_locations_list()
        except ValueError:
            print("Ошибка: Широта и долгота должны быть числами")

    def update_locations_list(self):
        self.locations_tree.delete(*self.locations_tree.get_children())
        for row in self.cursor.execute("SELECT * FROM locations"):
            self.locations_tree.insert("", tk.END, values=row)

    def update_map_markers(self):
        self.map_widget.delete_all_marker()
        for row in self.cursor.execute("SELECT * FROM locations"):
            try:
                lat = float(row[2])
                lon = float(row[3])
                self.map_widget.set_marker(lat, lon, text=row[1])
            except ValueError:
                print(f"Ошибка координат для точки {row[1]}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoSalonApp(root)
    root.mainloop()
