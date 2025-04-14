import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime
import time
import json

conn = sqlite3.connect('hookah.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS tobaccos
             (id INTEGER PRIMARY KEY, name TEXT, strength INTEGER, grams REAL, 
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

c.execute('''CREATE TABLE IF NOT EXISTS hookahs
             (id INTEGER PRIMARY KEY, name TEXT, tobacco_taste TEXT, price REAL, 
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

c.execute('''CREATE TABLE IF NOT EXISTS establishments
             (id INTEGER PRIMARY KEY, name TEXT, hookahs TEXT, quantities TEXT, address TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
conn.commit()

class HookahApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Управление кальянными")
        self.geometry("1200x800")
        self.configure(bg='#f5f5f5')
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure('TNotebook', background='#ffffff')
        self.style.configure('TNotebook.Tab', 
                            font=('Arial', 12, 'bold'),
                            padding=12,
                            background='#e0e0e0',
                            foreground='#333333')
        self.style.map('TNotebook.Tab', 
                      background=[('selected', '#4CAF50')],
                      foreground=[('selected', '#ffffff')])
        
        self.style.configure('TFrame', background='#ffffff')
        self.style.configure('TLabel', 
                            font=('Arial', 12),
                            background='#ffffff',
                            foreground='#333333',
                            padding=5)
        self.style.configure('TButton', 
                            font=('Arial', 12, 'bold'),
                            background='#4CAF50',
                            foreground='white',
                            borderwidth=1,
                            padding=10)
        self.style.map('TButton',
                      background=[('active', '#45a049')])
        
        self.style.configure('Listbox', 
                            font=('Arial', 11),
                            background='#ffffff',
                            relief='flat',
                            selectbackground='#e0e0e0')
        
        self.notebook = ttk.Notebook(self)
        self.tabs = [
            ttk.Frame(self.notebook),
            ttk.Frame(self.notebook),
            ttk.Frame(self.notebook),
            ttk.Frame(self.notebook)
        ]
        
        for i, text in enumerate(["Табак", "Кальяны", "Заведения", "Отчеты"]):
            self.notebook.add(self.tabs[i], text=text)
        
        self.notebook.pack(expand=True, fill='both', padx=20, pady=20)
        
        self.create_tabacco_tab()
        self.create_hookah_tab()
        self.create_establishment_tab()
        self.create_report_tab()
        self.refresh_all()
        
    def refresh_all(self):
        self.update_tobacco_list()
        self.update_tastes()
        self.update_hookah_list()
        self.update_hookah_select()
        self.update_establishment_list()
        
    def create_tabacco_tab(self):
        frame = ttk.Frame(self.tabs[0], padding=20)
        frame.pack(fill='both', expand=True)
        
        form_frame = ttk.Frame(frame)
        form_frame.pack(pady=10)
        
        ttk.Label(form_frame, text="Название:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.t_name = ttk.Entry(form_frame, width=30, font=('Arial', 12))
        self.t_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Крепость (1-10):").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.t_strength = ttk.Entry(form_frame, width=30, font=('Arial', 12))
        self.t_strength.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Граммы:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.t_grams = ttk.Entry(form_frame, width=30, font=('Arial', 12))
        self.t_grams.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(form_frame, text="Добавить табак", command=lambda: self.add_tobacco())\
            .grid(row=3, columnspan=2, pady=15)
        
        self.tobacco_list = tk.Listbox(frame, width=80, height=15, font=('Arial', 11))
        self.tobacco_list.pack(pady=10)
        
    def add_tobacco(self):
        c.execute("INSERT INTO tobaccos (name, strength, grams) VALUES (?, ?, ?)",
                  (self.t_name.get(), self.t_strength.get(), self.t_grams.get()))
        conn.commit()
        self.refresh_all()
        
    def update_tobacco_list(self):
        self.tobacco_list.delete(0, tk.END)
        for row in c.execute("SELECT * FROM tobaccos"):
            self.tobacco_list.insert(tk.END, f"{row[1]} | Крепость: {row[2]} | Граммы: {row[3]}")

    def create_hookah_tab(self):
        frame = ttk.Frame(self.tabs[1], padding=20)
        frame.pack(fill='both', expand=True)
        
        form_frame = ttk.Frame(frame)
        form_frame.pack(pady=10)
        
        ttk.Label(form_frame, text="Название:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.h_name = ttk.Entry(form_frame, width=30, font=('Arial', 12))
        self.h_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Вкус табака:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.h_taste = ttk.Combobox(form_frame, width=28, font=('Arial', 12))
        self.h_taste.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Цена:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.h_price = ttk.Entry(form_frame, width=30, font=('Arial', 12))
        self.h_price.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(form_frame, text="Добавить кальян", command=lambda: self.add_hookah())\
            .grid(row=3, columnspan=2, pady=15)
        
        self.hookah_list = tk.Listbox(frame, width=80, height=15, font=('Arial', 11))
        self.hookah_list.pack(pady=10)
        
    def update_tastes(self):
        self.h_taste['values'] = [row[0] for row in c.execute("SELECT name FROM tobaccos")]
        
    def add_hookah(self):
        c.execute("INSERT INTO hookahs (name, tobacco_taste, price) VALUES (?, ?, ?)",
                  (self.h_name.get(), self.h_taste.get(), self.h_price.get()))
        conn.commit()
        self.refresh_all()
        
    def update_hookah_list(self):
        self.hookah_list.delete(0, tk.END)
        for row in c.execute("SELECT * FROM hookahs"):
            self.hookah_list.insert(tk.END, f"{row[1]} | Вкус: {row[2]} | Цена: {row[3]}")

    def create_establishment_tab(self):
        frame = ttk.Frame(self.tabs[2], padding=20)
        frame.pack(fill='both', expand=True)
        
        form_frame = ttk.Frame(frame)
        form_frame.pack(pady=10)
        
        ttk.Label(form_frame, text="Название заведения:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.e_name = ttk.Entry(form_frame, width=30, font=('Arial', 12))
        self.e_name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Адрес:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.e_address = ttk.Entry(form_frame, width=30, font=('Arial', 12))
        self.e_address.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Кальяны:").grid(row=2, column=0, sticky='ne', padx=5, pady=5)
        self.hookah_select = tk.Listbox(form_frame, selectmode=tk.MULTIPLE, width=30, height=5, font=('Arial', 11))
        self.hookah_select.grid(row=2, column=1, padx=5, pady=5, sticky='nw')
        
        ttk.Label(form_frame, text="Количество:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.e_quantity = ttk.Entry(form_frame, width=30, font=('Arial', 12))
        self.e_quantity.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Button(form_frame, text="Добавить заведение", command=lambda: self.add_establishment())\
            .grid(row=4, columnspan=2, pady=15)
        
        self.establishment_list = tk.Listbox(frame, width=80, height=15, font=('Arial', 11))
        self.establishment_list.pack(pady=10)
        
    def update_hookah_select(self):
        self.hookah_select.delete(0, tk.END)
        for row in c.execute("SELECT name FROM hookahs"):
            self.hookah_select.insert(tk.END, row[0])
            
    def add_establishment(self):
        selected = [self.hookah_select.get(i) for i in self.hookah_select.curselection()]
        c.execute("INSERT INTO establishments (name, hookahs, quantities, address) VALUES (?, ?, ?, ?)",
                  (self.e_name.get(), json.dumps(selected), self.e_quantity.get(), self.e_address.get()))
        conn.commit()
        self.refresh_all()
        
    def update_establishment_list(self):
        self.establishment_list.delete(0, tk.END)
        for row in c.execute("SELECT * FROM establishments"):
            self.establishment_list.insert(tk.END, 
                f"{row[1]} | Адрес: {row[4]} | Кальяны: {json.loads(row[2])} | Кол-во: {row[3]}")

    def create_report_tab(self):
        frame = ttk.Frame(self.tabs[3], padding=20)
        frame.pack(fill='both', expand=True)
        
        form_frame = ttk.Frame(frame)
        form_frame.pack(pady=10)
        
        ttk.Label(form_frame, text="С:").grid(row=0, column=0, padx=5, pady=5)
        self.start_date = DateEntry(form_frame, width=12, font=('Arial', 12))
        self.start_date.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="По:").grid(row=0, column=2, padx=5, pady=5)
        self.end_date = DateEntry(form_frame, width=12, font=('Arial', 12))
        self.end_date.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(form_frame, text="Сгенерировать отчет", command=self.generate_report)\
            .grid(row=0, column=4, padx=15)
        
        self.report_text = tk.Text(frame, width=90, height=25, font=('Arial', 11))
        self.report_text.pack(pady=10)
        
    def generate_report(self):
        start = self.start_date.get_date().strftime('%Y-%m-%d')
        end = self.end_date.get_date().strftime('%Y-%m-%d')
        
        report = []
        report.append("----- Отчет -----")
        report.append(f"Табаки добавленные с {start} по {end}:")
        for row in c.execute("SELECT name FROM tobaccos WHERE date(created_at) BETWEEN ? AND ?", (start, end)):
            report.append(f"- {row[0]}")
            
        report.append("\nКальяны добавленные:")
        for row in c.execute("SELECT name FROM hookahs WHERE date(created_at) BETWEEN ? AND ?", (start, end)):
            report.append(f"- {row[0]}")
            
        report.append("\nЗаведения добавленные:")
        for row in c.execute("SELECT name FROM establishments WHERE date(created_at) BETWEEN ? AND ?", (start, end)):
            report.append(f"- {row[0]}")
            
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, '\n'.join(report))

if __name__ == "__main__":
    app = HookahApp()
    app.mainloop()
