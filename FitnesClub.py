import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
from tkintermapview import TkinterMapView

COLORS = {
    "primary": "#2A3D4C",
    "secondary": "#A1B2B7",
    "background": "#F1F5F9",
    "text": "#3C4A55",
    "success": "#6DBE45",
    "warning": "#FFBB33",
    "danger": "#E63946" 
}


def connect_db():
    return sqlite3.connect('fitness_club.db')


def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS clients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        age INTEGER NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS subscriptions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        type TEXT CHECK(type IN ('дневной', 'вечерний', 'безлимитный')),
                        duration INTEGER NOT NULL,
                        price REAL NOT NULL,
                        start_time TEXT,
                        end_time TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS purchases (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        client_id INTEGER,
                        subscription_id INTEGER,
                        purchase_date TEXT,
                        discount REAL DEFAULT 0,
                        FOREIGN KEY(client_id) REFERENCES clients(id),
                        FOREIGN KEY(subscription_id) REFERENCES subscriptions(id))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS markers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        latitude REAL NOT NULL,
                        longitude REAL NOT NULL,
                        text TEXT)''')
    
    conn.commit()
    conn.close()


class FitnessApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1280x720")
        self.root.title("Fitness Club Manager")
        self.root.configure(bg=COLORS["background"])
        self.configure_styles()
        
        self.main_container = ttk.Frame(root)
        self.main_container.pack(fill="both", expand=True)
        
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(expand=True, fill="both", padx=20, pady=20)
        
        self.create_members_tab()
        self.create_subscriptions_tab()
        self.create_sales_tab()
        self.create_management_tab()
        self.create_map_tab()
        
        create_tables()
        self.load_initial_data()


    def configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure(".", background=COLORS["background"], foreground=COLORS["text"])
        style.configure("TNotebook", background=COLORS["background"], borderwidth=0)
        style.configure("TNotebook.Tab", 
                       font=('Arial', 10, 'bold'), 
                       padding=15,
                       background=COLORS["secondary"],
                       foreground="white")
        style.map("TNotebook.Tab", 
                 background=[("selected", COLORS["primary"])],
                 foreground=[("selected", "white")])
        
        style.configure("TButton", 
                       font=('Arial', 10, 'bold'), 
                       padding=8,
                       borderwidth=2,
                       relief="flat",
                       background=COLORS["primary"],
                       foreground="white")
        style.map("TButton", 
                 background=[('active', COLORS["secondary"]), ('disabled', '#D3D3D3')],
                 relief=[('active', 'sunken'), ('!active', 'flat')])
        
        style.configure("Treeview",
                       font=('Arial', 10),
                       rowheight=30,
                       borderwidth=1,
                       relief="solid",
                       fieldbackground=COLORS["background"])
        style.configure("Treeview.Heading", 
                       font=('Arial', 11, 'bold'),
                       background=COLORS["primary"],
                       foreground="white",
                       relief="flat")
        style.map("Treeview.Heading", 
                 background=[('active', COLORS["secondary"])])
        
        style.configure("Header.TLabel", 
                       font=('Arial', 16, 'bold'), 
                       foreground=COLORS["primary"],
                       background=COLORS["background"])
        style.configure("Secondary.TLabel",
                       font=('Arial', 12),
                       foreground=COLORS["text"],
                       background=COLORS["background"])
        
        style.configure("TEntry",
                        fieldbackground="white",
                        bordercolor=COLORS["primary"],
                        lightcolor=COLORS["primary"],
                        darkcolor=COLORS["primary"])
        style.map("TEntry",
                 fieldbackground=[("readonly", "#F0F0F0")])


    def create_members_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Участники")
        
        header_frame = ttk.Frame(tab)
        header_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(header_frame, text="Управление участниками", style="Header.TLabel").pack(side="left")
        
        content_frame = ttk.Frame(tab)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.members_tree = ttk.Treeview(content_frame, columns=("ID", "Имя", "Телефон", "Возраст"), show="headings")
        self.members_tree.pack(fill="both", expand=True, pady=10)
        
        for col in ("ID", "Имя", "Телефон", "Возраст"):
            self.members_tree.heading(col, text=col)
            self.members_tree.column(col, width=120, anchor="center")
            
        btn_frame = ttk.Frame(content_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Обновить список", command=self.load_members).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Добавить участника", command=self.add_member_dialog, style="Accent.TButton").pack(side="left", padx=5)


    def create_subscriptions_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Абонементы")
        
        header_frame = ttk.Frame(tab)
        header_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(header_frame, text="Доступные абонементы", style="Header.TLabel").pack(side="left")
        
        content_frame = ttk.Frame(tab)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.subs_tree = ttk.Treeview(content_frame, columns=("ID", "Название", "Тип", "Длительность", "Цена"), show="headings")
        self.subs_tree.pack(fill="both", expand=True, pady=10)
        
        for col in ("ID", "Название", "Тип", "Длительность", "Цена"):
            self.subs_tree.heading(col, text=col)
            self.subs_tree.column(col, width=120, anchor="center")
            
        btn_frame = ttk.Frame(content_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Обновить список", command=self.load_subscriptions).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Добавить абонемент", command=self.add_subscription_dialog, style="Accent.TButton").pack(side="left", padx=5)


    def create_sales_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Продажи")
        
        header_frame = ttk.Frame(tab)
        header_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(header_frame, text="Активные абонементы", style="Header.TLabel").pack(side="left")
        
        content_frame = ttk.Frame(tab)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.sales_tree = ttk.Treeview(content_frame, columns=("ID", "Участник", "Абонемент", "Начало", "Окончание", "Осталось"), show="headings")
        self.sales_tree.pack(fill="both", expand=True, pady=10)
        
        for col in ("ID", "Участник", "Абонемент", "Начало", "Окончание", "Осталось"):
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=120, anchor="center")
            
        btn_frame = ttk.Frame(content_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Обновить данные", command=self.load_sales).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Оформить продажу", command=self.create_sale_dialog, style="Accent.TButton").pack(side="left", padx=5)


    def create_management_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Администрирование")
        
        header_frame = ttk.Frame(tab)
        header_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(header_frame, text="Статистика клуба", style="Header.TLabel").pack(side="left")
        
        stats_frame = ttk.Frame(tab)
        stats_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        stat_card = ttk.Frame(stats_frame, style="Card.TFrame")
        stat_card.pack(pady=10, fill="x", padx=20)
        ttk.Label(stat_card, text="Всего участников:", style="Secondary.TLabel").pack(side="left", padx=10, pady=5)
        self.total_members_label = ttk.Label(stat_card, text="0", style="Secondary.TLabel", font=('Arial', 14, 'bold'))
        self.total_members_label.pack(side="left", padx=10)
        
        stat_card = ttk.Frame(stats_frame, style="Card.TFrame")
        stat_card.pack(pady=10, fill="x", padx=20)
        ttk.Label(stat_card, text="Активных абонементов:", style="Secondary.TLabel").pack(side="left", padx=10, pady=5)
        self.active_subs_label = ttk.Label(stat_card, text="0", style="Secondary.TLabel", font=('Arial', 14, 'bold'))
        self.active_subs_label.pack(side="left", padx=10)
        
        ttk.Button(stats_frame, text="Обновить статистику", command=self.update_stats).pack(pady=20)


    def create_map_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Локация")
        
        control_frame = ttk.Frame(tab)
        control_frame.pack(pady=10, padx=20, fill="x")
        
        input_frame = ttk.Frame(control_frame)
        input_frame.pack(side="left", padx=10)
        
        ttk.Label(input_frame, text="Широта:").grid(row=0, column=0, padx=5)
        self.lat_entry = ttk.Entry(input_frame, width=15)
        self.lat_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(input_frame, text="Долгота:").grid(row=0, column=2, padx=5)
        self.lon_entry = ttk.Entry(input_frame, width=15)
        self.lon_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(input_frame, text="Название:").grid(row=0, column=4, padx=5)
        self.marker_text_entry = ttk.Entry(input_frame, width=20)
        self.marker_text_entry.grid(row=0, column=5, padx=5)
        
        ttk.Button(
            control_frame, 
            text="Добавить точку", 
            command=self.add_marker,
            style="Accent.TButton"
        ).pack(side="left", padx=10)
        
        self.map_widget = TkinterMapView(tab, width=1200, height=600, corner_radius=15)
        self.map_widget.pack(pady=20, padx=20, fill="both", expand=True)
        self.map_widget.set_position(55.7558, 37.6173)
        self.map_widget.set_zoom(15)
        marker = self.map_widget.set_marker(55.7558, 37.6173, text="Fitness Club")
        marker.set_text("Главный фитнес-клуб")


    def load_initial_data(self):
        self.load_members()
        self.load_subscriptions()
        self.load_sales()
        self.update_stats()
        self.load_markers()


    def load_members(self):
        for row in self.members_tree.get_children():
            self.members_tree.delete(row)
            
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, phone, age FROM clients")
        for row in cursor.fetchall():
            self.members_tree.insert("", "end", values=row)
        conn.close()


    def load_subscriptions(self):
        for row in self.subs_tree.get_children():
            self.subs_tree.delete(row)
            
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, type, duration, price FROM subscriptions")
        for row in cursor.fetchall():
            self.subs_tree.insert("", "end", values=row)
        conn.close()


    def load_sales(self):
        for row in self.sales_tree.get_children():
            self.sales_tree.delete(row)
            
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''SELECT p.id, c.name, s.name, p.purchase_date, 
                        DATE(p.purchase_date, '+'||s.duration||' days'), 
                        julianday(DATE(p.purchase_date, '+'||s.duration||' days')) - julianday('now') 
                        FROM purchases p
                        JOIN clients c ON p.client_id = c.id
                        JOIN subscriptions s ON p.subscription_id = s.id''')
        for row in cursor.fetchall():
            days_left = int(float(row[5])) if row[5] else 0
            self.sales_tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4], days_left))
        conn.close()


    def update_stats(self):
        conn = connect_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM clients")
        self.total_members_label.config(text=cursor.fetchone()[0])
        
        cursor.execute("SELECT COUNT(*) FROM purchases")
        self.active_subs_label.config(text=cursor.fetchone()[0])
        
        conn.close()


    def add_member_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить участника")
        
        ttk.Label(dialog, text="ФИО:").grid(row=0, column=0, padx=10, pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Телефон:").grid(row=1, column=0, padx=10, pady=5)
        phone_entry = ttk.Entry(dialog)
        phone_entry.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Возраст:").grid(row=2, column=0, padx=10, pady=5)
        age_entry = ttk.Entry(dialog)
        age_entry.grid(row=2, column=1, padx=10, pady=5)
        
        def save_member():
            if name_entry.get() and phone_entry.get() and age_entry.get():
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO clients (name, phone, age) VALUES (?, ?, ?)", 
                             (name_entry.get(), phone_entry.get(), age_entry.get()))
                conn.commit()
                conn.close()
                self.load_members()
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Заполните все поля")
        
        ttk.Button(dialog, text="Сохранить", command=save_member).grid(row=3, column=0, columnspan=2, pady=10)


    def add_subscription_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить абонемент")
        
        ttk.Label(dialog, text="Название:").grid(row=0, column=0, padx=10, pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Тип:").grid(row=1, column=0, padx=10, pady=5)
        type_combobox = ttk.Combobox(dialog, values=["дневной", "вечерний", "безлимитный"])
        type_combobox.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Длительность (дней):").grid(row=2, column=0, padx=10, pady=5)
        duration_entry = ttk.Entry(dialog)
        duration_entry.grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Цена:").grid(row=3, column=0, padx=10, pady=5)
        price_entry = ttk.Entry(dialog)
        price_entry.grid(row=3, column=1, padx=10, pady=5)
        
        def save_subscription():
            if all([name_entry.get(), type_combobox.get(), duration_entry.get(), price_entry.get()]):
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO subscriptions 
                               (name, type, duration, price) 
                               VALUES (?, ?, ?, ?)''',
                               (name_entry.get(), type_combobox.get(), 
                                duration_entry.get(), price_entry.get()))
                conn.commit()
                conn.close()
                self.load_subscriptions()
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Заполните все поля")
        
        ttk.Button(dialog, text="Сохранить", command=save_subscription).grid(row=4, column=0, columnspan=2, pady=10)


    def create_sale_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Оформить продажу")
        
        ttk.Label(dialog, text="Участник:").grid(row=0, column=0, padx=10, pady=5)
        client_combobox = ttk.Combobox(dialog)
        client_combobox.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Абонемент:").grid(row=1, column=0, padx=10, pady=5)
        sub_combobox = ttk.Combobox(dialog)
        sub_combobox.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Скидка (%):").grid(row=2, column=0, padx=10, pady=5)
        discount_entry = ttk.Entry(dialog)
        discount_entry.grid(row=2, column=1, padx=10, pady=5)
        
        def load_clients():
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM clients")
            client_combobox['values'] = [row[0] for row in cursor.fetchall()]
            conn.close()
            
        def load_subs():
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM subscriptions")
            sub_combobox['values'] = [row[0] for row in cursor.fetchall()]
            conn.close()
            
        load_clients()
        load_subs()
        
        def process_sale():
            client = client_combobox.get()
            subscription = sub_combobox.get()
            discount = discount_entry.get() or 0
            
            if client and subscription:
                conn = connect_db()
                cursor = conn.cursor()
                
                cursor.execute("SELECT id FROM clients WHERE name = ?", (client,))
                client_id = cursor.fetchone()[0]
                
                cursor.execute("SELECT id FROM subscriptions WHERE name = ?", (subscription,))
                sub_id = cursor.fetchone()[0]
                
                cursor.execute('''INSERT INTO purchases 
                               (client_id, subscription_id, purchase_date, discount)
                               VALUES (?, ?, DATE('now'), ?)''',
                               (client_id, sub_id, discount))
                conn.commit()
                conn.close()
                self.load_sales()
                self.update_stats()
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Выберите участника и абонемент")
        
        ttk.Button(dialog, text="Оформить", command=process_sale).grid(row=3, column=0, columnspan=2, pady=10)


    def add_marker(self):
        lat = self.lat_entry.get()
        lon = self.lon_entry.get()
        text = self.marker_text_entry.get()
        
        try:
            lat_float = float(lat)
            lon_float = float(lon)
            
            self.map_widget.set_marker(lat_float, lon_float, text=text)
            
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO markers (latitude, longitude, text)
                            VALUES (?, ?, ?)''', (lat_float, lon_float, text))
            conn.commit()
            conn.close()
            
            self.lat_entry.delete(0, "end")
            self.lon_entry.delete(0, "end")
            self.marker_text_entry.delete(0, "end")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные координаты (числа)")


    def load_markers(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT latitude, longitude, text FROM markers")
        for row in cursor.fetchall():
            self.map_widget.set_marker(row[0], row[1], text=row[2])
        conn.close()
        
if __name__ == "__main__":
    root = tk.Tk()
    app = FitnessApp(root)
    root.mainloop()
