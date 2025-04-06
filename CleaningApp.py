import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry

def create_database():
    conn = sqlite3.connect('cleaning.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS services
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  price REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  service_id INTEGER,
                  employee_id INTEGER,
                  client TEXT,
                  date TEXT,
                  status TEXT DEFAULT 'Новый')''')
    c.execute('''CREATE TABLE IF NOT EXISTS employees
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  phone TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS company
                 (id INTEGER PRIMARY KEY,
                  name TEXT,
                  address TEXT,
                  phone TEXT)''')
    conn.commit()
    conn.close()

create_database()

class CleaningApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Профессиональная клининговая служба")
        self.root.geometry("1280x840")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        self.tabs = {
            'Услуги': ttk.Frame(self.notebook),
            'Заказы': ttk.Frame(self.notebook),
            'Сотрудники': ttk.Frame(self.notebook),
            'Компания': ttk.Frame(self.notebook)
        }

        for name, tab in self.tabs.items():
            self.notebook.add(tab, text=name)

        self.init_services_tab()
        self.init_orders_tab()
        self.init_employees_tab()
        self.init_company_tab()

    def configure_styles(self):
        self.style.configure('TFrame', background='#F5F5F5')
        self.style.configure('TButton', font=('Arial', 10), padding=6, background='#2196F3', foreground='white')
        self.style.configure('TLabel', font=('Arial', 11), background='#F5F5F5', foreground='#333333')
        self.style.configure('Header.TLabel', font=('Arial', 14, 'bold'), background='#607D8B', foreground='white')
        self.style.configure('Treeview.Heading', font=('Arial', 11, 'bold'), background='#B0BEC5')
        self.style.configure('Treeview', font=('Arial', 11), rowheight=25)
        self.style.map('TButton',
            background=[('active', '#1976D2'), ('disabled', '#BBDEFB')],
            foreground=[('disabled', '#757575')]
        )

    def init_services_tab(self):
        frame = ttk.Frame(self.tabs['Услуги'], padding=15)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Управление услугами", style='Header.TLabel').pack(fill='x', pady=(0, 15))
        
        self.services_tree = ttk.Treeview(frame, columns=('name', 'price'), show='headings')
        self.services_tree.heading('name', text='Название услуги')
        self.services_tree.heading('price', text='Стоимость', anchor='center')
        self.services_tree.column('price', width=150, anchor='center')
        self.services_tree.pack(fill='both', expand=True)

        control_frame = ttk.Frame(frame)
        control_frame.pack(pady=15)
        
        ttk.Label(control_frame, text="Название:").grid(row=0, column=0, padx=5, sticky='e')
        self.service_name = ttk.Entry(control_frame, width=35)
        self.service_name.grid(row=0, column=1, padx=5)
        
        ttk.Label(control_frame, text="Стоимость:").grid(row=0, column=2, padx=5, sticky='e')
        self.service_price = ttk.Entry(control_frame, width=15)
        self.service_price.grid(row=0, column=3, padx=5)
        
        ttk.Button(control_frame, text="Добавить", command=self.add_service).grid(row=0, column=4, padx=10)
        self.load_services()

    def init_orders_tab(self):
        frame = ttk.Frame(self.tabs['Заказы'], padding=15)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Создание заказа", style='Header.TLabel').pack(fill='x', pady=(0, 15))
        
        form_frame = ttk.Frame(frame)
        form_frame.pack(fill='x', pady=10)
        
        ttk.Label(form_frame, text="Услуга:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.order_service = ttk.Combobox(form_frame, state="readonly", width=30)
        self.order_service.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Сотрудник:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.order_employee = ttk.Combobox(form_frame, state="readonly", width=30)
        self.order_employee.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Клиент:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.order_client = ttk.Entry(form_frame, width=35)
        self.order_client.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Дата:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.order_date = DateEntry(form_frame, width=12)
        self.order_date.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Button(form_frame, text="Создать заказ", command=self.create_order).grid(row=4, column=1, pady=10, sticky='w')
        
        ttk.Label(frame, text="Активные заказы", style='Header.TLabel').pack(fill='x', pady=(20, 10))
        
        self.orders_tree = ttk.Treeview(frame, columns=('id', 'service', 'employee', 'client', 'date', 'status'), show='headings')
        self.orders_tree.heading('id', text='ID')
        self.orders_tree.heading('service', text='Услуга')
        self.orders_tree.heading('employee', text='Сотрудник')
        self.orders_tree.heading('client', text='Клиент')
        self.orders_tree.heading('date', text='Дата')
        self.orders_tree.heading('status', text='Статус')
        self.orders_tree.column('id', width=50, anchor='center')
        self.orders_tree.column('date', width=100)
        self.orders_tree.column('status', width=120)
        self.orders_tree.pack(fill='both', expand=True)
        
        self.load_orders()
        self.update_order_combos()

    def init_employees_tab(self):
        frame = ttk.Frame(self.tabs['Сотрудники'], padding=15)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Управление сотрудниками", style='Header.TLabel').pack(fill='x', pady=(0, 15))
        
        self.employees_tree = ttk.Treeview(frame, columns=('name', 'phone'), show='headings')
        self.employees_tree.heading('name', text='ФИО')
        self.employees_tree.heading('phone', text='Телефон')
        self.employees_tree.pack(fill='both', expand=True)

        control_frame = ttk.Frame(frame)
        control_frame.pack(pady=15)
        
        ttk.Label(control_frame, text="ФИО:").grid(row=0, column=0, padx=5, sticky='e')
        self.employee_name = ttk.Entry(control_frame, width=30)
        self.employee_name.grid(row=0, column=1, padx=5)
        
        ttk.Label(control_frame, text="Телефон:").grid(row=0, column=2, padx=5, sticky='e')
        self.employee_phone = ttk.Entry(control_frame, width=20)
        self.employee_phone.grid(row=0, column=3, padx=5)
        
        ttk.Button(control_frame, text="Добавить", command=self.add_employee).grid(row=0, column=4, padx=10)
        self.load_employees()

    def init_company_tab(self):
        frame = ttk.Frame(self.tabs['Компания'], padding=15)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Информация о компании", style='Header.TLabel').pack(fill='x', pady=(0, 15))
        
        form_frame = ttk.Frame(frame)
        form_frame.pack(fill='x', pady=10)
        
        ttk.Label(form_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.company_name = ttk.Entry(form_frame, width=40)
        self.company_name.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(form_frame, text="Адрес:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.company_address = ttk.Entry(form_frame, width=40)
        self.company_address.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(form_frame, text="Телефон:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.company_phone = ttk.Entry(form_frame, width=40)
        self.company_phone.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        
        form_frame.columnconfigure(1, weight=1)
        
        ttk.Button(frame, text="Сохранить", command=self.save_company).pack(pady=10)
        
        self.load_company()

    def load_services(self):
        for i in self.services_tree.get_children():
            self.services_tree.delete(i)
        conn = sqlite3.connect('cleaning.db')
        c = conn.cursor()
        c.execute("SELECT * FROM services")
        for row in c.fetchall():
            self.services_tree.insert('', 'end', values=(row[1], f"{row[2]} руб."))
        conn.close()

    def add_service(self):
        name = self.service_name.get()
        price = self.service_price.get()
        if name and price:
            try:
                conn = sqlite3.connect('cleaning.db')
                c = conn.cursor()
                c.execute("INSERT INTO services (name, price) VALUES (?, ?)", (name, float(price)))
                conn.commit()
                self.load_services()
                self.service_name.delete(0, 'end')
                self.service_price.delete(0, 'end')
                self.update_order_combos()
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат стоимости")
            finally:
                conn.close()
        else:
            messagebox.showwarning("Ошибка", "Заполните все поля")

    def load_orders(self):
        for i in self.orders_tree.get_children():
            self.orders_tree.delete(i)
        conn = sqlite3.connect('cleaning.db')
        c = conn.cursor()
        c.execute('''SELECT orders.id, services.name, employees.name, orders.client, 
                    orders.date, orders.status
                 FROM orders 
                 JOIN services ON orders.service_id = services.id
                 LEFT JOIN employees ON orders.employee_id = employees.id''')
        for row in c.fetchall():
            self.orders_tree.insert('', 'end', values=row)
        conn.close()

    def update_order_combos(self):
        conn = sqlite3.connect('cleaning.db')
        c = conn.cursor()
        
        c.execute("SELECT name FROM services")
        services = [row[0] for row in c.fetchall()]
        self.order_service['values'] = services
        
        c.execute("SELECT name FROM employees")
        employees = [row[0] for row in c.fetchall()]
        self.order_employee['values'] = employees
        
        conn.close()

    def create_order(self):
        service = self.order_service.get()
        employee = self.order_employee.get()
        client = self.order_client.get()
        date = self.order_date.get_date()
        
        if service and client and date:
            try:
                conn = sqlite3.connect('cleaning.db')
                c = conn.cursor()
                
                c.execute("SELECT id FROM services WHERE name = ?", (service,))
                service_id = c.fetchone()[0]
                
                employee_id = None
                if employee:
                    c.execute("SELECT id FROM employees WHERE name = ?", (employee,))
                    result = c.fetchone()
                    if result:
                        employee_id = result[0]
                
                c.execute('''INSERT INTO orders 
                          (service_id, employee_id, client, date)
                          VALUES (?, ?, ?, ?)''',
                          (service_id, employee_id, client, date))
                
                conn.commit()
                conn.close()
                self.load_orders()
                messagebox.showinfo("Успех", "Заказ создан")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        else:
            messagebox.showwarning("Ошибка", "Заполните обязательные поля")

    def load_employees(self):
        for i in self.employees_tree.get_children():
            self.employees_tree.delete(i)
        conn = sqlite3.connect('cleaning.db')
        c = conn.cursor()
        c.execute("SELECT * FROM employees")
        for row in c.fetchall():
            self.employees_tree.insert('', 'end', values=(row[1], row[2]))
        conn.close()

    def add_employee(self):
        name = self.employee_name.get()
        phone = self.employee_phone.get()
        if name and phone:
            conn = sqlite3.connect('cleaning.db')
            c = conn.cursor()
            c.execute("INSERT INTO employees (name, phone) VALUES (?, ?)", (name, phone))
            conn.commit()
            conn.close()
            self.load_employees()
            self.employee_name.delete(0, 'end')
            self.employee_phone.delete(0, 'end')
            self.update_order_combos()
        else:
            messagebox.showwarning("Ошибка", "Заполните все поля")

    def load_company(self):
        conn = sqlite3.connect('cleaning.db')
        c = conn.cursor()
        c.execute("SELECT * FROM company WHERE id = 1")
        company = c.fetchone()
        if company:
            self.company_name.insert(0, company[1])
            self.company_address.insert(0, company[2])
            self.company_phone.insert(0, company[3])
        conn.close()

    def save_company(self):
        name = self.company_name.get()
        address = self.company_address.get()
        phone = self.company_phone.get()
        if name and address and phone:
            conn = sqlite3.connect('cleaning.db')
            c = conn.cursor()
            c.execute('''INSERT OR REPLACE INTO company 
                      (id, name, address, phone) 
                      VALUES (1, ?, ?, ?)''', 
                      (name, address, phone))
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Данные компании сохранены")
        else:
            messagebox.showwarning("Ошибка", "Заполните все поля")

if __name__ == "__main__":
    root = tk.Tk()
    app = CleaningApp(root)
    root.mainloop()
