import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
from datetime import datetime

class ServiceCenterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Управление сервисным центром")
        self.root.geometry("1000x600")
        
        self.create_database()
        self.setup_ui()
        
    def create_database(self):
        self.conn = sqlite3.connect('service_center.db')
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS clients (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            phone TEXT NOT NULL,
                            email TEXT)''')
                            
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS equipment (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            serial_number TEXT UNIQUE NOT NULL,
                            client_id INTEGER,
                            FOREIGN KEY(client_id) REFERENCES clients(id))''')
                            
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS requests (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            description TEXT NOT NULL,
                            created_date TEXT NOT NULL,
                            status TEXT DEFAULT 'В обработке',
                            client_id INTEGER,
                            equipment_id INTEGER,
                            FOREIGN KEY(client_id) REFERENCES clients(id),
                            FOREIGN KEY(equipment_id) REFERENCES equipment(id))''')
        self.conn.commit()
    
    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        
        self.clients_tab = ttk.Frame(self.notebook)
        self.equipment_tab = ttk.Frame(self.notebook)
        self.requests_tab = ttk.Frame(self.notebook)
        self.reports_tab = ttk.Frame(self.notebook)
        
        self.setup_clients_tab()
        self.setup_equipment_tab()
        self.setup_requests_tab()
        self.setup_reports_tab()
        
        self.notebook.add(self.clients_tab, text="Клиенты")
        self.notebook.add(self.equipment_tab, text="Оборудование")
        self.notebook.add(self.requests_tab, text="Заявки")
        self.notebook.add(self.reports_tab, text="Отчеты")
        self.notebook.pack(expand=True, fill='both')
        
        self.load_clients_combobox()

    def setup_clients_tab(self):
        ttk.Label(self.clients_tab, text="Имя:").grid(row=0, column=0, padx=5, pady=5)
        self.client_name = ttk.Entry(self.clients_tab, width=30)
        self.client_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.clients_tab, text="Телефон:").grid(row=1, column=0, padx=5, pady=5)
        self.client_phone = ttk.Entry(self.clients_tab, width=30)
        self.client_phone.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self.clients_tab, text="Email:").grid(row=2, column=0, padx=5, pady=5)
        self.client_email = ttk.Entry(self.clients_tab, width=30)
        self.client_email.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(self.clients_tab, text="Добавить клиента", command=self.add_client).grid(row=3, column=1, pady=10)
        
        self.clients_tree = ttk.Treeview(self.clients_tab, columns=('id', 'name', 'phone', 'email'), show='headings')
        self.clients_tree.heading('id', text='ID')
        self.clients_tree.heading('name', text='Имя')
        self.clients_tree.heading('phone', text='Телефон')
        self.clients_tree.heading('email', text='Email')
        self.clients_tree.column('id', width=50)
        self.clients_tree.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        
        self.clients_tab.grid_columnconfigure(0, weight=1)
        self.clients_tab.grid_rowconfigure(4, weight=1)
        
        self.load_clients()

    def setup_equipment_tab(self):
        ttk.Label(self.equipment_tab, text="Название:").grid(row=0, column=0, padx=5, pady=5)
        self.equip_name = ttk.Entry(self.equipment_tab, width=30)
        self.equip_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.equipment_tab, text="Серийный номер:").grid(row=1, column=0, padx=5, pady=5)
        self.equip_serial = ttk.Entry(self.equipment_tab, width=30)
        self.equip_serial.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self.equipment_tab, text="Клиент:").grid(row=2, column=0, padx=5, pady=5)
        self.equip_client = ttk.Combobox(self.equipment_tab, width=27)
        self.equip_client.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(self.equipment_tab, text="Добавить оборудование", command=self.add_equipment).grid(row=3, column=1, pady=10)
        
        self.equipment_tree = ttk.Treeview(self.equipment_tab, columns=('id', 'name', 'serial', 'client'), show='headings')
        self.equipment_tree.heading('id', text='ID')
        self.equipment_tree.heading('name', text='Название')
        self.equipment_tree.heading('serial', text='Серийный номер')
        self.equipment_tree.heading('client', text='Клиент')
        self.equipment_tree.column('id', width=50)
        self.equipment_tree.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        
        self.equipment_tab.grid_columnconfigure(0, weight=1)
        self.equipment_tab.grid_rowconfigure(4, weight=1)
        
        self.load_equipment()

    def setup_requests_tab(self):
        ttk.Label(self.requests_tab, text="Клиент:").grid(row=0, column=0, padx=5, pady=5)
        self.request_client = ttk.Combobox(self.requests_tab, width=27)
        self.request_client.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.requests_tab, text="Оборудование:").grid(row=1, column=0, padx=5, pady=5)
        self.request_equipment = ttk.Combobox(self.requests_tab, width=27)
        self.request_equipment.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self.requests_tab, text="Описание проблемы:").grid(row=2, column=0, padx=5, pady=5)
        self.request_desc = ttk.Entry(self.requests_tab, width=30)
        self.request_desc.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(self.requests_tab, text="Создать заявку", command=self.add_request).grid(row=3, column=1, pady=10)
        
        self.requests_tree = ttk.Treeview(self.requests_tab, 
                                       columns=('id', 'client', 'equipment', 'desc', 'date', 'status'), 
                                       show='headings')
        self.requests_tree.heading('id', text='ID')
        self.requests_tree.heading('client', text='Клиент')
        self.requests_tree.heading('equipment', text='Оборудование')
        self.requests_tree.heading('desc', text='Описание')
        self.requests_tree.heading('date', text='Дата')
        self.requests_tree.heading('status', text='Статус')
        self.requests_tree.column('id', width=50)
        self.requests_tree.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        
        self.requests_tab.grid_columnconfigure(0, weight=1)
        self.requests_tab.grid_rowconfigure(4, weight=1)
        
        self.load_requests()

    def setup_reports_tab(self):
        ttk.Label(self.reports_tab, text="Выберите тип отчета:").grid(row=0, column=0, padx=5, pady=5)
        
        self.report_type = ttk.Combobox(self.reports_tab, values=[
            "Количество заявок по клиентам",
            "Список оборудования по клиентам",
            "Заявки по статусам"
        ], width=30)
        self.report_type.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(self.reports_tab, text="Сформировать отчет", command=self.generate_report).grid(row=1, column=1, pady=10)
        
        self.report_tree = ttk.Treeview(self.reports_tab, columns=('data1', 'data2', 'data3'), show='headings')
        self.report_tree.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        
        self.reports_tab.grid_columnconfigure(0, weight=1)
        self.reports_tab.grid_rowconfigure(2, weight=1)

    def generate_report(self):
        report_type = self.report_type.get()
        self.report_tree.delete(*self.report_tree.get_children())
        
        if report_type == "Количество заявок по клиентам":
            self.report_tree.heading('data1', text='Клиент')
            self.report_tree.heading('data2', text='Количество заявок')
            self.report_tree.heading('data3', text='')
            
            self.cursor.execute('''SELECT clients.name, COUNT(requests.id) 
                                FROM clients 
                                LEFT JOIN requests ON clients.id = requests.client_id 
                                GROUP BY clients.id''')
            data = self.cursor.fetchall()
            for row in data:
                self.report_tree.insert('', 'end', values=row)
        
        elif report_type == "Список оборудования по клиентам":
            self.report_tree.heading('data1', text='Клиент')
            self.report_tree.heading('data2', text='Оборудование')
            self.report_tree.heading('data3', text='Серийный номер')
            
            self.cursor.execute('''SELECT clients.name, equipment.name, equipment.serial_number 
                                FROM equipment 
                                JOIN clients ON equipment.client_id = clients.id''')
            data = self.cursor.fetchall()
            for row in data:
                self.report_tree.insert('', 'end', values=row)
        
        elif report_type == "Заявки по статусам":
            self.report_tree.heading('data1', text='Статус')
            self.report_tree.heading('data2', text='Количество')
            self.report_tree.heading('data3', text='')
            
            self.cursor.execute('''SELECT status, COUNT(id) 
                                FROM requests 
                                GROUP BY status''')
            data = self.cursor.fetchall()
            for row in data:
                self.report_tree.insert('', 'end', values=row)

    def add_client(self):
        name = self.client_name.get()
        phone = self.client_phone.get()
        email = self.client_email.get()
        
        if not name or not phone:
            messagebox.showerror("Ошибка", "Имя и телефон обязательны для заполнения")
            return
            
        self.cursor.execute("INSERT INTO clients (name, phone, email) VALUES (?, ?, ?)",
                          (name, phone, email))
        self.conn.commit()
        self.load_clients()
        self.load_clients_combobox()
        self.client_name.delete(0, 'end')
        self.client_phone.delete(0, 'end')
        self.client_email.delete(0, 'end')

    def load_clients(self):
        for row in self.clients_tree.get_children():
            self.clients_tree.delete(row)
            
        self.cursor.execute("SELECT * FROM clients")
        clients = self.cursor.fetchall()
        for client in clients:
            self.clients_tree.insert('', 'end', values=client)

    def add_equipment(self):
        name = self.equip_name.get()
        serial = self.equip_serial.get()
        client = self.equip_client.get().split(':')[0]
        
        if not name or not serial:
            messagebox.showerror("Ошибка", "Название и серийный номер обязательны")
            return
            
        try:
            self.cursor.execute("INSERT INTO equipment (name, serial_number, client_id) VALUES (?, ?, ?)",
                              (name, serial, client))
            self.conn.commit()
            self.load_equipment()
            self.equip_name.delete(0, 'end')
            self.equip_serial.delete(0, 'end')
            self.load_equipment_combobox()
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Серийный номер должен быть уникальным")

    def load_equipment(self):
        for row in self.equipment_tree.get_children():
            self.equipment_tree.delete(row)
            
        self.cursor.execute('''SELECT equipment.id, equipment.name, equipment.serial_number, clients.name 
                            FROM equipment 
                            JOIN clients ON equipment.client_id = clients.id''')
        equipment = self.cursor.fetchall()
        for item in equipment:
            self.equipment_tree.insert('', 'end', values=item)

    def add_request(self):
        client = self.request_client.get().split(':')[0]
        equipment = self.request_equipment.get().split(':')[0]
        desc = self.request_desc.get()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if not client or not equipment or not desc:
            messagebox.showerror("Ошибка", "Все поля обязательны для заполнения")
            return
            
        self.cursor.execute('''INSERT INTO requests 
                            (description, created_date, status, client_id, equipment_id)
                            VALUES (?, ?, ?, ?, ?)''',
                          (desc, date, 'В обработке', client, equipment))
        self.conn.commit()
        self.load_requests()
        self.request_desc.delete(0, 'end')

    def load_requests(self):
        for row in self.requests_tree.get_children():
            self.requests_tree.delete(row)
            
        self.cursor.execute('''SELECT requests.id, clients.name, equipment.name, 
                            requests.description, requests.created_date, requests.status
                            FROM requests
                            JOIN clients ON requests.client_id = clients.id
                            JOIN equipment ON requests.equipment_id = equipment.id''')
        requests = self.cursor.fetchall()
        for req in requests:
            self.requests_tree.insert('', 'end', values=req)

    def load_clients_combobox(self):
        self.cursor.execute("SELECT id, name FROM clients")
        clients = [f"{row[0]}: {row[1]}" for row in self.cursor.fetchall()]
        self.equip_client['values'] = clients
        self.request_client['values'] = clients

    def load_equipment_combobox(self):
        self.cursor.execute("SELECT id, name FROM equipment")
        equipment = [f"{row[0]}: {row[1]}" for row in self.cursor.fetchall()]
        self.request_equipment['values'] = equipment

if __name__ == "__main__":
    root = tk.Tk()
    app = ServiceCenterApp(root)
    root.mainloop()
