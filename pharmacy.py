import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
import sqlite3

class PharmacyApplication:
    def __init__(self, root_window):
        self.root_window = root_window
        self.root_window.title("Аптека - Система управления")
        self.configure_styles()
        self.initialize_database_connection()
        
        self.application_notebook = ttk.Notebook(self.root_window)
        self.application_notebook.pack(padx=15, pady=15, fill='both', expand=True)

        self.medicines_tab = ttk.Frame(self.application_notebook)
        self.sales_management_tab = ttk.Frame(self.application_notebook)
        self.sales_history_tab = ttk.Frame(self.application_notebook)

        self.application_notebook.add(self.medicines_tab, text='Учёт лекарственных средств')
        self.application_notebook.add(self.sales_management_tab, text='Управление продажами')
        self.application_notebook.add(self.sales_history_tab, text='История транзакций')

        self.create_medicines_management_interface()
        self.create_sales_management_interface()
        self.create_sales_history_interface()
        self.refresh_medicines_list()

    def configure_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='white')
        self.style.configure('TLabel', background='white', foreground='#2D5D2E')
        self.style.configure('TButton', background='#4CAF50', foreground='white', bordercolor='#4CAF50')
        self.style.map('TButton', background=[('active', '#45A049')])
        self.style.configure('Treeview.Heading', background='#4CAF50', foreground='white')
        self.style.configure('Treeview', fieldbackground='white', foreground='#2D5D2E')

    def initialize_database_connection(self):
        self.database_connection = sqlite3.connect('pharmacy_database.db')
        self.database_cursor = self.database_connection.cursor()
        
        self.database_cursor.execute('''CREATE TABLE IF NOT EXISTS medicines_inventory (
                                      medicine_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                      medicine_name TEXT NOT NULL,
                                      medicine_manufacturer TEXT NOT NULL,
                                      expiration_date TEXT NOT NULL,
                                      unit_price REAL NOT NULL,
                                      stock_quantity INTEGER NOT NULL)''')
        
        self.database_cursor.execute('''CREATE TABLE IF NOT EXISTS sales_records (
                                      transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                      medicine_identifier INTEGER NOT NULL,
                                      sold_quantity INTEGER NOT NULL,
                                      transaction_date TEXT NOT NULL,
                                      total_amount REAL NOT NULL,
                                      FOREIGN KEY(medicine_identifier) REFERENCES medicines_inventory(medicine_id))''')
        
        self.database_connection.commit()

    def create_medicines_management_interface(self):
        input_fields_container = ttk.Frame(self.medicines_tab)
        input_fields_container.pack(pady=12)

        field_labels = ['Название препарата:', 'Производитель:', 'Дата окончания срока:', 'Цена за единицу:', 'Количество на складе:']
        self.medicine_input_fields = {}
        
        for index, label_text in enumerate(field_labels):
            field_label = ttk.Label(input_fields_container, text=label_text)
            field_label.grid(row=index, column=0, padx=6, pady=6, sticky='e')
            
            if label_text == 'Дата окончания срока:':
                input_field = DateEntry(input_fields_container, date_pattern='yyyy-mm-dd')
            else:
                input_field = ttk.Entry(input_fields_container)
            
            input_field.grid(row=index, column=1, padx=6, pady=6)
            self.medicine_input_fields[label_text] = input_field

        buttons_container = ttk.Frame(self.medicines_tab)
        buttons_container.pack(pady=12)
        
        ttk.Button(buttons_container, text="Добавить запись", command=self.add_new_medicine).pack(side='left', padx=6)
        ttk.Button(buttons_container, text="Обновить запись", command=self.update_existing_medicine).pack(side='left', padx=6)
        ttk.Button(buttons_container, text="Удалить запись", command=self.delete_existing_medicine).pack(side='left', padx=6)

        columns = ('ID', 'Наименование', 'Производитель', 'Срок годности', 'Цена', 'Остаток')
        self.medicines_treeview = ttk.Treeview(self.medicines_tab, columns=columns, show='headings', height=12)
        
        for column in columns:
            self.medicines_treeview.heading(column, text=column)
            self.medicines_treeview.column(column, width=120)
            
        self.medicines_treeview.pack(padx=12, pady=12, fill='both', expand=True)
        self.medicines_treeview.bind('<<TreeviewSelect>>', self.load_selected_medicine_data)

    def create_sales_management_interface(self):
        sales_container = ttk.Frame(self.sales_management_tab)
        sales_container.pack(pady=12, fill='both', expand=True)

        ttk.Label(sales_container, text="Выберите препарат:").grid(row=0, column=0, padx=6, pady=6)
        self.medicine_selection_combobox = ttk.Combobox(sales_container, state='readonly')
        self.medicine_selection_combobox.grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(sales_container, text="Количество для продажи:").grid(row=1, column=0, padx=6, pady=6)
        self.quantity_selection_spinbox = ttk.Spinbox(sales_container, from_=1, to=1000)
        self.quantity_selection_spinbox.grid(row=1, column=1, padx=6, pady=6)

        ttk.Label(sales_container, text="Дата совершения продажи:").grid(row=2, column=0, padx=6, pady=6)
        self.transaction_date_picker = DateEntry(sales_container, date_pattern='yyyy-mm-dd')
        self.transaction_date_picker.grid(row=2, column=1, padx=6, pady=6)

        ttk.Button(sales_container, text="Зафиксировать продажу", 
                 command=self.process_sale_transaction).grid(row=3, column=0, columnspan=2, pady=12)

    def create_sales_history_interface(self):
        filter_container = ttk.Frame(self.sales_history_tab)
        filter_container.pack(pady=12)
        
        ttk.Label(filter_container, text="Начальная дата:").pack(side='left')
        self.history_start_date = DateEntry(filter_container, date_pattern='yyyy-mm-dd')
        self.history_start_date.pack(side='left', padx=6)
        
        ttk.Label(filter_container, text="Конечная дата:").pack(side='left', padx=(12, 0))
        self.history_end_date = DateEntry(filter_container, date_pattern='yyyy-mm-dd')
        self.history_end_date.pack(side='left', padx=6)
        
        ttk.Button(filter_container, text="Обновить историю", 
                 command=self.refresh_sales_history).pack(side='left', padx=12)

        columns = ('ID', 'Препарат', 'Продано', 'Сумма', 'Дата операции')
        self.sales_history_treeview = ttk.Treeview(self.sales_history_tab, columns=columns, show='headings', height=15)
        
        for column in columns:
            self.sales_history_treeview.heading(column, text=column)
            self.sales_history_treeview.column(column, width=130)
            
        self.sales_history_treeview.pack(padx=12, pady=12, fill='both', expand=True)
        self.refresh_sales_history()

    def add_new_medicine(self):
        input_values = [
            self.medicine_input_fields['Название препарата:'].get(),
            self.medicine_input_fields['Производитель:'].get(),
            self.medicine_input_fields['Дата окончания срока:'].get(),
            self.medicine_input_fields['Цена за единицу:'].get(),
            self.medicine_input_fields['Количество на складе:'].get()
        ]
        
        if not all(input_values):
            messagebox.showerror("Ошибка ввода", "Необходимо заполнить все поля!")
            return
            
        try:
            self.database_cursor.execute('''INSERT INTO medicines_inventory 
                                        (medicine_name, medicine_manufacturer, expiration_date, unit_price, stock_quantity)
                                        VALUES (?, ?, ?, ?, ?)''', input_values)
            self.database_connection.commit()
            self.refresh_medicines_list()
            self.clear_input_fields()
        except Exception as error:
            messagebox.showerror("Ошибка базы данных", f"Ошибка: {str(error)}")

    def update_existing_medicine(self):
        selected_items = self.medicines_treeview.selection()
        if not selected_items:
            return
            
        medicine_identifier = self.medicines_treeview.item(selected_items[0], 'values')[0]
        updated_values = [
            self.medicine_input_fields['Название препарата:'].get(),
            self.medicine_input_fields['Производитель:'].get(),
            self.medicine_input_fields['Дата окончания срока:'].get(),
            self.medicine_input_fields['Цена за единицу:'].get(),
            self.medicine_input_fields['Количество на складе:'].get(),
            medicine_identifier
        ]
                
        try:
            self.database_cursor.execute('''UPDATE medicines_inventory SET 
                                        medicine_name=?, medicine_manufacturer=?, expiration_date=?, unit_price=?, stock_quantity=?
                                        WHERE medicine_id=?''', updated_values)
            self.database_connection.commit()
            self.refresh_medicines_list()
        except Exception as error:
            messagebox.showerror("Ошибка обновления", f"Ошибка: {str(error)}")

    def delete_existing_medicine(self):
        selected_items = self.medicines_treeview.selection()
        if not selected_items:
            return
            
        medicine_identifier = self.medicines_treeview.item(selected_items[0], 'values')[0]
        try:
            self.database_cursor.execute("DELETE FROM medicines_inventory WHERE medicine_id=?", (medicine_identifier,))
            self.database_connection.commit()
            self.refresh_medicines_list()
        except Exception as error:
            messagebox.showerror("Ошибка удаления", f"Ошибка: {str(error)}")

    def process_sale_transaction(self):
        selected_medicine = self.medicine_selection_combobox.get()
        transaction_quantity = self.quantity_selection_spinbox.get()
        transaction_date = self.transaction_date_picker.get()
        
        if not selected_medicine or not transaction_quantity:
            messagebox.showerror("Ошибка операции", "Укажите препарат и количество")
            return
            
        try:
            self.database_cursor.execute('''SELECT medicine_id, unit_price, stock_quantity 
                                         FROM medicines_inventory 
                                         WHERE medicine_name=?''', (selected_medicine,))
            medicine_data = self.database_cursor.fetchone()
            
            if not medicine_data:
                messagebox.showerror("Ошибка поиска", "Препарат не найден")
                return
                
            medicine_identifier, unit_price, current_stock = medicine_data
            transaction_quantity = int(transaction_quantity)
            
            if transaction_quantity > current_stock:
                messagebox.showerror("Ошибка операции", "Недостаточный остаток на складе")
                return
                
            updated_stock = current_stock - transaction_quantity
            self.database_cursor.execute('''UPDATE medicines_inventory 
                                         SET stock_quantity=? 
                                         WHERE medicine_id=?''', (updated_stock, medicine_identifier))
            
            total_transaction_amount = unit_price * transaction_quantity
            self.database_cursor.execute('''INSERT INTO sales_records 
                                         (medicine_identifier, sold_quantity, transaction_date, total_amount)
                                         VALUES (?, ?, ?, ?)''', 
                                         (medicine_identifier, transaction_quantity, transaction_date, total_transaction_amount))
                                         
            self.database_connection.commit()
            self.refresh_medicines_list()
            self.refresh_sales_history()
            messagebox.showinfo("Операция успешна", "Продажа зарегистрирована")
            
        except Exception as error:
            messagebox.showerror("Ошибка транзакции", f"Ошибка: {str(error)}")

    def refresh_medicines_list(self):
        self.medicines_treeview.delete(*self.medicines_treeview.get_children())
        self.database_cursor.execute('''SELECT * FROM medicines_inventory''')
        for record in self.database_cursor.fetchall():
            self.medicines_treeview.insert('', 'end', values=record)
        
        self.database_cursor.execute('''SELECT medicine_name FROM medicines_inventory''')
        medicine_names = [record[0] for record in self.database_cursor.fetchall()]
        self.medicine_selection_combobox['values'] = medicine_names

    def refresh_sales_history(self):
        self.sales_history_treeview.delete(*self.sales_history_treeview.get_children())
        start_date_filter = self.history_start_date.get()
        end_date_filter = self.history_end_date.get()
        
        history_query = '''SELECT sales_records.transaction_id, medicines_inventory.medicine_name, 
                         sales_records.sold_quantity, sales_records.total_amount, 
                         sales_records.transaction_date 
                         FROM sales_records 
                         JOIN medicines_inventory 
                         ON sales_records.medicine_identifier = medicines_inventory.medicine_id
                         WHERE sales_records.transaction_date BETWEEN ? AND ?'''
                         
        self.database_cursor.execute(history_query, (start_date_filter, end_date_filter))
        for historical_record in self.database_cursor.fetchall():
            self.sales_history_treeview.insert('', 'end', values=historical_record)

    def load_selected_medicine_data(self, event):
        selected_items = self.medicines_treeview.selection()
        if not selected_items:
            return
            
        medicine_values = self.medicines_treeview.item(selected_items[0], 'values')
        field_order = ['Название препарата:', 'Производитель:', 'Дата окончания срока:', 'Цена за единицу:', 'Количество на складе:']
        for field_name, value in zip(field_order, medicine_values[1:]):
            self.medicine_input_fields[field_name].delete(0, 'end')
            self.medicine_input_fields[field_name].insert(0, value)

    def clear_input_fields(self):
        for input_field in self.medicine_input_fields.values():
            if isinstance(input_field, DateEntry):
                input_field.set_date(None)
            else:
                input_field.delete(0, 'end')

    def __del__(self):
        self.database_connection.close()

if __name__ == "__main__":
    main_window = tk.Tk()
    application_instance = PharmacyApplication(main_window)
    main_window.mainloop()