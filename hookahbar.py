import tkinter as tk
from tkinter import ttk, messagebox
from tkintermapview import TkinterMapView
from tkcalendar import DateEntry
import sqlite3
import json
from datetime import datetime
import requests
import time

conn = sqlite3.connect('hookah.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS tobaccos
             (id INTEGER PRIMARY KEY, name TEXT, strength INTEGER, grams REAL, 
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

c.execute('''CREATE TABLE IF NOT EXISTS hookahs
             (id INTEGER PRIMARY KEY, name TEXT, tobacco_taste TEXT, price REAL, 
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

c.execute('''CREATE TABLE IF NOT EXISTS establishments
             (id INTEGER PRIMARY KEY, name TEXT, hookahs TEXT, quantities TEXT, 
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

c.execute('''CREATE TABLE IF NOT EXISTS map_points
             (id INTEGER PRIMARY KEY, lat REAL, lon REAL, establishment_id INTEGER)''')
conn.commit()

class CustomMapView(TkinterMapView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_request = 0
        self.headers = {
            "User-Agent": "HookahApp/1.0 (contact@example.com)",
            "Referer": "http://localhost/"
        }

    def set_address(self, address, marker=True, **kwargs):
        try:
            if time.time() - self.last_request < 1:
                messagebox.showwarning("Ожидание", "Пожалуйста, подождите между запросами")
                return
                
            self.last_request = time.time()
            url = f"https://nominatim.openstreetmap.org/search?q={address}&format=jsonv2"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 403:
                messagebox.showerror("Ошибка", "Доступ запрещен. Проверьте настройки запроса")
                return
                
            response.raise_for_status()
            data = response.json()
            
            if not data:
                messagebox.showinfo("Не найдено", "Локация не найдена")
                return
                
            first_result = data[0]
            lat = float(first_result['lat'])
            lon = float(first_result['lon'])
            
            self.set_position(lat, lon)
            self.set_zoom(15)
            if marker:
                self.set_marker(lat, lon, text=address)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка геокодирования: {str(e)}")

class HookahApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Кальянная Управление")
        self.geometry("1200x800")
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TNotebook.Tab', padding=10, font=('Arial', 12))
        self.style.configure('TButton', font=('Arial', 12), padding=5)
        self.style.configure('TLabel', font=('Arial', 12), padding=5)
        
        self.notebook = ttk.Notebook(self)
        self.tabs = [
            ttk.Frame(self.notebook),
            ttk.Frame(self.notebook),
            ttk.Frame(self.notebook),
            ttk.Frame(self.notebook),
            ttk.Frame(self.notebook)
        ]
        
        for i, text in enumerate(["Табак", "Кальяны", "Заведения", "Карта", "Отчеты"]):
            self.notebook.add(self.tabs[i], text=text)
        
        self.notebook.pack(expand=True, fill='both')
        
        self.create_tabacco_tab()
        self.create_hookah_tab()
        self.create_establishment_tab()
        self.create_map_tab()
        self.create_report_tab()
        self.refresh_all()
        
    def refresh_all(self):
        self.update_tobacco_list()
        self.update_tastes()
        self.update_hookah_list()
        self.update_hookah_select()
        self.update_establishment_list()
        self.load_map_points()
        
    def create_tabacco_tab(self):
        frame = ttk.Frame(self.tabs[0])
        frame.pack(pady=20)
        
        ttk.Label(frame, text="Название:").grid(row=0, column=0)
        self.t_name = ttk.Entry(frame, width=30)
        self.t_name.grid(row=0, column=1)
        
        ttk.Label(frame, text="Крепость (1-10):").grid(row=1, column=0)
        self.t_strength = ttk.Entry(frame, width=30)
        self.t_strength.grid(row=1, column=1)
        
        ttk.Label(frame, text="Граммы:").grid(row=2, column=0)
        self.t_grams = ttk.Entry(frame, width=30)
        self.t_grams.grid(row=2, column=1)
        
        ttk.Button(frame, text="Добавить", command=lambda: self.add_tobacco()).grid(row=3, columnspan=2, pady=10)
        
        self.tobacco_list = tk.Listbox(self.tabs[0], width=50)
        self.tobacco_list.pack(pady=20)
        
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
        frame = ttk.Frame(self.tabs[1])
        frame.pack(pady=20)
        
        ttk.Label(frame, text="Название:").grid(row=0, column=0)
        self.h_name = ttk.Entry(frame, width=30)
        self.h_name.grid(row=0, column=1)
        
        ttk.Label(frame, text="Вкус табака:").grid(row=1, column=0)
        self.h_taste = ttk.Combobox(frame, width=27)
        self.h_taste.grid(row=1, column=1)
        
        ttk.Label(frame, text="Цена:").grid(row=2, column=0)
        self.h_price = ttk.Entry(frame, width=30)
        self.h_price.grid(row=2, column=1)
        
        ttk.Button(frame, text="Добавить", command=lambda: self.add_hookah()).grid(row=3, columnspan=2, pady=10)
        
        self.hookah_list = tk.Listbox(self.tabs[1], width=50)
        self.hookah_list.pack(pady=20)
        
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
        frame = ttk.Frame(self.tabs[2])
        frame.pack(pady=20)
        
        ttk.Label(frame, text="Название заведения:").grid(row=0, column=0)
        self.e_name = ttk.Entry(frame, width=30)
        self.e_name.grid(row=0, column=1)
        
        ttk.Label(frame, text="Кальяны:").grid(row=1, column=0)
        self.hookah_select = tk.Listbox(frame, selectmode=tk.MULTIPLE, width=30, height=5)
        self.hookah_select.grid(row=1, column=1)
        
        ttk.Label(frame, text="Количество:").grid(row=2, column=0)
        self.e_quantity = ttk.Entry(frame, width=30)
        self.e_quantity.grid(row=2, column=1)
        
        ttk.Button(frame, text="Добавить", command=lambda: self.add_establishment()).grid(row=3, columnspan=2, pady=10)
        
        self.establishment_list = tk.Listbox(self.tabs[2], width=50)
        self.establishment_list.pack(pady=20)
        
    def update_hookah_select(self):
        self.hookah_select.delete(0, tk.END)
        for row in c.execute("SELECT name FROM hookahs"):
            self.hookah_select.insert(tk.END, row[0])
            
    def add_establishment(self):
        selected = [self.hookah_select.get(i) for i in self.hookah_select.curselection()]
        c.execute("INSERT INTO establishments (name, hookahs, quantities) VALUES (?, ?, ?)",
                  (self.e_name.get(), json.dumps(selected), self.e_quantity.get()))
        conn.commit()
        self.refresh_all()
        
    def update_establishment_list(self):
        self.establishment_list.delete(0, tk.END)
        for row in c.execute("SELECT * FROM establishments"):
            self.establishment_list.insert(tk.END, f"{row[1]} | Кальяны: {json.loads(row[2])} | Кол-во: {row[3]}")

    def create_map_tab(self):
        self.map_widget = CustomMapView(self.tabs[3], width=1100, height=580)
        self.map_widget.pack()
        
        top_frame = ttk.Frame(self.tabs[3])
        top_frame.pack(pady=10)
        
        ttk.Label(top_frame, text="Город:").pack(side=tk.LEFT)
        self.city_entry = ttk.Entry(top_frame, width=30)
        self.city_entry.pack(side=tk.LEFT, padx=10)
        ttk.Button(top_frame, text="Поиск", command=self.search_city).pack(side=tk.LEFT)
        
        self.map_widget.add_right_click_menu_command("Добавить точку", self.add_map_point, pass_coords=True)
        
    def search_city(self):
        address = self.city_entry.get()
        if address:
            self.map_widget.set_address(address)
        
    def add_map_point(self, coords):
        lat, lon = coords
        establishments = [row[0] for row in c.execute("SELECT name FROM establishments")]
        
        if not establishments:
            messagebox.showerror("Ошибка", "Сначала создайте заведение!")
            return
            
        dlg = tk.Toplevel()
        dlg.title("Выбор заведения")
        ttk.Label(dlg, text="Выберите заведение:").pack(padx=10, pady=5)
        establishment_var = tk.StringVar(dlg)
        cb = ttk.Combobox(dlg, textvariable=establishment_var, values=establishments, width=30)
        cb.pack(padx=10, pady=5)
        
        def save_point():
            establishment = establishment_var.get()
            if establishment:
                c.execute("INSERT INTO map_points (lat, lon, establishment_id) VALUES (?, ?, (SELECT id FROM establishments WHERE name = ?))",
                          (lat, lon, establishment))
                conn.commit()
                self.refresh_all()
                dlg.destroy()
                
        ttk.Button(dlg, text="Сохранить", command=save_point).pack(pady=10)
        
    def load_map_points(self):
        self.map_widget.delete_all_marker()
        for row in c.execute("SELECT lat, lon, establishments.name FROM map_points JOIN establishments ON establishment_id = establishments.id"):
            self.map_widget.set_marker(row[0], row[1], text=row[2])

    def create_report_tab(self):
        frame = ttk.Frame(self.tabs[4])
        frame.pack(pady=20)
        
        ttk.Label(frame, text="С:").grid(row=0, column=0)
        self.start_date = DateEntry(frame)
        self.start_date.grid(row=0, column=1)
        
        ttk.Label(frame, text="По:").grid(row=1, column=0)
        self.end_date = DateEntry(frame)
        self.end_date.grid(row=1, column=1)
        
        ttk.Button(frame, text="Сгенерировать отчет", command=self.generate_report).grid(row=2, columnspan=2, pady=10)
        
        self.report_text = tk.Text(self.tabs[4], width=80, height=20)
        self.report_text.pack(pady=20)
        
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
