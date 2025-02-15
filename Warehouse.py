import sqlite3
from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime

class WarehouseApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Управление складом")
        self.master.geometry("1000x700")
        self.master.configure(bg='#f0f0f0')
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        self.conn = sqlite3.connect('warehouse.db')
        self.c = self.conn.cursor()
        self.create_tables()
        
        self.notebook = ttk.Notebook(master, style='Custom.TNotebook')
        self.create_dashboard_tab()
        self.create_zones_tab()
        self.create_suppliers_tab()
        self.create_goods_tab()
        self.create_reports_tab()
        self.notebook.pack(expand=1, fill='both', padx=10, pady=10)
        
    def configure_styles(self):
        self.style.configure('Custom.TNotebook', background='#f0f0f0')
        self.style.configure('Custom.TNotebook.Tab', 
                           font=('Helvetica', 10, 'bold'),
                           padding=[20, 5],
                           background='#d3d3d3',
                           foreground='#333333')
        self.style.map('Custom.TNotebook.Tab',
                     background=[('selected', '#4a90d9')],
                     foreground=[('selected', 'white')])
        
        self.style.configure('Treeview', 
                           font=('Helvetica', 9),
                           rowheight=25,
                           background='#ffffff',
                           fieldbackground='#ffffff')
        self.style.configure('Treeview.Heading', 
                           font=('Helvetica', 10, 'bold'),
                           background='#4a90d9',
                           foreground='white')
        self.style.configure('TButton', 
                           font=('Helvetica', 10, 'bold'),
                           padding=6,
                           background='#4a90d9',
                           foreground='white')
        self.style.configure('TLabel', 
                           font=('Helvetica', 10),
                           background='#f0f0f0',
                           foreground='#333333')
        self.style.configure('TEntry', 
                           font=('Helvetica', 10),
                           padding=5)
        self.style.configure('Horizontal.TProgressbar', 
                           thickness=20,
                           troughcolor='#d3d3d3',
                           background='#4a90d9')
        
    def create_tables(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS suppliers (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        contact TEXT)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS zones (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        capacity INTEGER,
                        occupied INTEGER DEFAULT 0)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS goods (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        supplier_id INTEGER,
                        zone_id INTEGER,
                        quantity INTEGER,
                        date_added TEXT)''')
        self.conn.commit()
    
    def create_dashboard_tab(self):
        tab = Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(tab, text="📊 Обзор")
        
        container = Frame(tab, bg='#ffffff', bd=2, relief=GROOVE)
        container.pack(pady=20, padx=20, fill='both', expand=True)
        
        Label(container, text="Состояние склада", font=('Helvetica', 14, 'bold'), 
              bg='#ffffff', fg='#333333').pack(pady=15)
        
        self.load_label = Label(container, text="Общая загруженность склада:", 
                              font=('Helvetica', 12), bg='#ffffff')
        self.load_label.pack(pady=10)
        
        self.progress = ttk.Progressbar(container, length=400, 
                                      style='Horizontal.TProgressbar')
        self.progress.pack(pady=5)
        self.update_progress()
    
    def create_zones_tab(self):
        tab = Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(tab, text="📦 Зоны")
        
        left_frame = Frame(tab, bg='#ffffff', bd=2, relief=GROOVE)
        left_frame.pack(side=LEFT, padx=10, pady=10, fill='y')
        
        Label(left_frame, text="Добавить новую зону", font=('Helvetica', 12, 'bold'), 
              bg='#ffffff').grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(left_frame, text="Название зоны:").grid(row=1, column=0, padx=5, pady=5)
        self.zone_name = ttk.Entry(left_frame)
        self.zone_name.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(left_frame, text="Вместимость:").grid(row=2, column=0, padx=5, pady=5)
        self.zone_capacity = ttk.Entry(left_frame)
        self.zone_capacity.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(left_frame, text="Добавить зону", command=self.add_zone).grid(
            row=3, column=0, columnspan=2, pady=10)
        
        right_frame = Frame(tab, bg='#ffffff', bd=2, relief=GROOVE)
        right_frame.pack(side=RIGHT, padx=10, pady=10, fill='both', expand=True)
        
        self.zones_tree = ttk.Treeview(right_frame, columns=('id', 'name', 'capacity', 'occupied'), 
                                     show='headings')
        self.zones_tree.heading('id', text='ID')
        self.zones_tree.heading('name', text='Название')
        self.zones_tree.heading('capacity', text='Вместимость')
        self.zones_tree.heading('occupied', text='Занято')
        
        vsb = ttk.Scrollbar(right_frame, orient="vertical", command=self.zones_tree.yview)
        self.zones_tree.configure(yscrollcommand=vsb.set)
        
        self.zones_tree.pack(side=LEFT, fill='both', expand=True)
        vsb.pack(side=RIGHT, fill='y')
        
        self.update_zones_list()
    
    def create_suppliers_tab(self):
        tab = Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(tab, text="🏭 Поставщики")
        
        left_frame = Frame(tab, bg='#ffffff', bd=2, relief=GROOVE)
        left_frame.pack(side=LEFT, padx=10, pady=10, fill='y')
        
        Label(left_frame, text="Управление поставщиками", font=('Helvetica', 12, 'bold'), 
              bg='#ffffff').grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(left_frame, text="Название:").grid(row=1, column=0, padx=5, pady=5)
        self.supplier_name = ttk.Entry(left_frame)
        self.supplier_name.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(left_frame, text="Контакты:").grid(row=2, column=0, padx=5, pady=5)
        self.supplier_contact = ttk.Entry(left_frame)
        self.supplier_contact.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(left_frame, text="Добавить", command=self.add_supplier).grid(
            row=3, column=0, pady=10, padx=5)
        ttk.Button(left_frame, text="Удалить", command=self.delete_supplier).grid(
            row=3, column=1, pady=10, padx=5)
        
        right_frame = Frame(tab, bg='#ffffff', bd=2, relief=GROOVE)
        right_frame.pack(side=RIGHT, padx=10, pady=10, fill='both', expand=True)
        
        self.suppliers_tree = ttk.Treeview(right_frame, columns=('id', 'name', 'contact'), 
                                        show='headings')
        self.suppliers_tree.heading('id', text='ID')
        self.suppliers_tree.heading('name', text='Название')
        self.suppliers_tree.heading('contact', text='Контакты')
        
        vsb = ttk.Scrollbar(right_frame, orient="vertical", command=self.suppliers_tree.yview)
        self.suppliers_tree.configure(yscrollcommand=vsb.set)
        
        self.suppliers_tree.pack(side=LEFT, fill='both', expand=True)
        vsb.pack(side=RIGHT, fill='y')
        
        self.update_suppliers_list()
    
    def create_goods_tab(self):
        tab = Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(tab, text="📦 Товары")
        
        form_frame = Frame(tab, bg='#ffffff', bd=2, relief=GROOVE)
        form_frame.pack(pady=10, padx=10, fill='x')
        
        Label(form_frame, text="Добавление товара", font=('Helvetica', 12, 'bold'), 
              bg='#ffffff').grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(form_frame, text="Товар:").grid(row=1, column=0, padx=5, pady=5)
        self.goods_name = ttk.Entry(form_frame)
        self.goods_name.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Поставщик:").grid(row=2, column=0, padx=5, pady=5)
        self.supplier_combo = ttk.Combobox(form_frame)
        self.supplier_combo.grid(row=2, column=1, padx=5, pady=5)
        self.update_suppliers_combo()
        
        ttk.Label(form_frame, text="Зона хранения:").grid(row=3, column=0, padx=5, pady=5)
        self.zone_combo = ttk.Combobox(form_frame)
        self.zone_combo.grid(row=3, column=1, padx=5, pady=5)
        self.update_zones_combo()
        
        ttk.Label(form_frame, text="Количество:").grid(row=4, column=0, padx=5, pady=5)
        self.goods_quantity = ttk.Entry(form_frame)
        self.goods_quantity.grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Дата поступления:").grid(row=5, column=0, padx=5, pady=5)
        self.goods_date = DateEntry(form_frame, date_pattern='dd.mm.yyyy')
        self.goods_date.grid(row=5, column=1, padx=5, pady=5)
        
        ttk.Button(form_frame, text="Добавить товар", command=self.add_goods).grid(
            row=6, column=0, columnspan=2, pady=10)
    
    def create_reports_tab(self):
        tab = Frame(self.notebook, bg='#f0f0f0')
        self.notebook.add(tab, text="📄 Отчеты")
        
        control_frame = Frame(tab, bg='#ffffff', bd=2, relief=GROOVE)
        control_frame.pack(pady=10, padx=10, fill='x')
        
        Label(control_frame, text="Параметры отчета", font=('Helvetica', 12, 'bold'), 
              bg='#ffffff').pack(pady=10)
        
        ttk.Label(control_frame, text="Начальная дата:").pack(side=LEFT, padx=5)
        self.start_date = DateEntry(control_frame, date_pattern='dd.mm.yyyy')
        self.start_date.pack(side=LEFT, padx=5)
        
        ttk.Label(control_frame, text="Конечная дата:").pack(side=LEFT, padx=5)
        self.end_date = DateEntry(control_frame, date_pattern='dd.mm.yyyy')
        self.end_date.pack(side=LEFT, padx=5)
        
        ttk.Button(control_frame, text="Сформировать отчет", command=self.generate_report).pack(
            side=LEFT, padx=10)
        
        report_frame = Frame(tab, bg='#ffffff', bd=2, relief=GROOVE)
        report_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        self.report_tree = ttk.Treeview(report_frame, columns=('name', 'quantity', 'date'), 
                                      show='headings')
        self.report_tree.heading('name', text='Товар')
        self.report_tree.heading('quantity', text='Количество')
        self.report_tree.heading('date', text='Дата')
        
        vsb = ttk.Scrollbar(report_frame, orient="vertical", command=self.report_tree.yview)
        self.report_tree.configure(yscrollcommand=vsb.set)
        
        self.report_tree.pack(side=LEFT, fill='both', expand=True)
        vsb.pack(side=RIGHT, fill='y')
    
    def add_zone(self):
        name = self.zone_name.get()
        capacity = self.zone_capacity.get()
        if not name or not capacity:
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
        try:
            self.c.execute("INSERT INTO zones (name, capacity) VALUES (?, ?)", (name, int(capacity)))
            self.conn.commit()
            self.update_zones_list()
            self.update_zones_combo()
            self.zone_name.delete(0, END)
            self.zone_capacity.delete(0, END)
        except:
            messagebox.showerror("Ошибка", "Некорректные данные")
    
    def add_supplier(self):
        name = self.supplier_name.get()
        contact = self.supplier_contact.get()
        if not name or not contact:
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
        try:
            self.c.execute("INSERT INTO suppliers (name, contact) VALUES (?, ?)", (name, contact))
            self.conn.commit()
            self.update_suppliers_list()
            self.update_suppliers_combo()
            self.supplier_name.delete(0, END)
            self.supplier_contact.delete(0, END)
        except:
            messagebox.showerror("Ошибка", "Ошибка при добавлении")
    
    def delete_supplier(self):
        selected = self.suppliers_tree.selection()
        if not selected:
            return
        supplier_id = self.suppliers_tree.item(selected[0], 'values')[0]
        try:
            self.c.execute("DELETE FROM suppliers WHERE id=?", (supplier_id,))
            self.conn.commit()
            self.update_suppliers_list()
            self.update_suppliers_combo()
        except:
            messagebox.showerror("Ошибка", "Нельзя удалить используемого поставщика")
    
    def add_goods(self):
        name = self.goods_name.get()
        supplier = self.supplier_combo.get()
        zone = self.zone_combo.get()
        quantity = self.goods_quantity.get()
        date = self.goods_date.get_date()
        if not all([name, supplier, zone, quantity]):
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
        try:
            supplier_id = self.c.execute("SELECT id FROM suppliers WHERE name=?", (supplier,)).fetchone()[0]
            zone_id = self.c.execute("SELECT id FROM zones WHERE name=?", (zone,)).fetchone()[0]
            self.c.execute('''INSERT INTO goods 
                           (name, supplier_id, zone_id, quantity, date_added)
                           VALUES (?, ?, ?, ?, ?)''',
                           (name, supplier_id, zone_id, int(quantity), date))
            self.c.execute("UPDATE zones SET occupied = occupied + ? WHERE id=?", (int(quantity), zone_id))
            self.conn.commit()
            self.update_progress()
            self.goods_name.delete(0, END)
            self.goods_quantity.delete(0, END)
            messagebox.showinfo("Успех", "Товар добавлен")
        except:
            messagebox.showerror("Ошибка", "Ошибка при добавлении товара")
    
    def generate_report(self):
        start = self.start_date.get_date()
        end = self.end_date.get_date()
        for row in self.report_tree.get_children():
            self.report_tree.delete(row)
        goods = self.c.execute('''SELECT name, quantity, date_added FROM goods
                               WHERE date_added BETWEEN ? AND ?''', (start, end)).fetchall()
        for good in goods:
            self.report_tree.insert('', END, values=good)
    
    def update_progress(self):
        total_capacity = self.c.execute("SELECT SUM(capacity) FROM zones").fetchone()[0]
        total_occupied = self.c.execute("SELECT SUM(occupied) FROM zones").fetchone()[0]
        if total_capacity and total_occupied:
            percent = (total_occupied / total_capacity) * 100
            self.progress['value'] = percent
            self.load_label.config(text=f"Общая загруженность склада: {percent:.1f}%")
    
    def update_zones_list(self):
        for row in self.zones_tree.get_children():
            self.zones_tree.delete(row)
        zones = self.c.execute("SELECT id, name, capacity, occupied FROM zones").fetchall()
        for zone in zones:
            self.zones_tree.insert('', END, values=zone)
    
    def update_zones_combo(self):
        zones = self.c.execute("SELECT name FROM zones").fetchall()
        self.zone_combo['values'] = [zone[0] for zone in zones]
    
    def update_suppliers_combo(self):
        suppliers = self.c.execute("SELECT name FROM suppliers").fetchall()
        self.supplier_combo['values'] = [supplier[0] for supplier in suppliers]
    
    def update_suppliers_list(self):
        for row in self.suppliers_tree.get_children():
            self.suppliers_tree.delete(row)
        suppliers = self.c.execute("SELECT id, name, contact FROM suppliers").fetchall()
        for supplier in suppliers:
            self.suppliers_tree.insert('', END, values=supplier)

if __name__ == "__main__":
    root = Tk()
    app = WarehouseApp(root)
    root.mainloop()
