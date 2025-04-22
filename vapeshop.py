import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class VapeShopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Вейп Шоп")
        self.root.geometry("1000x700")
        self.root.configure(bg="#e6f0ff")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#e6f0ff")
        style.configure("TNotebook.Tab", background="#b3d1ff", foreground="#003366", font=("Arial", 12, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#6699cc")])
        style.configure("Treeview", background="#ffffff", foreground="#000000", rowheight=25, fieldbackground="#e6f0ff")
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#cce0ff", foreground="#003366")
        style.configure("TButton", font=("Arial", 11), padding=6, background="#b3d1ff", foreground="#003366")
        style.map("TButton", background=[("active", "#99c2ff")])
        style.configure("TLabel", background="#e6f0ff", font=("Arial", 11))

        self.create_db()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        self.create_order_tab()
        self.create_vapes_tab()
        self.create_liquids_tab()
        self.create_report_tab()

        self.cart = []
        
    def create_db(self):
        self.conn = sqlite3.connect('vapeshop.db')
        self.c = self.conn.cursor()
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS vapes
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT,
                     price REAL,
                     quantity INTEGER)''')
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS liquids
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT,
                     price REAL,
                     flavor TEXT,
                     volume INTEGER,
                     nicotine INTEGER,
                     quantity INTEGER)''')
        
        self.c.execute('''CREATE TABLE IF NOT EXISTS orders
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     product_id INTEGER,
                     product_type TEXT,
                     quantity INTEGER,
                     total REAL,
                     date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        self.conn.commit()
        
    def create_order_tab(self):
        self.order_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.order_frame, text='Заказ')

        self.vapes_tree = ttk.Treeview(self.order_frame, columns=('name', 'price', 'quantity'), show='headings')
        for col in ('name', 'price', 'quantity'):
            self.vapes_tree.heading(col, text=col.capitalize())
            self.vapes_tree.column(col, anchor="center", width=200, stretch=True)
        self.vapes_tree.pack(fill='x', padx=10, pady=5)

        self.add_vape_btn = ttk.Button(self.order_frame, text='Добавить вейп в корзину', command=lambda: self.add_to_cart('vape'))
        self.add_vape_btn.pack(pady=5)

        self.liquids_tree = ttk.Treeview(self.order_frame, columns=('name', 'price', 'flavor', 'quantity'), show='headings')
        for col in ('name', 'price', 'flavor', 'quantity'):
            self.liquids_tree.heading(col, text=col.capitalize())
            self.liquids_tree.column(col, anchor="center", width=200, stretch=True)
        self.liquids_tree.pack(fill='x', padx=10, pady=5)

        self.add_liquid_btn = ttk.Button(self.order_frame, text='Добавить жидкость в корзину', command=lambda: self.add_to_cart('liquid'))
        self.add_liquid_btn.pack(pady=5)

        self.cart_label = ttk.Label(self.order_frame, text='Корзина:')
        self.cart_label.pack(anchor='w', padx=10, pady=5)

        self.cart_combo = ttk.Combobox(self.order_frame, state='readonly')
        self.cart_combo.pack(fill='x', padx=10, pady=5)

        self.total_label = ttk.Label(self.order_frame, text='Итого: 0 руб')
        self.total_label.pack(anchor='w', padx=10, pady=5)

        self.checkout_btn = ttk.Button(self.order_frame, text='Оформить заказ', command=self.checkout)
        self.checkout_btn.pack(pady=10)

        self.update_order_trees()
        
    def create_vapes_tab(self):
        self.vapes_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.vapes_tab, text='Вейпы')

        fields = [('Название:', 0), ('Цена:', 1), ('Количество:', 2)]
        self.vape_entries = {}
        for label, row in fields:
            ttk.Label(self.vapes_tab, text=label).grid(row=row, column=0, sticky='e', padx=10, pady=5)
            entry = ttk.Entry(self.vapes_tab)
            entry.grid(row=row, column=1, sticky='ew', padx=10)
            self.vape_entries[label] = entry
        self.vapes_tab.grid_columnconfigure(1, weight=1)

        self.add_vape_btn = ttk.Button(self.vapes_tab, text='Добавить', command=self.add_vape)
        self.add_vape_btn.grid(row=3, column=0, pady=10)
        self.update_vape_btn = ttk.Button(self.vapes_tab, text='Изменить', command=self.update_vape)
        self.update_vape_btn.grid(row=3, column=1, pady=10)
        self.delete_vape_btn = ttk.Button(self.vapes_tab, text='Удалить', command=self.delete_vape)
        self.delete_vape_btn.grid(row=3, column=2, pady=10)

        self.vapes_list_tree = ttk.Treeview(self.vapes_tab, columns=('id', 'name', 'price', 'quantity'), show='headings')
        for col in ('id', 'name', 'price', 'quantity'):
            self.vapes_list_tree.heading(col, text=col.upper())
            self.vapes_list_tree.column(col, anchor='center', stretch=True)
        self.vapes_list_tree.grid(row=4, column=0, columnspan=3, sticky='nsew', padx=10, pady=10)
        self.vapes_tab.grid_rowconfigure(4, weight=1)
        self.vapes_tab.grid_columnconfigure(2, weight=1)

        self.vapes_list_tree.bind('<<TreeviewSelect>>', self.select_vape)

        self.update_vapes_list()

    def create_liquids_tab(self):
        self.liquids_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.liquids_tab, text='Жидкости')

        labels = ['Название:', 'Цена:', 'Вкус:', 'Объем:', 'Никотин:', 'Количество:']
        self.liquid_entries = {}
        for i, label in enumerate(labels):
            ttk.Label(self.liquids_tab, text=label).grid(row=i, column=0, sticky='e', padx=10, pady=5)
            entry = ttk.Entry(self.liquids_tab)
            entry.grid(row=i, column=1, sticky='ew', padx=10)
            self.liquid_entries[label] = entry
        self.liquids_tab.grid_columnconfigure(1, weight=1)

        self.add_liquid_btn = ttk.Button(self.liquids_tab, text='Добавить', command=self.add_liquid)
        self.add_liquid_btn.grid(row=6, column=0, pady=10)
        self.update_liquid_btn = ttk.Button(self.liquids_tab, text='Изменить', command=self.update_liquid)
        self.update_liquid_btn.grid(row=6, column=1, pady=10)
        self.delete_liquid_btn = ttk.Button(self.liquids_tab, text='Удалить', command=self.delete_liquid)
        self.delete_liquid_btn.grid(row=6, column=2, pady=10)

        self.liquids_list_tree = ttk.Treeview(self.liquids_tab, columns=('id', 'name', 'price', 'flavor', 'volume', 'nicotine', 'quantity'), show='headings')
        for col in ('id', 'name', 'price', 'flavor', 'volume', 'nicotine', 'quantity'):
            self.liquids_list_tree.heading(col, text=col.upper())
            self.liquids_list_tree.column(col, anchor='center', stretch=True)
        self.liquids_list_tree.grid(row=7, column=0, columnspan=3, sticky='nsew', padx=10, pady=10)
        self.liquids_tab.grid_rowconfigure(7, weight=1)
        self.liquids_tab.grid_columnconfigure(2, weight=1)

        self.liquids_list_tree.bind('<<TreeviewSelect>>', self.select_liquid)

        self.update_liquids_list()

    def create_report_tab(self):
        self.report_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.report_tab, text='Отчет')

        self.report_text = tk.Text(self.report_tab, bg="#f0f8ff", fg="#000066", font=("Courier", 12))
        self.report_text.pack(fill='both', expand=True, padx=10, pady=10)

        self.generate_report_btn = ttk.Button(self.report_tab, text='Сгенерировать отчет', command=self.generate_report)
        self.generate_report_btn.pack(pady=10)
        
    def update_order_trees(self):
        for row in self.vapes_tree.get_children():
            self.vapes_tree.delete(row)
        self.c.execute("SELECT name, price, quantity FROM vapes")
        for row in self.c.fetchall():
            self.vapes_tree.insert('', 'end', values=row)
            
        for row in self.liquids_tree.get_children():
            self.liquids_tree.delete(row)
        self.c.execute("SELECT name, price, flavor, quantity FROM liquids")
        for row in self.c.fetchall():
            self.liquids_tree.insert('', 'end', values=row)
            
    def add_to_cart(self, product_type):
        tree = self.vapes_tree if product_type == 'vape' else self.liquids_tree
        selected = tree.selection()
        if not selected:
            return
        item = tree.item(selected[0])['values']
        name = item[0]
        price = item[1]
        self.cart.append({'name': name, 'price': price, 'type': product_type})
        self.cart_combo['values'] = [f"{item['name']} - {item['price']} руб" for item in self.cart]
        total = sum(item['price'] for item in self.cart)
        self.total_label.config(text=f'Итого: {total} руб')
        
    def checkout(self):
        if not self.cart:
            messagebox.showwarning('Ошибка', 'Корзина пуста')
            return
        
        try:
            for item in self.cart:
                if item['type'] == 'vape':
                    self.c.execute("UPDATE vapes SET quantity = quantity - 1 WHERE name = ?", (item['name'],))
                    self.c.execute("INSERT INTO orders (product_id, product_type, quantity, total) VALUES ((SELECT id FROM vapes WHERE name = ?), 'vape', 1, ?)", 
                                 (item['name'], item['price']))
                else:
                    self.c.execute("UPDATE liquids SET quantity = quantity - 1 WHERE name = ?", (item['name'],))
                    self.c.execute("INSERT INTO orders (product_id, product_type, quantity, total) VALUES ((SELECT id FROM liquids WHERE name = ?), 'liquid', 1, ?)", 
                                 (item['name'], item['price']))
            self.conn.commit()
            self.cart = []
            self.cart_combo.set('')
            self.total_label.config(text='Итого: 0 руб')
            self.update_order_trees()
            self.update_vapes_list()
            self.update_liquids_list()
            messagebox.showinfo('Успех', 'Заказ оформлен')
        except Exception as e:
            messagebox.showerror('Ошибка', str(e))
            
    def update_vapes_list(self):
        for row in self.vapes_list_tree.get_children():
            self.vapes_list_tree.delete(row)
        self.c.execute("SELECT * FROM vapes")
        for row in self.c.fetchall():
            self.vapes_list_tree.insert('', 'end', values=row)
            
    def select_vape(self, event):
        selected = self.vapes_list_tree.selection()
        if selected:
            item = self.vapes_list_tree.item(selected[0])['values']
            self.vape_entries['Название:'].delete(0, 'end')
            self.vape_entries['Название:'].insert(0, item[1])
            self.vape_entries['Цена:'].delete(0, 'end')
            self.vape_entries['Цена:'].insert(0, item[2])
            self.vape_entries['Количество:'].delete(0, 'end')
            self.vape_entries['Количество:'].insert(0, item[3])
            
    def add_vape(self):
        name = self.vape_entries['Название:'].get()
        price = self.vape_entries['Цена:'].get()
        quantity = self.vape_entries['Количество:'].get()
        if not all([name, price, quantity]):
            return
        self.c.execute("INSERT INTO vapes (name, price, quantity) VALUES (?, ?, ?)", 
                     (name, float(price), int(quantity)))
        self.conn.commit()
        self.update_vapes_list()
        self.update_order_trees()
        
    def update_vape(self):
        selected = self.vapes_list_tree.selection()
        if not selected:
            return
        item = self.vapes_list_tree.item(selected[0])['values']
        name = self.vape_entries['Название:'].get()
        price = self.vape_entries['Цена:'].get()
        quantity = self.vape_entries['Количество:'].get()
        if not all([name, price, quantity]):
            return
        self.c.execute("UPDATE vapes SET name=?, price=?, quantity=? WHERE id=?", 
                     (name, float(price), int(quantity), item[0]))
        self.conn.commit()
        self.update_vapes_list()
        self.update_order_trees()
        
    def delete_vape(self):
        selected = self.vapes_list_tree.selection()
        if not selected:
            return
        item = self.vapes_list_tree.item(selected[0])['values']
        self.c.execute("DELETE FROM vapes WHERE id=?", (item[0],))
        self.conn.commit()
        self.update_vapes_list()
        self.update_order_trees()
        
    def update_liquids_list(self):
        for row in self.liquids_list_tree.get_children():
            self.liquids_list_tree.delete(row)
        self.c.execute("SELECT * FROM liquids")
        for row in self.c.fetchall():
            self.liquids_list_tree.insert('', 'end', values=row)
            
    def select_liquid(self, event):
        selected = self.liquids_list_tree.selection()
        if selected:
            item = self.liquids_list_tree.item(selected[0])['values']
            self.liquid_entries['Название:'].delete(0, 'end')
            self.liquid_entries['Название:'].insert(0, item[1])
            self.liquid_entries['Цена:'].delete(0, 'end')
            self.liquid_entries['Цена:'].insert(0, item[2])
            self.liquid_entries['Вкус:'].delete(0, 'end')
            self.liquid_entries['Вкус:'].insert(0, item[3])
            self.liquid_entries['Объем:'].delete(0, 'end')
            self.liquid_entries['Объем:'].insert(0, item[4])
            self.liquid_entries['Никотин:'].delete(0, 'end')
            self.liquid_entries['Никотин:'].insert(0, item[5])
            self.liquid_entries['Количество:'].delete(0, 'end')
            self.liquid_entries['Количество:'].insert(0, item[6])
            
    def add_liquid(self):
        name = self.liquid_entries['Название:'].get()
        price = self.liquid_entries['Цена:'].get()
        flavor = self.liquid_entries['Вкус:'].get()
        volume = self.liquid_entries['Объем:'].get()
        nicotine = self.liquid_entries['Никотин:'].get()
        quantity = self.liquid_entries['Количество:'].get()
        if not all([name, price, flavor, volume, nicotine, quantity]):
            return
        self.c.execute("INSERT INTO liquids (name, price, flavor, volume, nicotine, quantity) VALUES (?, ?, ?, ?, ?, ?)", 
                     (name, float(price), flavor, int(volume), int(nicotine), int(quantity)))
        self.conn.commit()
        self.update_liquids_list()
        self.update_order_trees()
        
    def update_liquid(self):
        selected = self.liquids_list_tree.selection()
        if not selected:
            return
        item = self.liquids_list_tree.item(selected[0])['values']
        name = self.liquid_name.get()
        price = self.liquid_price.get()
        flavor = self.liquid_flavor.get()
        volume = self.liquid_volume.get()
        nicotine = self.liquid_nicotine.get()
        quantity = self.liquid_quantity.get()
        if not all([name, price, flavor, volume, nicotine, quantity]):
            return
        self.c.execute("UPDATE liquids SET name=?, price=?, flavor=?, volume=?, nicotine=?, quantity=? WHERE id=?", 
                     (name, float(price), flavor, int(volume), int(nicotine), int(quantity), item[0]))
        self.conn.commit()
        self.update_liquids_list()
        self.update_order_trees()
        
    def delete_liquid(self):
        selected = self.liquids_list_tree.selection()
        if not selected:
            return
        item = self.liquids_list_tree.item(selected[0])['values']
        self.c.execute("DELETE FROM liquids WHERE id=?", (item[0],))
        self.conn.commit()
        self.update_liquids_list()
        self.update_order_trees()
        
    def generate_report(self):
        self.c.execute("SELECT product_type, COUNT(*), SUM(total) FROM orders GROUP BY product_type")
        sales = self.c.fetchall()
        
        self.c.execute("""SELECT v.name, COUNT(*) as cnt 
                        FROM orders o 
                        JOIN vapes v ON o.product_id = v.id 
                        WHERE o.product_type = 'vape' 
                        GROUP BY v.name 
                        ORDER BY cnt DESC 
                        LIMIT 1""")
        top_vape = self.c.fetchone()
        
        self.c.execute("""SELECT l.name, COUNT(*) as cnt 
                        FROM orders o 
                        JOIN liquids l ON o.product_id = l.id 
                        WHERE o.product_type = 'liquid' 
                        GROUP BY l.name 
                        ORDER BY cnt DESC 
                        LIMIT 1""")
        top_liquid = self.c.fetchone()
        
        report = "Отчет о продажах:\n\n"
        for line in sales:
            report += f"{line[0]}: {line[1]} шт. на сумму {line[2]} руб\n"
        
        report += "\nСамый популярный вейп: "
        report += f"{top_vape[0]} ({top_vape[1]} шт)\n" if top_vape else "нет данных\n"
        
        report += "Самая популярная жидкость: "
        report += f"{top_liquid[0]} ({top_liquid[1]} шт)" if top_liquid else "нет данных"
        
        self.report_text.delete(1.0, 'end')
        self.report_text.insert(1.0, report)

if __name__ == "__main__":
    root = tk.Tk()
    app = VapeShopApp(root)
    root.mainloop()
