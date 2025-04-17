import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
from datetime import datetime
from tkintermapview import TkinterMapView
from tkcalendar import DateEntry

class FlowerShopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Учет цветочного магазина")
        self.root.geometry("1200x820")
        
        self.set_styles()
        self.create_database()
        self.create_widgets()
        self.load_initial_data()

    def set_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#F5F5F5')
        self.style.configure('TLabel', background='#F5F5F5', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
        self.style.configure('Treeview', font=('Arial', 9), rowheight=25)
        self.style.map('TButton', foreground=[('active', '!disabled', 'white')], background=[('active', '#0052cc')])

    def create_database(self):
        self.conn = sqlite3.connect('flowershop.db')
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS flowers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                supplier_id INTEGER
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact TEXT NOT NULL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                position TEXT NOT NULL,
                salary REAL NOT NULL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flower_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                sale_date TEXT NOT NULL,
                total_price REAL NOT NULL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flower_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                purchase_date TEXT NOT NULL,
                supplier_id INTEGER NOT NULL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL
            )
        ''')
        
        self.conn.commit()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        
        self.flowers_frame = ttk.Frame(self.notebook)
        self.suppliers_frame = ttk.Frame(self.notebook)
        self.employees_frame = ttk.Frame(self.notebook)
        self.sales_frame = ttk.Frame(self.notebook)
        self.purchases_frame = ttk.Frame(self.notebook)
        self.reports_frame = ttk.Frame(self.notebook)
        self.map_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.flowers_frame, text="Цветы")
        self.notebook.add(self.suppliers_frame, text="Поставщики")
        self.notebook.add(self.employees_frame, text="Сотрудники")
        self.notebook.add(self.sales_frame, text="Продажи")
        self.notebook.add(self.purchases_frame, text="Закупки")
        self.notebook.add(self.reports_frame, text="Отчеты")
        self.notebook.add(self.map_frame, text="Карта")
        
        self.notebook.pack(expand=1, fill='both')
        
        self.create_flowers_tab()
        self.create_suppliers_tab()
        self.create_employees_tab()
        self.create_sales_tab()
        self.create_purchases_tab()
        self.create_reports_tab()
        self.create_map_tab()

    def create_flowers_tab(self):
        frame = ttk.LabelFrame(self.flowers_frame, text="Управление цветами", padding=10)
        frame.pack(pady=10, padx=10, fill='both', expand=True)

        ttk.Label(frame, text="Название:").grid(row=0, column=0, sticky='e')
        self.flower_name = ttk.Entry(frame, width=30)
        self.flower_name.grid(row=0, column=1, pady=2)

        ttk.Label(frame, text="Количество:").grid(row=1, column=0, sticky='e')
        self.flower_quantity = ttk.Entry(frame, width=30)
        self.flower_quantity.grid(row=1, column=1, pady=2)

        ttk.Label(frame, text="Цена:").grid(row=2, column=0, sticky='e')
        self.flower_price = ttk.Entry(frame, width=30)
        self.flower_price.grid(row=2, column=1, pady=2)

        ttk.Label(frame, text="Поставщик:").grid(row=3, column=0, sticky='e')
        self.flower_supplier = ttk.Combobox(frame, width=27)
        self.flower_supplier.grid(row=3, column=1, pady=2)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Добавить", command=self.add_flower).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Обновить", command=self.update_flower).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_flower).pack(side='left', padx=5)

        self.flowers_tree = ttk.Treeview(self.flowers_frame, columns=('ID','Name','Quantity','Price','Supplier'), show='headings')
        self.flowers_tree.heading('ID', text='ID')
        self.flowers_tree.heading('Name', text='Название')
        self.flowers_tree.heading('Quantity', text='Количество')
        self.flowers_tree.heading('Price', text='Цена')
        self.flowers_tree.heading('Supplier', text='Поставщик')
        self.flowers_tree.pack(fill='both', expand=True)
        
        self.flowers_tree.bind('<<TreeviewSelect>>', self.load_flower_data)

    def create_suppliers_tab(self):
        frame = ttk.LabelFrame(self.suppliers_frame, text="Управление поставщиками", padding=10)
        frame.pack(pady=10, padx=10, fill='both', expand=True)

        ttk.Label(frame, text="Название:").grid(row=0, column=0, sticky='e')
        self.supplier_name = ttk.Entry(frame, width=30)
        self.supplier_name.grid(row=0, column=1, pady=2)

        ttk.Label(frame, text="Контакты:").grid(row=1, column=0, sticky='e')
        self.supplier_contact = ttk.Entry(frame, width=30)
        self.supplier_contact.grid(row=1, column=1, pady=2)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Добавить", command=self.add_supplier).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Обновить", command=self.update_supplier).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_supplier).pack(side='left', padx=5)

        self.suppliers_tree = ttk.Treeview(self.suppliers_frame, columns=('ID','Name','Contact'), show='headings')
        self.suppliers_tree.heading('ID', text='ID')
        self.suppliers_tree.heading('Name', text='Название')
        self.suppliers_tree.heading('Contact', text='Контакты')
        self.suppliers_tree.pack(fill='both', expand=True)
        
        self.suppliers_tree.bind('<<TreeviewSelect>>', self.load_supplier_data)

    def create_employees_tab(self):
        frame = ttk.LabelFrame(self.employees_frame, text="Управление сотрудниками", padding=10)
        frame.pack(pady=10, padx=10, fill='both', expand=True)

        ttk.Label(frame, text="ФИО:").grid(row=0, column=0, sticky='e')
        self.employee_name = ttk.Entry(frame, width=30)
        self.employee_name.grid(row=0, column=1, pady=2)

        ttk.Label(frame, text="Должность:").grid(row=1, column=0, sticky='e')
        self.employee_position = ttk.Entry(frame, width=30)
        self.employee_position.grid(row=1, column=1, pady=2)

        ttk.Label(frame, text="Зарплата:").grid(row=2, column=0, sticky='e')
        self.employee_salary = ttk.Entry(frame, width=30)
        self.employee_salary.grid(row=2, column=1, pady=2)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Добавить", command=self.add_employee).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Обновить", command=self.update_employee).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_employee).pack(side='left', padx=5)

        self.employees_tree = ttk.Treeview(self.employees_frame, columns=('ID','FullName','Position','Salary'), show='headings')
        self.employees_tree.heading('ID', text='ID')
        self.employees_tree.heading('FullName', text='ФИО')
        self.employees_tree.heading('Position', text='Должность')
        self.employees_tree.heading('Salary', text='Зарплата')
        self.employees_tree.pack(fill='both', expand=True)
        
        self.employees_tree.bind('<<TreeviewSelect>>', self.load_employee_data)

    def create_sales_tab(self):
        frame = ttk.LabelFrame(self.sales_frame, text="Управление продажами", padding=10)
        frame.pack(pady=10, padx=10, fill='both', expand=True)

        ttk.Label(frame, text="Цветок:").grid(row=0, column=0, sticky='e')
        self.sale_flower = ttk.Combobox(frame, width=27)
        self.sale_flower.grid(row=0, column=1, pady=2)

        ttk.Label(frame, text="Количество:").grid(row=1, column=0, sticky='e')
        self.sale_quantity = ttk.Entry(frame, width=30)
        self.sale_quantity.grid(row=1, column=1, pady=2)

        ttk.Button(frame, text="Добавить", command=self.add_sale).grid(row=2, column=0, columnspan=2, pady=10)

        self.sales_tree = ttk.Treeview(self.sales_frame, columns=('ID','Flower','Quantity','Date','Total'), show='headings')
        self.sales_tree.heading('ID', text='ID')
        self.sales_tree.heading('Flower', text='Цветок')
        self.sales_tree.heading('Quantity', text='Количество')
        self.sales_tree.heading('Date', text='Дата')
        self.sales_tree.heading('Total', text='Сумма')
        self.sales_tree.pack(fill='both', expand=True)

    def create_purchases_tab(self):
        frame = ttk.LabelFrame(self.purchases_frame, text="Управление закупками", padding=10)
        frame.pack(pady=10, padx=10, fill='both', expand=True)

        ttk.Label(frame, text="Цветок:").grid(row=0, column=0, sticky='e')
        self.purchase_flower = ttk.Combobox(frame, width=27)
        self.purchase_flower.grid(row=0, column=1, pady=2)

        ttk.Label(frame, text="Количество:").grid(row=1, column=0, sticky='e')
        self.purchase_quantity = ttk.Entry(frame, width=30)
        self.purchase_quantity.grid(row=1, column=1, pady=2)

        ttk.Label(frame, text="Поставщик:").grid(row=2, column=0, sticky='e')
        self.purchase_supplier = ttk.Combobox(frame, width=27)
        self.purchase_supplier.grid(row=2, column=1, pady=2)

        ttk.Button(frame, text="Добавить", command=self.add_purchase).grid(row=3, column=0, columnspan=2, pady=10)

        self.purchases_tree = ttk.Treeview(self.purchases_frame, columns=('ID','Flower','Quantity','Date','Supplier'), show='headings')
        self.purchases_tree.heading('ID', text='ID')
        self.purchases_tree.heading('Flower', text='Цветок')
        self.purchases_tree.heading('Quantity', text='Количество')
        self.purchases_tree.heading('Date', text='Дата')
        self.purchases_tree.heading('Supplier', text='Поставщик')
        self.purchases_tree.pack(fill='both', expand=True)

    def create_reports_tab(self):
        frame = ttk.LabelFrame(self.reports_frame, text="Отчеты", padding=10)
        frame.pack(pady=10, padx=10, fill='both', expand=True)

        ttk.Label(frame, text="С:").grid(row=0, column=0)
        self.start_date = DateEntry(
            frame, 
            width=12, 
            background='darkblue',
            foreground='white', 
            borderwidth=2,
            date_pattern='y-mm-dd'
        )
        self.start_date.grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="По:").grid(row=0, column=2)
        self.end_date = DateEntry(
            frame, 
            width=12, 
            background='darkblue',
            foreground='white', 
            borderwidth=2,
            date_pattern='y-mm-dd'
        )
        self.end_date.grid(row=0, column=3, padx=5)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=1, column=0, columnspan=4, pady=10)
        ttk.Button(btn_frame, text="Продажи", command=self.generate_sales_report).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Закупки", command=self.generate_purchases_report).pack(side='left', padx=5)

        self.report_tree = ttk.Treeview(self.reports_frame, columns=('ID','Type','Details','Date','Amount'), show='headings')
        self.report_tree.heading('ID', text='ID')
        self.report_tree.heading('Type', text='Тип')
        self.report_tree.heading('Details', text='Детали')
        self.report_tree.heading('Date', text='Дата')
        self.report_tree.heading('Amount', text='Сумма')
        self.report_tree.pack(fill='both', expand=True)

    def create_map_tab(self):
        main_frame = ttk.Frame(self.map_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        control_frame = ttk.LabelFrame(main_frame, text="Управление маркерами", padding=10)
        control_frame.pack(side='left', fill='y')

        self.map_widget = TkinterMapView(main_frame, width=800, height=600)
        self.map_widget.pack(side='right', fill='both', expand=True)

        ttk.Label(control_frame, text="Адрес:").grid(row=0, column=0, sticky='e')
        self.location_address = ttk.Entry(control_frame, width=25)
        self.location_address.grid(row=0, column=1, pady=2)

        ttk.Label(control_frame, text="Широта:").grid(row=1, column=0, sticky='e')
        self.location_lat = ttk.Entry(control_frame, width=25)
        self.location_lat.grid(row=1, column=1, pady=2)

        ttk.Label(control_frame, text="Долгота:").grid(row=2, column=0, sticky='e')
        self.location_lon = ttk.Entry(control_frame, width=25)
        self.location_lon.grid(row=2, column=1, pady=2)

        btn_frame = ttk.Frame(control_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Добавить", command=self.add_location).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Обновить", command=self.update_location).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_location).pack(side='left', padx=5)

        self.locations_tree = ttk.Treeview(control_frame, columns=('ID','Address','Lat','Lon'), show='headings', height=15)
        self.locations_tree.heading('ID', text='ID')
        self.locations_tree.heading('Address', text='Адрес')
        self.locations_tree.heading('Lat', text='Широта')
        self.locations_tree.heading('Lon', text='Долгота')
        self.locations_tree.grid(row=4, column=0, columnspan=2, pady=10)
        
        self.locations_tree.bind('<<TreeviewSelect>>', self.load_location_data)

    def load_initial_data(self):
        self.update_flowers_tree()
        self.update_suppliers_tree()
        self.update_employees_tree()
        self.update_sales_tree()
        self.update_purchases_tree()
        self.update_comboboxes()
        self.update_locations_tree()
        self.update_map_markers()

    def update_comboboxes(self):
        self.cursor.execute("SELECT id, name FROM suppliers")
        suppliers = self.cursor.fetchall()
        self.flower_supplier['values'] = [f"{s[0]} - {s[1]}" for s in suppliers]
        self.purchase_supplier['values'] = [f"{s[0]} - {s[1]}" for s in suppliers]
        
        self.cursor.execute("SELECT id, name FROM flowers")
        flowers = self.cursor.fetchall()
        self.sale_flower['values'] = [f"{f[0]} - {f[1]}" for f in flowers]
        self.purchase_flower['values'] = [f"{f[0]} - {f[1]}" for f in flowers]

    def update_flowers_tree(self):
        for item in self.flowers_tree.get_children():
            self.flowers_tree.delete(item)
        self.cursor.execute("SELECT flowers.id, flowers.name, flowers.quantity, flowers.price, suppliers.name FROM flowers LEFT JOIN suppliers ON flowers.supplier_id = suppliers.id")
        for row in self.cursor.fetchall():
            self.flowers_tree.insert('', 'end', values=row)

    def update_suppliers_tree(self):
        for item in self.suppliers_tree.get_children():
            self.suppliers_tree.delete(item)
        self.cursor.execute("SELECT * FROM suppliers")
        for row in self.cursor.fetchall():
            self.suppliers_tree.insert('', 'end', values=row)

    def update_employees_tree(self):
        for item in self.employees_tree.get_children():
            self.employees_tree.delete(item)
        self.cursor.execute("SELECT * FROM employees")
        for row in self.cursor.fetchall():
            self.employees_tree.insert('', 'end', values=row)

    def update_sales_tree(self):
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        self.cursor.execute("SELECT sales.id, flowers.name, sales.quantity, sales.sale_date, sales.total_price FROM sales JOIN flowers ON sales.flower_id = flowers.id")
        for row in self.cursor.fetchall():
            self.sales_tree.insert('', 'end', values=row)

    def update_purchases_tree(self):
        for item in self.purchases_tree.get_children():
            self.purchases_tree.delete(item)
        self.cursor.execute("SELECT purchases.id, flowers.name, purchases.quantity, purchases.purchase_date, suppliers.name FROM purchases JOIN flowers ON purchases.flower_id = flowers.id JOIN suppliers ON purchases.supplier_id = suppliers.id")
        for row in self.cursor.fetchall():
            self.purchases_tree.insert('', 'end', values=row)

    def update_locations_tree(self):
        for item in self.locations_tree.get_children():
            self.locations_tree.delete(item)
        self.cursor.execute("SELECT * FROM locations")
        for row in self.cursor.fetchall():
            self.locations_tree.insert('', 'end', values=row)

    def update_map_markers(self):
        self.map_widget.delete_all_marker()
        self.cursor.execute("SELECT address, latitude, longitude FROM locations")
        for row in self.cursor.fetchall():
            self.map_widget.set_marker(row[1], row[2], text=row[0])

    def load_flower_data(self, event):
        selected = self.flowers_tree.selection()
        if selected:
            item = self.flowers_tree.item(selected[0])
            values = item['values']
            self.flower_name.delete(0, tk.END)
            self.flower_name.insert(0, values[1])
            self.flower_quantity.delete(0, tk.END)
            self.flower_quantity.insert(0, values[2])
            self.flower_price.delete(0, tk.END)
            self.flower_price.insert(0, values[3])
            self.flower_supplier.set(f"{values[4]}" if values[4] else "")

    def load_supplier_data(self, event):
        selected = self.suppliers_tree.selection()
        if selected:
            item = self.suppliers_tree.item(selected[0])
            values = item['values']
            self.supplier_name.delete(0, tk.END)
            self.supplier_name.insert(0, values[1])
            self.supplier_contact.delete(0, tk.END)
            self.supplier_contact.insert(0, values[2])

    def load_employee_data(self, event):
        selected = self.employees_tree.selection()
        if selected:
            item = self.employees_tree.item(selected[0])
            values = item['values']
            self.employee_name.delete(0, tk.END)
            self.employee_name.insert(0, values[1])
            self.employee_position.delete(0, tk.END)
            self.employee_position.insert(0, values[2])
            self.employee_salary.delete(0, tk.END)
            self.employee_salary.insert(0, values[3])

    def load_location_data(self, event):
        selected = self.locations_tree.selection()
        if selected:
            item = self.locations_tree.item(selected[0])
            values = item['values']
            self.location_address.delete(0, tk.END)
            self.location_address.insert(0, values[1])
            self.location_lat.delete(0, tk.END)
            self.location_lat.insert(0, values[2])
            self.location_lon.delete(0, tk.END)
            self.location_lon.insert(0, values[3])

    def add_flower(self):
        try:
            supplier = self.flower_supplier.get().split(' - ')[0]
            self.cursor.execute("INSERT INTO flowers (name, quantity, price, supplier_id) VALUES (?, ?, ?, ?)",
                               (self.flower_name.get(), 
                                int(self.flower_quantity.get()),
                                float(self.flower_price.get()),
                                int(supplier) if supplier else None))
            self.conn.commit()
            self.update_flowers_tree()
            self.update_comboboxes()
            self.clear_flower_fields()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def update_flower(self):
        selected = self.flowers_tree.selection()
        if selected:
            try:
                item = self.flowers_tree.item(selected[0])
                flower_id = item['values'][0]
                supplier = self.flower_supplier.get().split(' - ')[0]
                self.cursor.execute("UPDATE flowers SET name=?, quantity=?, price=?, supplier_id=? WHERE id=?",
                                   (self.flower_name.get(),
                                    int(self.flower_quantity.get()),
                                    float(self.flower_price.get()),
                                    int(supplier) if supplier else None,
                                    flower_id))
                self.conn.commit()
                self.update_flowers_tree()
                self.update_comboboxes()
                self.clear_flower_fields()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def delete_flower(self):
        selected = self.flowers_tree.selection()
        if selected:
            try:
                flower_id = self.flowers_tree.item(selected[0])['values'][0]
                self.cursor.execute("DELETE FROM flowers WHERE id=?", (flower_id,))
                self.conn.commit()
                self.update_flowers_tree()
                self.update_comboboxes()
                self.clear_flower_fields()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def clear_flower_fields(self):
        self.flower_name.delete(0, tk.END)
        self.flower_quantity.delete(0, tk.END)
        self.flower_price.delete(0, tk.END)
        self.flower_supplier.set('')

    def add_supplier(self):
        try:
            self.cursor.execute("INSERT INTO suppliers (name, contact) VALUES (?, ?)",
                               (self.supplier_name.get(), self.supplier_contact.get()))
            self.conn.commit()
            self.update_suppliers_tree()
            self.update_comboboxes()
            self.clear_supplier_fields()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def update_supplier(self):
        selected = self.suppliers_tree.selection()
        if selected:
            try:
                supplier_id = self.suppliers_tree.item(selected[0])['values'][0]
                self.cursor.execute("UPDATE suppliers SET name=?, contact=? WHERE id=?",
                                   (self.supplier_name.get(), self.supplier_contact.get(), supplier_id))
                self.conn.commit()
                self.update_suppliers_tree()
                self.update_comboboxes()
                self.clear_supplier_fields()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def delete_supplier(self):
        selected = self.suppliers_tree.selection()
        if selected:
            try:
                supplier_id = self.suppliers_tree.item(selected[0])['values'][0]
                self.cursor.execute("DELETE FROM suppliers WHERE id=?", (supplier_id,))
                self.conn.commit()
                self.update_suppliers_tree()
                self.update_comboboxes()
                self.clear_supplier_fields()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def clear_supplier_fields(self):
        self.supplier_name.delete(0, tk.END)
        self.supplier_contact.delete(0, tk.END)

    def add_employee(self):
        try:
            self.cursor.execute("INSERT INTO employees (full_name, position, salary) VALUES (?, ?, ?)",
                               (self.employee_name.get(), 
                                self.employee_position.get(),
                                float(self.employee_salary.get())))
            self.conn.commit()
            self.update_employees_tree()
            self.clear_employee_fields()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def update_employee(self):
        selected = self.employees_tree.selection()
        if selected:
            try:
                employee_id = self.employees_tree.item(selected[0])['values'][0]
                self.cursor.execute("UPDATE employees SET full_name=?, position=?, salary=? WHERE id=?",
                                   (self.employee_name.get(),
                                    self.employee_position.get(),
                                    float(self.employee_salary.get()),
                                    employee_id))
                self.conn.commit()
                self.update_employees_tree()
                self.clear_employee_fields()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def delete_employee(self):
        selected = self.employees_tree.selection()
        if selected:
            try:
                employee_id = self.employees_tree.item(selected[0])['values'][0]
                self.cursor.execute("DELETE FROM employees WHERE id=?", (employee_id,))
                self.conn.commit()
                self.update_employees_tree()
                self.clear_employee_fields()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def clear_employee_fields(self):
        self.employee_name.delete(0, tk.END)
        self.employee_position.delete(0, tk.END)
        self.employee_salary.delete(0, tk.END)

    def add_sale(self):
        try:
            flower_id = self.sale_flower.get().split(' - ')[0]
            quantity = int(self.sale_quantity.get())
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute("SELECT price FROM flowers WHERE id=?", (flower_id,))
            price = self.cursor.fetchone()[0]
            total = price * quantity
            
            self.cursor.execute("INSERT INTO sales (flower_id, quantity, sale_date, total_price) VALUES (?, ?, ?, ?)",
                               (flower_id, quantity, date, total))
            
            self.cursor.execute("UPDATE flowers SET quantity = quantity - ? WHERE id=?", (quantity, flower_id))
            
            self.conn.commit()
            self.update_sales_tree()
            self.update_flowers_tree()
            self.clear_sale_fields()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def clear_sale_fields(self):
        self.sale_flower.set('')
        self.sale_quantity.delete(0, tk.END)

    def add_purchase(self):
        try:
            flower_id = self.purchase_flower.get().split(' - ')[0]
            supplier_id = self.purchase_supplier.get().split(' - ')[0]
            quantity = int(self.purchase_quantity.get())
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute("INSERT INTO purchases (flower_id, quantity, purchase_date, supplier_id) VALUES (?, ?, ?, ?)",
                               (flower_id, quantity, date, supplier_id))
            
            self.cursor.execute("UPDATE flowers SET quantity = quantity + ? WHERE id=?", (quantity, flower_id))
            
            self.conn.commit()
            self.update_purchases_tree()
            self.update_flowers_tree()
            self.clear_purchase_fields()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def clear_purchase_fields(self):
        self.purchase_flower.set('')
        self.purchase_supplier.set('')
        self.purchase_quantity.delete(0, tk.END)

    def generate_sales_report(self):
        start_date_str = self.start_date.get()
        end_date_str = self.end_date.get()
        start = f"{start_date_str} 00:00:00"
        end = f"{end_date_str} 23:59:59"
        try:
            for item in self.report_tree.get_children():
                self.report_tree.delete(item)
            self.cursor.execute("""
                SELECT id, 'Продажа', flower_id || ' - ' || quantity || 'шт', sale_date, total_price 
                FROM sales 
                WHERE sale_date BETWEEN ? AND ?
            """, (start, end))
            for row in self.cursor.fetchall():
                self.report_tree.insert('', 'end', values=row)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def generate_purchases_report(self):
        start_date_str = self.start_date.get()
        end_date_str = self.end_date.get()
        start = f"{start_date_str} 00:00:00"
        end = f"{end_date_str} 23:59:59"
        try:
            for item in self.report_tree.get_children():
                self.report_tree.delete(item)
            self.cursor.execute("""
                SELECT id, 'Закупка', flower_id || ' - ' || quantity || 'шт', purchase_date, supplier_id 
                FROM purchases 
                WHERE purchase_date BETWEEN ? AND ?
            """, (start, end))
            for row in self.cursor.fetchall():
                self.report_tree.insert('', 'end', values=row)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def add_location(self):
        try:
            self.cursor.execute("INSERT INTO locations (address, latitude, longitude) VALUES (?, ?, ?)",
                              (self.location_address.get(),
                               float(self.location_lat.get()),
                               float(self.location_lon.get())))
            self.conn.commit()
            self.update_locations_tree()
            self.update_map_markers()
            self.clear_location_fields()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def update_location(self):
        selected = self.locations_tree.selection()
        if selected:
            try:
                loc_id = self.locations_tree.item(selected[0])['values'][0]
                self.cursor.execute("UPDATE locations SET address=?, latitude=?, longitude=? WHERE id=?",
                                  (self.location_address.get(),
                                   float(self.location_lat.get()),
                                   float(self.location_lon.get()),
                                   loc_id))
                self.conn.commit()
                self.update_locations_tree()
                self.update_map_markers()
                self.clear_location_fields()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def delete_location(self):
        selected = self.locations_tree.selection()
        if selected:
            try:
                loc_id = self.locations_tree.item(selected[0])['values'][0]
                self.cursor.execute("DELETE FROM locations WHERE id=?", (loc_id,))
                self.conn.commit()
                self.update_locations_tree()
                self.update_map_markers()
                self.clear_location_fields()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def clear_location_fields(self):
        self.location_address.delete(0, tk.END)
        self.location_lat.delete(0, tk.END)
        self.location_lon.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = FlowerShopApp(root)
    root.mainloop()
