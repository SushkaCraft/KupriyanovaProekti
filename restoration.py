import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import Calendar, DateEntry
import sqlite3
from datetime import datetime

class FurnitureRestorationApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Сервис реставрации мебели")
        self.master.geometry("900x600")
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        self.conn = sqlite3.connect('restoration.db')
        self.create_tables()
        
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(pady=10, expand=True, fill='both')
        
        self.create_order_tab()
        self.create_orders_list_tab()
        self.create_calendar_tab()
        self.create_reports_tab()
        
        self.update_orders_list()
        self.load_calendar_events()
    
    def configure_styles(self):
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('Treeview', rowheight=25)
        self.style.map('Treeview', background=[('selected', '#0078D7')])
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        client_name TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        description TEXT NOT NULL,
                        order_date TEXT NOT NULL,
                        deadline_date TEXT NOT NULL,
                        status TEXT DEFAULT 'в работе')''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        order_id INTEGER NOT NULL,
                        report_text TEXT NOT NULL,
                        report_date TEXT NOT NULL,
                        FOREIGN KEY(order_id) REFERENCES orders(id))''')
        self.conn.commit()
    
    def create_order_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Новый заказ")
        
        fields_frame = ttk.Frame(tab)
        fields_frame.pack(pady=20, padx=20, fill='both')
        
        labels = ['Имя клиента:', 'Телефон:', 'Описание работ:', 'Дата заказа:', 'Срок выполнения:']
        self.entry_name = ttk.Entry(fields_frame, width=40)
        self.entry_phone = ttk.Entry(fields_frame, width=40)
        self.entry_desc = tk.Text(fields_frame, width=40, height=5)
        self.entry_order_date = DateEntry(fields_frame, width=37, date_pattern='dd.mm.yyyy')
        self.entry_deadline = DateEntry(fields_frame, width=37, date_pattern='dd.mm.yyyy')
        
        for i, text in enumerate(labels):
            ttk.Label(fields_frame, text=text).grid(row=i, column=0, padx=10, pady=5, sticky='e')
        
        self.entry_name.grid(row=0, column=1, padx=10, pady=5)
        self.entry_phone.grid(row=1, column=1, padx=10, pady=5)
        self.entry_desc.grid(row=2, column=1, padx=10, pady=5)
        self.entry_order_date.grid(row=3, column=1, padx=10, pady=5)
        self.entry_deadline.grid(row=4, column=1, padx=10, pady=5)
        
        ttk.Button(tab, text="Сохранить заказ", command=self.save_order).pack(pady=10)
    
    def create_orders_list_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Список заказов")
        
        filter_frame = ttk.Frame(tab)
        filter_frame.pack(pady=10, fill='x')
        
        self.filter_var = tk.StringVar(value='все')
        ttk.Label(filter_frame, text="Фильтр по статусу:").pack(side='left', padx=10)
        ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                    values=['все', 'в работе', 'завершено'], state='readonly', width=15).pack(side='left')
        self.filter_var.trace('w', lambda *args: self.update_orders_list())
        
        columns = ('id', 'client_name', 'order_date', 'deadline', 'status')
        self.tree = ttk.Treeview(tab, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col.capitalize().replace('_', ' '))
            self.tree.column(col, width=100, anchor='center')
        
        self.tree.column('id', width=50)
        self.tree.column('client_name', width=200)
        
        scrollbar = ttk.Scrollbar(tab, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.tree.bind('<Double-1>', self.show_order_details)
    
    def create_calendar_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Календарь сроков")
        
        self.calendar = Calendar(tab, selectmode='day', date_pattern='dd.mm.yyyy')
        self.calendar.pack(pady=10, padx=10, fill='both', expand=True)
        self.calendar.bind('<<CalendarSelected>>', self.update_calendar_orders)
        
        self.calendar_orders_tree = ttk.Treeview(tab, columns=('client', 'deadline'), show='headings')
        self.calendar_orders_tree.heading('client', text='Клиент')
        self.calendar_orders_tree.heading('deadline', text='Срок выполнения')
        self.calendar_orders_tree.pack(pady=10, padx=10, fill='both', expand=True)
    
    def create_reports_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Отчеты")
        
        report_frame = ttk.Frame(tab)
        report_frame.pack(pady=10, fill='x')
        
        ttk.Label(report_frame, text="Выберите заказ:").pack(side='left', padx=10)
        self.report_order_var = tk.StringVar()
        self.report_order_combobox = ttk.Combobox(report_frame, textvariable=self.report_order_var, state='readonly')
        self.report_order_combobox.pack(side='left', padx=10)
        self.update_report_orders()
        
        ttk.Label(tab, text="Текст отчета:").pack(pady=5)
        self.report_text = tk.Text(tab, height=10, width=80)
        self.report_text.pack(pady=5, padx=10)
        
        ttk.Button(tab, text="Сохранить отчет", command=self.save_report).pack(pady=10)
        
        self.reports_tree = ttk.Treeview(tab, columns=('order_id', 'date', 'text'), show='headings')
        self.reports_tree.heading('order_id', text='№ заказа')
        self.reports_tree.heading('date', text='Дата отчета')
        self.reports_tree.heading('text', text='Содержание')
        self.reports_tree.column('text', width=400)
        self.reports_tree.pack(pady=10, padx=10, fill='both', expand=True)
        self.update_reports_list()
    
    def save_order(self):
        try:
            order_date = self.entry_order_date.get_date().strftime('%Y-%m-%d')
            deadline = self.entry_deadline.get_date().strftime('%Y-%m-%d')
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка в дате: {str(e)}")
            return
        
        data = (
            self.entry_name.get(),
            self.entry_phone.get(),
            self.entry_desc.get("1.0", tk.END).strip(),
            order_date,
            deadline
        )
        
        if not all(data):
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''INSERT INTO orders 
                          (client_name, phone, description, order_date, deadline_date)
                          VALUES (?, ?, ?, ?, ?)''', data)
            self.conn.commit()
            messagebox.showinfo("Успех", "Заказ успешно сохранен!")
            self.update_orders_list()
            self.load_calendar_events()
            self.update_report_orders()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка базы данных: {str(e)}")
    
    def update_orders_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        filter_status = self.filter_var.get()
        query = "SELECT id, client_name, order_date, deadline_date, status FROM orders"
        params = ()
        
        if filter_status != 'все':
            query += " WHERE status = ?"
            params = (filter_status,)
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        
        for row in cursor.fetchall():
            self.tree.insert('', 'end', values=row)
    
    def load_calendar_events(self):
        self.calendar.calevent_remove('all')
        cursor = self.conn.cursor()
        cursor.execute("SELECT deadline_date FROM orders WHERE status = 'в работе'")
        
        dates = []
        for row in cursor.fetchall():
            try:
                d = datetime.strptime(row[0], '%Y-%m-%d').date()
                dates.append(d)
            except ValueError:
                continue
        
        for date_obj in dates:
            self.calendar.calevent_create(
                date_obj, 
                'Срок сдачи', 
                'deadline'
            )
        self.calendar.tag_config('deadline', background='#d9534f', foreground='white')
    
    def update_calendar_orders(self, event=None):
        selected_date = datetime.strptime(self.calendar.get_date(), '%d.%m.%Y').strftime('%Y-%m-%d')
        
        for row in self.calendar_orders_tree.get_children():
            self.calendar_orders_tree.delete(row)
        
        cursor = self.conn.cursor()
        cursor.execute('''SELECT client_name, deadline_date 
                       FROM orders WHERE deadline_date = ?''', 
                       (selected_date,))
        
        for row in cursor.fetchall():
            self.calendar_orders_tree.insert('', 'end', values=(
                row[0],
                datetime.strptime(row[1], '%Y-%m-%d').strftime('%d.%m.%Y')
            ))
    
    def show_order_details(self, event):
        item = self.tree.selection()[0]
        order_id = self.tree.item(item, 'values')[0]
        
        cursor = self.conn.cursor()
        cursor.execute('''SELECT * FROM orders WHERE id = ?''', (order_id,))
        order = cursor.fetchone()
        
        detail_window = tk.Toplevel(self.master)
        detail_window.title(f"Заказ №{order[0]}")
        
        ttk.Label(detail_window, text=f"Клиент: {order[1]}").pack(pady=5)
        ttk.Label(detail_window, text=f"Телефон: {order[2]}").pack(pady=5)
        ttk.Label(detail_window, text=f"Описание: {order[3]}").pack(pady=5)
        
        status_frame = ttk.Frame(detail_window)
        status_frame.pack(pady=5)
        ttk.Label(status_frame, text="Статус:").pack(side='left')
        status_var = tk.StringVar(value=order[6])
        status_combobox = ttk.Combobox(status_frame, textvariable=status_var, 
                                      values=['в работе', 'завершено'], state='readonly')
        status_combobox.pack(side='left', padx=10)
        
        ttk.Button(detail_window, text="Обновить статус",
                  command=lambda: self.update_status(order_id, status_var.get(), detail_window)).pack(pady=10)
    
    def update_status(self, order_id, new_status, window):
        cursor = self.conn.cursor()
        cursor.execute('''UPDATE orders SET status = ? WHERE id = ?''', 
                     (new_status, order_id))
        self.conn.commit()
        window.destroy()
        self.update_orders_list()
        self.load_calendar_events()
    
    def update_report_orders(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, client_name FROM orders")
        orders = [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]
        self.report_order_combobox['values'] = orders
    
    def save_report(self):
        order = self.report_order_var.get()
        if not order:
            messagebox.showerror("Ошибка", "Выберите заказ!")
            return
        
        report_text = self.report_text.get("1.0", tk.END).strip()
        if not report_text:
            messagebox.showerror("Ошибка", "Введите текст отчета!")
            return
        
        order_id = order.split(' - ')[0]
        report_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('''INSERT INTO reports 
                          (order_id, report_text, report_date)
                          VALUES (?, ?, ?)''', 
                          (order_id, report_text, report_date))
            self.conn.commit()
            messagebox.showinfo("Успех", "Отчет сохранен!")
            self.update_reports_list()
            self.report_text.delete("1.0", tk.END)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка базы данных: {str(e)}")
    
    def update_reports_list(self):
        for row in self.reports_tree.get_children():
            self.reports_tree.delete(row)
        
        cursor = self.conn.cursor()
        cursor.execute('''SELECT order_id, report_date, report_text FROM reports''')
        for row in cursor.fetchall():
            self.reports_tree.insert('', 'end', values=row)
    
    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = FurnitureRestorationApp(root)
    root.mainloop()
