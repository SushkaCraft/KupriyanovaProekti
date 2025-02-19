import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime
from tkintermapview import TkinterMapView

COLORS = {
    "primary": "#6DB8D1",
    "secondary": "#759DAB",
    "background": "#F1F5F9",
    "text": "#6A787C",
    "success": "#404D52",
    "warning": "#1F2E33",
    "danger": "#1F2E33" 
}

class CoffeeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YaCoffee")
        self.root.geometry("960x640")
        self.root.configure(bg=COLORS["background"])
        
        self.style = ttk.Style()
        self.configure_styles()
        
        self.main_container = ttk.Frame(root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.create_tables()
        self.create_employee_tab()
        self.create_order_tab()
        self.create_inventory_tab()
        self.create_report_tab()
        self.create_map_tab()
        self.create_points_tab()

    def configure_styles(self):
        self.style.theme_use("clam")
        
        self.style.configure(".", background=COLORS["background"], foreground=COLORS["text"])
        self.style.configure("TNotebook", background=COLORS["background"])
        self.style.configure("TNotebook.Tab", 
                            font=('Helvetica', 12, 'bold'), 
                            padding=[15, 5],
                            background=COLORS["secondary"],
                            foreground="white")
        self.style.map("TNotebook.Tab", 
                      background=[("selected", COLORS["primary"])],
                      foreground=[("selected", "white")])
        
        self.style.configure("TButton", 
                            font=('Helvetica', 12, 'bold'), 
                            padding=8,
                            borderwidth=2,
                            relief="flat",
                            background=COLORS["primary"],
                            foreground="white")
        self.style.map("TButton", 
                      background=[('active', COLORS["secondary"]), ('disabled', '#D3D3D3')],
                      relief=[('active', 'sunken'), ('!active', 'flat')])
        
        self.style.configure("TLabel", 
                            font=('Helvetica', 12), 
                            background=COLORS["background"],
                            foreground=COLORS["text"])
        self.style.configure("Header.TLabel", 
                            font=('Helvetica', 14, 'bold'), 
                            foreground=COLORS["primary"])
        
        self.style.configure("TEntry",
                            fieldbackground="white",
                            bordercolor=COLORS["primary"],
                            lightcolor=COLORS["primary"],
                            darkcolor=COLORS["primary"])
        
        self.style.configure("Treeview",
                            font=('Helvetica', 11),
                            rowheight=30,
                            borderwidth=1,
                            relief="solid",
                            fieldbackground=COLORS["background"])
        self.style.configure("Treeview.Heading", 
                            font=('Helvetica', 12, 'bold'),
                            background=COLORS["primary"],
                            foreground="white",
                            relief="flat")
        self.style.map("Treeview.Heading", 
                      background=[('active', COLORS["secondary"])])

    def create_tables(self):
        self.conn = sqlite3.connect("YaCoffeeBAZA.db") 
        self.cursor = self.conn.cursor()
        self.cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS employees ( 
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name TEXT NOT NULL, 
                position TEXT NOT NULL, 
                salary REAL NOT NULL 
            ) 
        ''')
        self.cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS orders ( 
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                employee_id INTEGER NOT NULL, 
                order_date TEXT NOT NULL, 
                total_amount REAL NOT NULL, 
                FOREIGN KEY (employee_id) REFERENCES employees (id) 
            ) 
        ''')
        self.cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS inventory ( 
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                item_name TEXT NOT NULL, 
                quantity INTEGER NOT NULL, 
                price REAL NOT NULL 
            ) 
        ''')
        self.cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS points ( 
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name TEXT NOT NULL, 
                latitude REAL NOT NULL, 
                longitude REAL NOT NULL 
            ) 
        ''')

    def create_employee_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Сотрудники')
        
        header_frame = ttk.Frame(tab)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(header_frame, text="Управление сотрудниками", style="Header.TLabel").pack(side=tk.LEFT)
        
        content_frame = ttk.Frame(tab)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        input_frame = ttk.Frame(content_frame)
        input_frame.pack(pady=10, fill=tk.X)
        
        ttk.Label(input_frame, text="Имя сотрудника:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.employee_name_entry = ttk.Entry(input_frame)
        self.employee_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(input_frame, text="Должность:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.employee_position_entry = ttk.Entry(input_frame)
        self.employee_position_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(input_frame, text="Зарплата:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        self.employee_salary_entry = ttk.Entry(input_frame)
        self.employee_salary_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.EW)
        
        btn_frame = ttk.Frame(content_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Добавить сотрудника", command=self.add_employee).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Обновить список", command=self.update_employee_list).pack(side=tk.LEFT, padx=5)
        
        self.employee_tree = ttk.Treeview(content_frame, columns=("ID", "Имя", "Должность", "Зарплата"), show="headings")
        self.employee_tree.heading("ID", text='ID')
        self.employee_tree.heading("Имя", text='Имя')
        self.employee_tree.heading("Должность", text='Должность')
        self.employee_tree.heading("Зарплата", text='Зарплата')
        self.employee_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.update_employee_list()
    
    def create_order_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Заказы")
        
        header_frame = ttk.Frame(tab)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(header_frame, text="Управление заказами", style="Header.TLabel").pack(side=tk.LEFT)
        
        content_frame = ttk.Frame(tab)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        input_frame = ttk.Frame(content_frame)
        input_frame.pack(pady=10, fill=tk.X)
        
        ttk.Label(input_frame, text="ID сотрудника:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.employee_id_entry = ttk.Entry(input_frame)
        self.employee_id_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(input_frame, text="Сумма заказа:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.order_amount_entry = ttk.Entry(input_frame)
        self.order_amount_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
        
        btn_frame = ttk.Frame(content_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Добавить заказ", command=self.add_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Обновить список", command=self.update_orders_list).pack(side=tk.LEFT, padx=5)
        
        self.orders_tree = ttk.Treeview(content_frame, columns=("ID", "Сотрудник", "Дата Заказа", "Сумма"), show="headings")
        self.orders_tree.heading("ID", text="ID")
        self.orders_tree.heading("Сотрудник", text="Сотрудник")
        self.orders_tree.heading("Дата Заказа", text="Дата Заказа")
        self.orders_tree.heading("Сумма", text="Сумма")
        self.orders_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.update_orders_list()

    def create_inventory_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Инвентарь")
        
        header_frame = ttk.Frame(tab)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(header_frame, text="Управление инвентарем", style="Header.TLabel").pack(side=tk.LEFT)
        
        content_frame = ttk.Frame(tab)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        input_frame = ttk.Frame(content_frame)
        input_frame.pack(pady=10, fill=tk.X)
        
        ttk.Label(input_frame, text="Название товара:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.item_name_entry = ttk.Entry(input_frame)
        self.item_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(input_frame, text="Количество:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.item_quantity_entry = ttk.Entry(input_frame)
        self.item_quantity_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(input_frame, text="Цена:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        self.item_price_entry = ttk.Entry(input_frame)
        self.item_price_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.EW)
        
        btn_frame = ttk.Frame(content_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Добавить товар", command=self.add_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Обновить список", command=self.update_inventory_list).pack(side=tk.LEFT, padx=5)
        
        self.inventory_tree = ttk.Treeview(content_frame, columns=("ID", "Название", "Количество", "Цена"), show="headings")
        self.inventory_tree.heading("ID", text="ID")
        self.inventory_tree.heading("Название", text="Название")
        self.inventory_tree.heading("Количество", text="Количество")
        self.inventory_tree.heading("Цена", text="Цена")
        self.inventory_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.update_inventory_list()

    def create_report_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Отчеты")
        
        header_frame = ttk.Frame(tab)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(header_frame, text="Финансовые отчеты", style="Header.TLabel").pack(side=tk.LEFT)
        
        content_frame = ttk.Frame(tab)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.report_label = ttk.Label(content_frame, font=('Helvetica', 12), wraplength=400)
        self.report_label.pack(pady=10)
        
        ttk.Button(content_frame, text="Создать отчет", command=self.generate_report).pack(pady=10)

    def create_map_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Карта")
        
        header_frame = ttk.Frame(tab)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(header_frame, text="Карта кофеен", style="Header.TLabel").pack(side=tk.LEFT)
        
        self.map_widget = TkinterMapView(tab, width=800, height=600, corner_radius=15)
        self.map_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.map_widget.set_position(55.7558, 37.6176)
        self.map_widget.set_zoom(15)
        self.update_map_points()

    def create_points_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Точки")
        
        header_frame = ttk.Frame(tab)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(header_frame, text="Управление точками", style="Header.TLabel").pack(side=tk.LEFT)
        
        content_frame = ttk.Frame(tab)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        input_frame = ttk.Frame(content_frame)
        input_frame.pack(pady=10, fill=tk.X)
        
        ttk.Label(input_frame, text="Название точки:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.point_name_entry = ttk.Entry(input_frame)
        self.point_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(input_frame, text="Широта:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.point_latitude_entry = ttk.Entry(input_frame)
        self.point_latitude_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.EW)
        
        ttk.Label(input_frame, text="Долгота:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        self.point_longitude_entry = ttk.Entry(input_frame)
        self.point_longitude_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.EW)
        
        btn_frame = ttk.Frame(content_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Добавить точку", command=self.add_point).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Обновить список", command=self.update_points_list).pack(side=tk.LEFT, padx=5)
        
        self.points_tree = ttk.Treeview(content_frame, columns=("ID", "Название", "Широта", "Долгота"), show="headings")
        self.points_tree.heading("ID", text="ID")
        self.points_tree.heading("Название", text="Название")
        self.points_tree.heading("Широта", text="Широта")
        self.points_tree.heading("Долгота", text="Долгота")
        self.points_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.update_points_list()

    def add_employee(self):
        name = self.employee_name_entry.get()
        position = self.employee_position_entry.get()
        salary = self.employee_salary_entry.get()
        self.cursor.execute("INSERT INTO employees (name, position, salary) VALUES (?, ?, ?)", (name, position, salary))
        self.conn.commit()
        self.update_employee_list()
        
    def update_employee_list(self):
        for row in self.employee_tree.get_children():
            self.employee_tree.delete(row)
        self.cursor.execute("SELECT * FROM employees")
        employees = self.cursor.fetchall()
        for employee in employees:
            self.employee_tree.insert("", tk.END, values=employee)

    def add_order(self):
        employee_id = self.employee_id_entry.get()
        order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_amount = self.order_amount_entry.get()
        self.cursor.execute("INSERT INTO orders (employee_id, order_date, total_amount) VALUES (?, ?, ?)", (employee_id, order_date, total_amount))
        self.conn.commit()
        self.update_order_list()
        
    def update_orders_list(self):
        for row in self.orders_tree.get_children():
            self.orders_tree.delete(row)
        self.cursor.execute("SELECT orders.id, employees.name, orders.order_date, orders.total_amount FROM orders JOIN employees ON orders.employee_id = employees.id")
        orders = self.cursor.fetchall()
        for order in orders:
            self.orders_tree.insert("", tk.END, values=order)

    def add_item(self):
        item_name = self.item_name_entry.get()
        quantity = self.item_quantity_entry.get()
        price = self.item_price_entry.get()
        self.cursor.execute("INSERT INTO inventory (item_name, quantity, price) VALUES (?, ?, ?)", (item_name, quantity, price))
        self.conn.commit()
        self.update_inventory_list()

    def update_inventory_list(self):
        for row in self.inventory_tree.get_children():
            self.inventory_tree.delete(row)
        self.cursor.execute("SELECT * FROM inventory")
        inventory = self.cursor.fetchall()
        for item in inventory:
            self.inventory_tree.insert("", tk.END, values=item)

    def generate_report(self):
        self.cursor.execute("SELECT SUM(total_amount) FROM orders")
        total_amount = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT SUM(quantity * price) FROM inventory")
        total_inventory = self.cursor.fetchone()[0]
        report_text = f"Общая сумма заказов: {total_amount}\nОбщая стоимость инвенторя: {total_inventory}"
        if total_amount != None and total_inventory != None:
            self.report_label.config(text=report_text)
        else:
            self.report_label.config(text="Недостаточно сведений для создания отчёта...")

    def add_point(self):
        name = self.point_name_entry.get()
        latitude = self.point_latitude_entry.get()
        longitude = self.point_longitude_entry.get()
        self.cursor.execute("INSERT INTO points (name, latitude, longitude) VALUES (?, ?, ?)", (name, latitude, longitude))
        self.conn.commit()
        self.update_points_list()
        self.update_map_points()

    def update_points_list(self):
        for row in self.points_tree.get_children():
            self.points_tree.delete(row)
        self.cursor.execute("SELECT * FROM points")
        points = self.cursor.fetchall()
        for point in points:
            self.points_tree.insert("", tk.END, values=point)

    def update_map_points(self):
        self.map_widget.delete_all_marker()
        self.cursor.execute("SELECT * FROM points")
        points = self.cursor.fetchall()
        for point in points:
            self.map_widget.set_marker(point[2], point[3], text=point[1])
                

    # def dismiss(window):
    #     window.grab_release() 
    #     window.destroy()
    

    # def click():
    #     window = Toplevel()
    #     window.title ("Открыть чат сотрудников")
    #     window.geometry("450x200")
    #     window.protocol("WM_DELETE_WINDOW", lambda: dismiss(window)) 
    #     close_button = ttk.Button(window, text="Закрыть чат", command=lambda: dismiss(window))
    #     close_button.pack(anchor="center", expand=1)
    #     window.grab_set()      
 
    #     open_button = ttk.Button(text="Создать чат", command=click)
    #     open_button.pack(anchor="center", expand=1)


if __name__ == "__main__":
    root = tk.Tk()
    app = CoffeeApp(root)
    root.mainloop()
