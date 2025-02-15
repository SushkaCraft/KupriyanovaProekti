import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import sqlite3

class ComputerClubApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Управление компьютерным клубом")
        self.geometry("1000x700")
        self.configure(bg='#F0F0F0')
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.setupStyles()
        self.createDatabase()
        self.setupUI()
        self.updateComputersList()
        self.updateRoomsList()

    def setupStyles(self):
        self.style.configure('TNotebook', background='#F0F0F0')
        self.style.configure('TFrame', background='#F0F0F0')
        self.style.configure('TButton', foreground='white', background='#4CAF50', 
                            font=('Arial', 10), padding=5)
        self.style.map('TButton', background=[('active', '#45a049')])
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'), 
                            foreground='#333333', background='#F0F0F0')
        self.style.configure('Red.TButton', background='#ff4444', foreground='white')
        self.style.map('Red.TButton', background=[('active', '#cc0000')])

    def createDatabase(self):
        conn = sqlite3.connect('computer_club.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Computers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Rooms (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        computer_id INTEGER,
                        quantity INTEGER,
                        price_per_hour REAL,
                        FOREIGN KEY (computer_id) REFERENCES Computers(id))''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Bookings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        room_id INTEGER,
                        computer_number INTEGER,
                        start_time DATETIME,
                        end_time DATETIME,
                        FOREIGN KEY (room_id) REFERENCES Rooms(id))''')
        conn.commit()
        conn.close()

    def setupUI(self):
        self.notebook = ttk.Notebook(self)
        self.createComputersTab()
        self.createRoomsTab()
        self.createBookingTab()
        self.createReportsTab()
        self.notebook.pack(expand=True, fill='both')
        self.notebook.bind("<<NotebookTabChanged>>", self.onTabChange)

    def onTabChange(self, event):
        current_tab = self.notebook.tab(self.notebook.select(), 'text')
        if current_tab == 'Помещения':
            self.updateComputersList()
        elif current_tab == 'Бронирование':
            self.updateRoomsList()
        elif current_tab == 'Отчеты':
            self.generateReport()

    def createComputersTab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Компьютеры')
        
        ttk.Label(frame, text='Добавление компьютера', style='Header.TLabel').pack(pady=10)
        
        form_frame = ttk.Frame(frame)
        form_frame.pack(pady=20, padx=30)
        
        ttk.Label(form_frame, text='Название:').grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.computer_name = ttk.Entry(form_frame, width=30)
        self.computer_name.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(form_frame, text='Описание:').grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.computer_desc = ttk.Entry(form_frame, width=30)
        self.computer_desc.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Button(form_frame, text='Сохранить', command=self.saveComputer).grid(row=2, columnspan=2, pady=15)

    def createRoomsTab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Помещения')
        
        ttk.Label(frame, text='Добавление помещения', style='Header.TLabel').pack(pady=10)
        
        self.room_form_frame = ttk.Frame(frame)
        self.room_form_frame.pack(pady=20, padx=30)
        
        self.updateComputersList()
        
        ttk.Label(self.room_form_frame, text='Название:').grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.room_name = ttk.Entry(self.room_form_frame, width=30)
        self.room_name.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(self.room_form_frame, text='Компьютер:').grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.computer_combo = ttk.Combobox(self.room_form_frame, width=27)
        self.computer_combo.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(self.room_form_frame, text='Количество:').grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.room_quantity = ttk.Spinbox(self.room_form_frame, from_=1, to=100, width=28)
        self.room_quantity.grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(self.room_form_frame, text='Цена за час:').grid(row=3, column=0, padx=10, pady=5, sticky='e')
        self.room_price = ttk.Entry(self.room_form_frame, width=30)
        self.room_price.grid(row=3, column=1, padx=10, pady=5)
        
        ttk.Button(self.room_form_frame, text='Сохранить', command=self.saveRoom).grid(row=4, columnspan=2, pady=15)

    def createBookingTab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Бронирование')
        
        ttk.Label(frame, text='Выберите помещение', style='Header.TLabel').pack(pady=10)
        
        self.room_combo = ttk.Combobox(frame, width=40)
        self.room_combo.pack(pady=10)
        self.room_combo.bind("<<ComboboxSelected>>", self.showComputers)
        
        self.computers_frame = ttk.Frame(frame)
        self.computers_frame.pack(pady=20, padx=30)

    def createReportsTab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Отчеты')
        
        ttk.Label(frame, text='Генерация отчета', style='Header.TLabel').pack(pady=10)
        
        form_frame = ttk.Frame(frame)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text='С:').grid(row=0, column=0, padx=10, pady=5)
        self.start_date = DateEntry(form_frame, date_pattern='yyyy-mm-dd', width=12)
        self.start_date.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(form_frame, text='По:').grid(row=0, column=2, padx=10, pady=5)
        self.end_date = DateEntry(form_frame, date_pattern='yyyy-mm-dd', width=12)
        self.end_date.grid(row=0, column=3, padx=10, pady=5)
        
        ttk.Button(form_frame, text='Сформировать', command=self.generateReport).grid(row=0, column=4, padx=20)
        
        self.report_text = tk.Text(frame, height=12, width=70, font=('Arial', 10), bg='white', bd=2)
        self.report_text.pack(pady=20, padx=30)

    def saveComputer(self):
        name = self.computer_name.get()
        desc = self.computer_desc.get()
        if not name:
            messagebox.showerror("Ошибка", "Введите название компьютера")
            return
        
        conn = sqlite3.connect('computer_club.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Computers (name, description) VALUES (?, ?)", (name, desc))
        conn.commit()
        conn.close()
        
        self.computer_name.delete(0, tk.END)
        self.computer_desc.delete(0, tk.END)
        self.updateComputersList()
        messagebox.showinfo("Успех", "Компьютер успешно добавлен")

    def updateComputersList(self):
        conn = sqlite3.connect('computer_club.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM Computers")
        self.computers = cursor.fetchall()
        conn.close()
        
        if hasattr(self, 'computer_combo'):
            self.computer_combo['values'] = [c[1] for c in self.computers]

    def saveRoom(self):
        name = self.room_name.get()
        computer = self.computer_combo.get()
        quantity = self.room_quantity.get()
        price = self.room_price.get()
        
        if not all([name, computer, quantity, price]):
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
        
        try:
            computer_id = next(c[0] for c in self.computers if c[1] == computer)
        except StopIteration:
            messagebox.showerror("Ошибка", "Выберите компьютер из списка")
            return
        
        conn = sqlite3.connect('computer_club.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO Rooms (name, computer_id, quantity, price_per_hour)
                        VALUES (?, ?, ?, ?)''', (name, computer_id, quantity, float(price)))
        conn.commit()
        conn.close()
        
        self.room_name.delete(0, tk.END)
        self.room_quantity.delete(0, tk.END)
        self.room_price.delete(0, tk.END)
        self.updateRoomsList()
        messagebox.showinfo("Успех", "Помещение успешно добавлено")

    def updateRoomsList(self):
        conn = sqlite3.connect('computer_club.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM Rooms")
        self.rooms = cursor.fetchall()
        conn.close()
        
        if hasattr(self, 'room_combo'):
            self.room_combo['values'] = [r[1] for r in self.rooms]

    def showComputers(self, event=None):
        for widget in self.computers_frame.winfo_children():
            widget.destroy()
        
        room_name = self.room_combo.get()
        try:
            room_id = next(r[0] for r in self.rooms if r[1] == room_name)
        except StopIteration:
            return
        
        conn = sqlite3.connect('computer_club.db')
        cursor = conn.cursor()
        cursor.execute("SELECT quantity FROM Rooms WHERE id=?", (room_id,))
        quantity = cursor.fetchone()[0]
        conn.close()
        
        for i in range(quantity):
            btn = ttk.Button(self.computers_frame, text=str(i+1), 
                            style='Red.TButton' if self.isComputerBooked(room_id, i+1) else 'TButton',
                            command=lambda num=i+1: self.bookComputer(room_id, num))
            btn.grid(row=i//6, column=i%6, padx=5, pady=5)

    def isComputerBooked(self, room_id, computer_number):
        conn = sqlite3.connect('computer_club.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT end_time FROM Bookings 
                        WHERE room_id=? AND computer_number=? 
                        AND end_time > datetime('now')''', (room_id, computer_number))
        return bool(cursor.fetchone())

    def bookComputer(self, room_id, computer_number):
        dialog = tk.Toplevel(self)
        dialog.title("Бронирование")
        dialog.geometry("300x200")
        
        main_frame = ttk.Frame(dialog)
        main_frame.pack(pady=20, padx=30, fill='both')
        
        ttk.Label(main_frame, text="Часы брони:").grid(row=0, column=0, pady=5, sticky='w')
        self.hours = ttk.Combobox(main_frame, values=[1, 2, 3, 4, 5], width=5)
        self.hours.grid(row=0, column=1, pady=5)
        
        self.price_label = ttk.Label(main_frame, text="Стоимость: 0.00 руб.")
        self.price_label.grid(row=1, columnspan=2, pady=10)
        
        self.hours.bind("<<ComboboxSelected>>", self.calculatePrice)
        ttk.Button(main_frame, text="Подтвердить", 
                 command=lambda: self.confirmBooking(room_id, computer_number, dialog)
                ).grid(row=2, columnspan=2, pady=15)
        
        self.calculatePrice()

    def calculatePrice(self, event=None):
        try:
            room_id = next(r[0] for r in self.rooms if r[1] == self.room_combo.get())
            hours = int(self.hours.get())
            
            conn = sqlite3.connect('computer_club.db')
            cursor = conn.cursor()
            cursor.execute("SELECT price_per_hour FROM Rooms WHERE id=?", (room_id,))
            price = cursor.fetchone()[0]
            conn.close()
            
            total = hours * price
            self.price_label.config(text=f"Стоимость: {total:.2f} руб.")
        except:
            self.price_label.config(text="Стоимость: 0.00 руб.")

    def confirmBooking(self, room_id, computer_number, dialog):
        try:
            hours = int(self.hours.get())
            start_time = datetime.now()
            end_time = start_time + timedelta(hours=hours)
            
            if self.checkBookingConflict(room_id, computer_number, start_time, end_time):
                messagebox.showerror("Ошибка", "Компьютер уже забронирован на это время")
                return
            
            conn = sqlite3.connect('computer_club.db')
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO Bookings (room_id, computer_number, start_time, end_time)
                            VALUES (?, ?, ?, ?)''', 
                         (room_id, computer_number, start_time, end_time))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Успех", "Бронирование подтверждено")
            dialog.destroy()
            self.showComputers()
            self.generateReport()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка бронирования: {str(e)}")

    def checkBookingConflict(self, room_id, computer_number, start, end):
        conn = sqlite3.connect('computer_club.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM Bookings 
                        WHERE room_id=? AND computer_number=?
                        AND ((start_time BETWEEN ? AND ?) 
                        OR (end_time BETWEEN ? AND ?) 
                        OR (? BETWEEN start_time AND end_time))''',
                     (room_id, computer_number, start, end, start, end, start))
        result = bool(cursor.fetchone())
        conn.close()
        return result

    def generateReport(self):
        try:
            start = self.start_date.get()
            end = self.end_date.get() + " 23:59:59"
            
            conn = sqlite3.connect('computer_club.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    COUNT(*), 
                    SUM((strftime('%s', end_time) - strftime('%s', start_time))/3600.0 * r.price_per_hour)
                FROM Bookings b
                JOIN Rooms r ON b.room_id = r.id
                WHERE b.start_time >= ? AND b.start_time <= ?
            ''', (start, end))
            result = cursor.fetchone()
            total_bookings = result[0] or 0
            total_profit = result[1] or 0.0
            conn.close()
            
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, f"▪ Всего бронирований: {total_bookings}\n")
            self.report_text.insert(tk.END, f"▪ Общая прибыль: {total_profit:.2f} руб.\n\n")
            self.report_text.insert(tk.END, f"Период: {self.start_date.get()} — {self.end_date.get()}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

if __name__ == "__main__":
    app = ComputerClubApp()
    app.mainloop()
