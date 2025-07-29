import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from PIL import Image, ImageTk
import os

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Информационная система")
        self.root.minsize(800, 500)
        self.root.geometry("1000x600")
        self.db = Database()
        self.current_user = None

        # Стили
        self.primary_bg = "#FFFFFF"
        self.secondary_bg = "#D2DFFF"
        self.accent_color = "#355CBD"
        self.font_family = "Candara"
        self.title_font = (self.font_family, 18, "bold")
        self.label_font = (self.font_family, 12)
        self.card_font = (self.font_family, 13)
        self.card_title_font = (self.font_family, 15, "bold")

        # Установка иконки приложения
        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

        # Грид-адаптивность
        self.root.grid_rowconfigure(0, weight=0)  # Шапка фиксирована
        self.root.grid_rowconfigure(1, weight=1)  # Контент адаптивен
        self.root.grid_columnconfigure(0, weight=1)

        self.setup_login_frame()

    def setup_login_frame(self):
        self.login_frame = tk.Frame(self.root, bg=self.primary_bg, padx=20, pady=20)
        self.login_frame.grid(row=1, column=0, sticky="nsew")
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Заголовок
        header = tk.Frame(self.root, bg=self.secondary_bg)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        tk.Label(header, text="Вход в систему", font=self.title_font, bg=self.secondary_bg, fg=self.accent_color).pack(anchor="center", pady=8)

        tk.Label(self.login_frame, text="Логин:", font=self.label_font, bg=self.primary_bg).grid(row=0, column=0, pady=5, sticky=tk.E)
        self.username_entry = ttk.Entry(self.login_frame, font=self.label_font)
        self.username_entry.grid(row=0, column=1, pady=5, sticky="ew")

        tk.Label(self.login_frame, text="Пароль:", font=self.label_font, bg=self.primary_bg).grid(row=1, column=0, pady=5, sticky=tk.E)
        self.password_entry = ttk.Entry(self.login_frame, show="*", font=self.label_font)
        self.password_entry.grid(row=1, column=1, pady=5, sticky="ew")

        self.login_frame.grid_columnconfigure(1, weight=1)

        login_btn = tk.Button(self.login_frame, text="Войти", command=self.login, font=self.label_font, bg=self.accent_color, fg="white", activebackground=self.secondary_bg)
        login_btn.grid(row=2, column=0, columnspan=2, pady=15, ipadx=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        query = """
        SELECT u.UserID, u.Username, r.RoleName 
        FROM Users u 
        JOIN Roles r ON u.RoleID = r.RoleID 
        WHERE Username = ? AND Password = ?
        """
        result = self.db.execute_query(query, (username, password))
        if result:
            self.current_user = {
                'id': result[0][0],
                'username': result[0][1],
                'role': result[0][2]
            }
            self.login_frame.destroy()
            self.setup_main_interface()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

    def setup_main_interface(self):
        self.root.configure(bg=self.primary_bg)
        # Удаляем все виджеты кроме меню
        for widget in self.root.winfo_children():
            widget.destroy()

        # --- Шапка ---
        self.header_frame = tk.Frame(self.root, bg=self.secondary_bg)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=0)
        self.header_frame.grid_columnconfigure(1, weight=1)
        self.header_frame.grid_columnconfigure(2, weight=0)

        # Логотип
        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        if os.path.exists(logo_path):
            img = Image.open(logo_path)
            img = img.resize((40, 40), Image.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img)
            tk.Label(self.header_frame, image=self.logo_img, bg=self.secondary_bg).grid(row=0, column=0, padx=(10, 10), pady=5, sticky="w")

        # Главная надпись
        tk.Label(self.header_frame, text="Главное меню", font=self.title_font, bg=self.secondary_bg, fg=self.accent_color).grid(row=0, column=1, sticky="w", pady=5)

        # Имя пользователя и роль
        user_info = f"{self.current_user['username']} ({self.current_user['role']})"
        tk.Label(self.header_frame, text=user_info, font=self.label_font, bg=self.secondary_bg, fg=self.accent_color).grid(row=0, column=2, sticky="e", padx=(0, 15))

        # --- Меню ---
        self.menu_frame = tk.Frame(self.root, bg=self.secondary_bg, padx=10, pady=5)
        self.menu_frame.grid(row=1, column=0, sticky="ew")
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        btns = [
            ("Материалы", self.show_materials),
            ("Продукция", self.show_products),
            ("Цеха", self.show_workshops),
        ]
        for idx, (text, cmd) in enumerate(btns):
            tk.Button(self.menu_frame, text=text, command=cmd, font=self.label_font, bg=self.accent_color, fg="white", activebackground=self.secondary_bg).grid(row=0, column=idx, padx=5, pady=2, ipadx=5, sticky="ew")

        if self.current_user['role'] == 'Администратор':
            tk.Button(self.menu_frame, text="Пользователи", command=self.show_users, font=self.label_font, bg=self.accent_color, fg="white", activebackground=self.secondary_bg).grid(row=0, column=len(btns), padx=5, pady=2, ipadx=5, sticky="ew")

        for i in range(len(btns) + 1):
            self.menu_frame.grid_columnconfigure(i, weight=1)

    def clear_main_area(self):
        # Удаляет все виджеты кроме шапки и меню
        for widget in self.root.winfo_children():
            if widget not in (self.header_frame, self.menu_frame):
                widget.destroy()

    def show_materials(self):
        self.clear_main_area()
        frame = tk.Frame(self.root, bg=self.primary_bg, padx=20, pady=20)
        frame.grid(row=2, column=0, sticky="nsew")
        tk.Label(frame, text="Материалы", font=self.title_font, bg=self.primary_bg, fg=self.accent_color).grid(row=0, column=0, sticky="w", pady=(0, 15))

        # --- Поиск и сортировка ---
        search_frame = tk.Frame(frame, bg=self.primary_bg)
        search_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        tk.Label(search_frame, text="Поиск по типу:", font=self.label_font, bg=self.primary_bg).pack(side="left")
        search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=search_var, font=self.label_font, width=20).pack(side="left", padx=5)
        tk.Label(search_frame, text="Сортировка:", font=self.label_font, bg=self.primary_bg).pack(side="left", padx=(20,0))
        sort_options = ["Без сортировки", "По возрастанию % потерь", "По убыванию % потерь"]
        sort_var = tk.StringVar(value=sort_options[0])
        ttk.Combobox(search_frame, values=sort_options, textvariable=sort_var, state="readonly", width=22).pack(side="left", padx=5)
        def reload():
            self.show_materials_filtered(search_var.get(), sort_var.get(), parent=frame)
        tk.Button(search_frame, text="Поиск", font=self.label_font, command=reload).pack(side="left", padx=10)

        add_btn = tk.Button(frame, text="Добавить материал", font=self.label_font, bg=self.accent_color, fg="white",
                            command=self.add_material_dialog)
        add_btn.grid(row=2, column=1, sticky="e", padx=10)

        self.show_materials_filtered("", "Без сортировки", parent=frame)

    def show_materials_filtered(self, search, sort_mode, parent=None):
        # Удалить старые карточки
        if parent:
            for widget in parent.pack_slaves():
                if isinstance(widget, tk.Frame) and widget not in [parent.children.get('!frame'), parent.children.get('!button')]:
                    widget.destroy()
        frame = parent if parent else self.root

        # --- Скроллируемая область ---
        canvas = tk.Canvas(frame, bg=self.primary_bg, highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.primary_bg)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=3, column=0, sticky="nsew")
        scrollbar.grid(row=3, column=1, sticky="ns")
        frame.grid_rowconfigure(3, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Сортировка
        order_clause = ""
        if sort_mode == "По возрастанию % потерь":
            order_clause = "ORDER BY [Процент потерь сырья] ASC"
        elif sort_mode == "По убыванию % потерь":
            order_clause = "ORDER BY [Процент потерь сырья] DESC"

        query = f"""
        SELECT ID, [Тип материала], [Процент потерь сырья]
        FROM Material_type_import
        WHERE (? = '' OR [Тип материала] LIKE ?)
        {order_clause}
        """
        params = (search, f"%{search}%")
        rows = self.db.execute_query(query, params)

        if not rows:
            tk.Label(scrollable_frame, text="Нет данных", font=self.label_font, bg=self.primary_bg).pack()
            return

        for material in rows:
            card = tk.Frame(scrollable_frame, bg=self.primary_bg, highlightbackground="#888", highlightthickness=1, bd=0)
            card.pack(fill="x", pady=10, padx=5)
            left = tk.Frame(card, bg=self.primary_bg)
            left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            right = tk.Frame(card, bg=self.primary_bg)
            right.pack(side="right", fill="y", padx=10, pady=10)

            tk.Label(left, text=f"ID: {material[0]}", font=self.card_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            tk.Label(left, text=f"Тип материала: {material[1]}", font=self.card_title_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            tk.Label(left, text=f"Процент потерь сырья: {material[2]}", font=self.card_font, bg=self.primary_bg, anchor="w").pack(anchor="w")

            tk.Button(right, text="Редактировать", font=self.label_font, bg="#888", fg="white",
                      command=lambda m=material: self.edit_material_dialog(m)).pack(anchor="e", pady=(0, 5))

            def confirm_and_delete_material(mid=material[0]):
                if messagebox.askyesno("Подтвердите", "Удалить материал?"):
                    self.db.execute_query("DELETE FROM Material_type_import WHERE ID=?", (mid,))
                    self.show_materials()
            tk.Button(right, text="Удалить", font=self.label_font, bg="#c0392b", fg="white",
                      command=confirm_and_delete_material).pack(anchor="e", pady=(0, 5))

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        frame.grid_rowconfigure(3, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig("all", width=e.width))

    def add_material_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить материал")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.primary_bg)

        tk.Label(dialog, text="ID", font=self.label_font, bg=self.primary_bg).grid(row=0, column=0, sticky="e", pady=3, padx=5)
        id_var = tk.StringVar()
        tk.Entry(dialog, font=self.label_font, textvariable=id_var).grid(row=0, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Тип материала", font=self.label_font, bg=self.primary_bg).grid(row=1, column=0, sticky="e", pady=3, padx=5)
        type_var = tk.StringVar()
        tk.Entry(dialog, font=self.label_font, textvariable=type_var).grid(row=1, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Процент потерь сырья", font=self.label_font, bg=self.primary_bg).grid(row=2, column=0, sticky="e", pady=3, padx=5)
        loss_var = tk.StringVar()
        tk.Entry(dialog, font=self.label_font, textvariable=loss_var).grid(row=2, column=1, pady=3, padx=5, sticky="ew")

        dialog.grid_columnconfigure(1, weight=1)

        def save():
            try:
                self.db.execute_query(
                    "INSERT INTO Material_type_import (ID, [Тип материала], [Процент потерь сырья]) VALUES (?, ?, ?)",
                    (id_var.get(), type_var.get(), loss_var.get())
                )
                messagebox.showinfo("Успех", "Материал добавлен")
                dialog.destroy()
                self.show_materials()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка добавления: {e}")

        tk.Button(dialog, text="Сохранить", font=self.label_font, bg=self.accent_color, fg="white", command=save).grid(row=3, column=0, columnspan=2, pady=10)

    def edit_material_dialog(self, values):
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать материал")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.primary_bg)

        tk.Label(dialog, text="ID", font=self.label_font, bg=self.primary_bg).grid(row=0, column=0, sticky="e", pady=3, padx=5)
        id_var = tk.StringVar(value=values[0])
        tk.Entry(dialog, font=self.label_font, textvariable=id_var, state="readonly").grid(row=0, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Тип материала", font=self.label_font, bg=self.primary_bg).grid(row=1, column=0, sticky="e", pady=3, padx=5)
        type_var = tk.StringVar(value=values[1])
        tk.Entry(dialog, font=self.label_font, textvariable=type_var).grid(row=1, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Процент потерь сырья", font=self.label_font, bg=self.primary_bg).grid(row=2, column=0, sticky="e", pady=3, padx=5)
        loss_var = tk.StringVar(value=values[2])
        tk.Entry(dialog, font=self.label_font, textvariable=loss_var).grid(row=2, column=1, pady=3, padx=5, sticky="ew")

        dialog.grid_columnconfigure(1, weight=1)

        def save():
            try:
                self.db.execute_query(
                    "UPDATE Material_type_import SET [Тип материала]=?, [Процент потерь сырья]=? WHERE ID=?",
                    (type_var.get(), loss_var.get(), id_var.get())
                )
                messagebox.showinfo("Успех", "Материал обновлен")
                dialog.destroy()
                self.show_materials()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка обновления: {e}")

        tk.Button(dialog, text="Сохранить", font=self.label_font, bg=self.accent_color, fg="white", command=save).grid(row=3, column=0, columnspan=2, pady=10)

    def show_products(self):
        self.clear_main_area()
        frame = tk.Frame(self.root, bg=self.primary_bg, padx=20, pady=20)
        frame.grid(row=2, column=0, sticky="nsew")
        tk.Label(frame, text="Продукция", font=self.title_font, bg=self.primary_bg, fg=self.accent_color).grid(row=0, column=0, sticky="w", pady=(0, 15))

        # --- Поиск и сортировка ---
        search_frame = tk.Frame(frame, bg=self.primary_bg)
        search_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        tk.Label(search_frame, text="Поиск по наименованию:", font=self.label_font, bg=self.primary_bg).pack(side="left")
        search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=search_var, font=self.label_font, width=20).pack(side="left", padx=5)
        tk.Label(search_frame, text="Сортировка:", font=self.label_font, bg=self.primary_bg).pack(side="left", padx=(20,0))
        sort_options = ["Без сортировки", "По возрастанию цены", "По убыванию цены"]
        sort_var = tk.StringVar(value=sort_options[0])
        ttk.Combobox(search_frame, values=sort_options, textvariable=sort_var, state="readonly", width=22).pack(side="left", padx=5)
        def reload():
            self.show_products_filtered(search_var.get(), sort_var.get(), parent=frame)
        tk.Button(search_frame, text="Поиск", font=self.label_font, command=reload).pack(side="left", padx=10)

        add_btn = tk.Button(frame, text="Добавить продукцию", font=self.label_font, bg=self.accent_color, fg="white",
                            command=self.add_product_dialog)
        add_btn.grid(row=2, column=1, sticky="e", padx=10)

        self.show_products_filtered("", "Без сортировки", parent=frame)

    def show_products_filtered(self, search, sort_mode, parent=None):
        if parent:
            for widget in parent.pack_slaves():
                if isinstance(widget, tk.Frame) and widget not in [parent.children.get('!frame'), parent.children.get('!button')]:
                    widget.destroy()
        frame = parent if parent else self.root

        canvas = tk.Canvas(frame, bg=self.primary_bg, highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.primary_bg)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=3, column=0, sticky="nsew")
        scrollbar.grid(row=3, column=1, sticky="ns")
        frame.grid_rowconfigure(3, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        order_clause = ""
        if sort_mode == "По возрастанию цены":
            order_clause = "ORDER BY p.[Минимальная стоимость для партнера] ASC"
        elif sort_mode == "По убыванию цены":
            order_clause = "ORDER BY p.[Минимальная стоимость для партнера] DESC"

        query = f"""
        SELECT p.ID, pt.[Тип продукции], p.[Наименование продукции], p.Артикул, p.[Минимальная стоимость для партнера], mt.[Тип материала]
        FROM Products_import p
        JOIN Product_type_import pt ON p.[Тип продукции] = pt.ID
        JOIN Material_type_import mt ON p.[Основной материал] = mt.ID
        WHERE (? = '' OR p.[Наименование продукции] LIKE ?)
        {order_clause}
        """
        params = (search, f"%{search}%")
        rows = self.db.execute_query(query, params)

        if not rows:
            tk.Label(scrollable_frame, text="Нет данных", font=self.label_font, bg=self.primary_bg).pack()
            return

        for product in rows:
            # Получаем сумму времени изготовления для продукта
            time_query = """
            SELECT SUM([Время изготовления, ч])
            FROM Product_workshops_import
            WHERE [Наименование продукции]=?
            """
            time_row = self.db.execute_query(time_query, (product[0],))
            total_time = int(time_row[0][0]) if time_row and time_row[0][0] is not None else 0

            card = tk.Frame(scrollable_frame, bg=self.primary_bg, highlightbackground="#888", highlightthickness=1, bd=0)
            card.pack(fill="x", pady=10, padx=5)
            left = tk.Frame(card, bg=self.primary_bg)
            left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            right = tk.Frame(card, bg=self.primary_bg)
            right.pack(side="right", fill="y", padx=10, pady=10)

            tk.Label(left, text=f"ID: {product[0]}", font=self.card_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            tk.Label(left, text=f"Тип продукции: {product[1]}", font=self.card_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            tk.Label(left, text=f"Наименование: {product[2]}", font=self.card_title_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            tk.Label(left, text=f"Артикул: {product[3]}", font=self.card_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            tk.Label(left, text=f"Мин. стоимость: {product[4]}", font=self.card_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            tk.Label(left, text=f"Основной материал: {product[5]}", font=self.card_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            
            tk.Label(left, text=f"Время изготовления: {total_time} ч", font=self.card_font, bg=self.primary_bg, anchor="e").pack(anchor="e", pady=(0, 5))

            tk.Button(right, text="Изготовить", font=self.label_font, bg=self.accent_color, fg="white",
                      command=lambda p=product: messagebox.showinfo("Изготовление!", "Изготовление!")).pack(anchor="e", pady=(0, 5))

            tk.Button(right, text="Редактировать", font=self.label_font, bg="#888", fg="white",
                      command=lambda p=product: self.edit_product_dialog(p)).pack(anchor="e", pady=(0, 5))

            def confirm_and_delete_product(pid=product[0]):
                if messagebox.askyesno("Подтвердите", "Удалить продукцию?"):
                    self.db.execute_query("DELETE FROM Products_import WHERE ID=?", (pid,))
                    self.show_products()
            tk.Button(right, text="Удалить", font=self.label_font, bg="#c0392b", fg="white",
                      command=confirm_and_delete_product).pack(anchor="e", pady=(0, 5))

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        frame.grid_rowconfigure(3, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig("all", width=e.width))

    def add_product_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить продукцию")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.primary_bg)

        # Получить типы продукции и материалы
        types = self.db.execute_query("SELECT ID, [Тип продукции] FROM Product_type_import")
        type_names = [t[1] for t in types] if types else []
        type_ids = {t[1]: t[0] for t in types} if types else {}

        mats = self.db.execute_query("SELECT ID, [Тип материала] FROM Material_type_import")
        mat_names = [m[1] for m in mats] if mats else []
        mat_ids = {m[1]: m[0] for m in mats} if mats else {}

        tk.Label(dialog, text="ID", font=self.label_font, bg=self.primary_bg).grid(row=0, column=0, sticky="e", pady=3, padx=5)
        id_var = tk.StringVar()
        tk.Entry(dialog, font=self.label_font, textvariable=id_var).grid(row=0, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Тип продукции", font=self.label_font, bg=self.primary_bg).grid(row=1, column=0, sticky="e", pady=3, padx=5)
        type_var = tk.StringVar(value=type_names[0] if type_names else "")
        ttk.Combobox(dialog, font=self.label_font, values=type_names, textvariable=type_var, state="readonly").grid(row=1, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Наименование продукции", font=self.label_font, bg=self.primary_bg).grid(row=2, column=0, sticky="e", pady=3, padx=5)
        name_var = tk.StringVar()
        tk.Entry(dialog, font=self.label_font, textvariable=name_var).grid(row=2, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Артикул", font=self.label_font, bg=self.primary_bg).grid(row=3, column=0, sticky="e", pady=3, padx=5)
        art_var = tk.StringVar()
        tk.Entry(dialog, font=self.label_font, textvariable=art_var).grid(row=3, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Мин. стоимость для партнера", font=self.label_font, bg=self.primary_bg).grid(row=4, column=0, sticky="e", pady=3, padx=5)
        price_var = tk.StringVar()
        tk.Entry(dialog, font=self.label_font, textvariable=price_var).grid(row=4, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Основной материал", font=self.label_font, bg=self.primary_bg).grid(row=5, column=0, sticky="e", pady=3, padx=5)
        mat_var = tk.StringVar(value=mat_names[0] if mat_names else "")
        ttk.Combobox(dialog, font=self.label_font, values=mat_names, textvariable=mat_var, state="readonly").grid(row=5, column=1, pady=3, padx=5, sticky="ew")

        dialog.grid_columnconfigure(1, weight=1)

        def save():
            try:
                self.db.execute_query(
                    "INSERT INTO Products_import (ID, [Тип продукции], [Наименование продукции], Артикул, [Минимальная стоимость для партнера], [Основной материал]) VALUES (?, ?, ?, ?, ?, ?)",
                    (id_var.get(), type_ids.get(type_var.get()), name_var.get(), art_var.get(), price_var.get(), mat_ids.get(mat_var.get()))
                )
                messagebox.showinfo("Успех", "Продукция добавлена")
                dialog.destroy()
                self.show_products()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка добавления: {e}")

        tk.Button(dialog, text="Сохранить", font=self.label_font, bg=self.accent_color, fg="white", command=save).grid(row=6, column=0, columnspan=2, pady=10)

    def edit_product_dialog(self, values):
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать продукцию")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.primary_bg)

        types = self.db.execute_query("SELECT ID, [Тип продукции] FROM Product_type_import")
        type_names = [t[1] for t in types] if types else []
        type_ids = {t[1]: t[0] for t in types} if types else {}

        mats = self.db.execute_query("SELECT ID, [Тип материала] FROM Material_type_import")
        mat_names = [m[1] for m in mats] if mats else []
        mat_ids = {m[1]: m[0] for m in mats} if mats else {}

        tk.Label(dialog, text="ID", font=self.label_font, bg=self.primary_bg).grid(row=0, column=0, sticky="e", pady=3, padx=5)
        id_var = tk.StringVar(value=values[0])
        tk.Entry(dialog, font=self.label_font, textvariable=id_var, state="readonly").grid(row=0, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Тип продукции", font=self.label_font, bg=self.primary_bg).grid(row=1, column=0, sticky="e", pady=3, padx=5)
        type_var = tk.StringVar(value=values[1])
        ttk.Combobox(dialog, font=self.label_font, values=type_names, textvariable=type_var, state="readonly").grid(row=1, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Наименование продукции", font=self.label_font, bg=self.primary_bg).grid(row=2, column=0, sticky="e", pady=3, padx=5)
        name_var = tk.StringVar(value=values[2])
        tk.Entry(dialog, font=self.label_font, textvariable=name_var).grid(row=2, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Артикул", font=self.label_font, bg=self.primary_bg).grid(row=3, column=0, sticky="e", pady=3, padx=5)
        art_var = tk.StringVar(value=values[3])
        tk.Entry(dialog, font=self.label_font, textvariable=art_var).grid(row=3, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Мин. стоимость для партнера", font=self.label_font, bg=self.primary_bg).grid(row=4, column=0, sticky="e", pady=3, padx=5)
        price_var = tk.StringVar(value=values[4])
        tk.Entry(dialog, font=self.label_font, textvariable=price_var).grid(row=4, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Основной материал", font=self.label_font, bg=self.primary_bg).grid(row=5, column=0, sticky="e", pady=3, padx=5)
        mat_var = tk.StringVar(value=values[5])
        ttk.Combobox(dialog, font=self.label_font, values=mat_names, textvariable=mat_var, state="readonly").grid(row=5, column=1, pady=3, padx=5, sticky="ew")

        dialog.grid_columnconfigure(1, weight=1)

        def save():
            try:
                self.db.execute_query(
                    "UPDATE Products_import SET [Тип продукции]=?, [Наименование продукции]=?, Артикул=?, [Минимальная стоимость для партнера]=?, [Основной материал]=? WHERE ID=?",
                    (type_ids.get(type_var.get()), name_var.get(), art_var.get(), price_var.get(), mat_ids.get(mat_var.get()), id_var.get())
                )
                messagebox.showinfo("Успех", "Продукция обновлена")
                dialog.destroy()
                self.show_products()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка обновления: {e}")

        tk.Button(dialog, text="Сохранить", font=self.label_font, bg=self.accent_color, fg="white", command=save).grid(row=6, column=0, columnspan=2, pady=10)

    def show_workshops(self):
        self.clear_main_area()
        frame = tk.Frame(self.root, bg=self.primary_bg, padx=20, pady=20)
        frame.grid(row=2, column=0, sticky="nsew")
        tk.Label(frame, text="Цеха", font=self.title_font, bg=self.primary_bg, fg=self.accent_color).grid(row=0, column=0, sticky="w", pady=(0, 15))

        # --- Поиск и сортировка ---
        search_frame = tk.Frame(frame, bg=self.primary_bg)
        search_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        tk.Label(search_frame, text="Поиск по названию:", font=self.label_font, bg=self.primary_bg).pack(side="left")
        search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=search_var, font=self.label_font, width=20).pack(side="left", padx=5)
        tk.Label(search_frame, text="Сортировка:", font=self.label_font, bg=self.primary_bg).pack(side="left", padx=(20,0))
        sort_options = ["Без сортировки", "По возрастанию кол-ва", "По убыванию кол-ва"]
        sort_var = tk.StringVar(value=sort_options[0])
        ttk.Combobox(search_frame, values=sort_options, textvariable=sort_var, state="readonly", width=22).pack(side="left", padx=5)
        def reload():
            self.show_workshops_filtered(search_var.get(), sort_var.get(), parent=frame)
        tk.Button(search_frame, text="Поиск", font=self.label_font, command=reload).pack(side="left", padx=10)

        add_btn = tk.Button(frame, text="Добавить цех", font=self.label_font, bg=self.accent_color, fg="white",
                            command=self.add_workshop_dialog)
        add_btn.grid(row=2, column=1, sticky="e", padx=10)

        self.show_workshops_filtered("", "Без сортировки", parent=frame)

    def show_workshops_filtered(self, search, sort_mode, parent=None):
        if parent:
            for widget in parent.pack_slaves():
                if isinstance(widget, tk.Frame) and widget not in [parent.children.get('!frame'), parent.children.get('!button')]:
                    widget.destroy()
        frame = parent if parent else self.root

        canvas = tk.Canvas(frame, bg=self.primary_bg, highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.primary_bg)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=3, column=0, sticky="nsew")
        scrollbar.grid(row=3, column=1, sticky="ns")
        frame.grid_rowconfigure(3, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        order_clause = ""
        if sort_mode == "По возрастанию кол-ва":
            order_clause = "ORDER BY [Количество человек для производства] ASC"
        elif sort_mode == "По убыванию кол-ва":
            order_clause = "ORDER BY [Количество человек для производства] DESC"

        query = f"""
        SELECT ID, [Название цеха], [Тип цеха], [Количество человек для производства]
        FROM Workshops_import
        WHERE (? = '' OR [Название цеха] LIKE ?)
        {order_clause}
        """
        params = (search, f"%{search}%")
        rows = self.db.execute_query(query, params)

        if not rows:
            tk.Label(scrollable_frame, text="Нет данных", font=self.label_font, bg=self.primary_bg).pack()
            return

        for ws in rows:
            card = tk.Frame(scrollable_frame, bg=self.primary_bg, highlightbackground="#888", highlightthickness=1, bd=0)
            card.pack(fill="x", pady=10, padx=5)
            left = tk.Frame(card, bg=self.primary_bg)
            left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            right = tk.Frame(card, bg=self.primary_bg)
            right.pack(side="right", fill="y", padx=10, pady=10)

            tk.Label(left, text=f"ID: {ws[0]}", font=self.card_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            tk.Label(left, text=f"Название цеха: {ws[1]}", font=self.card_title_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            tk.Label(left, text=f"Тип цеха: {ws[2]}", font=self.card_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            tk.Label(left, text=f"Кол-во человек: {ws[3]}", font=self.card_font, bg=self.primary_bg, anchor="w").pack(anchor="w")

            tk.Button(right, text="Редактировать", font=self.label_font, bg="#888", fg="white",
                      command=lambda w=ws: self.edit_workshop_dialog(w)).pack(anchor="e", pady=(0, 5))

            def confirm_and_delete_ws(wid=ws[0]):
                if messagebox.askyesno("Подтвердите", "Удалить цех?"):
                    self.db.execute_query("DELETE FROM Workshops_import WHERE ID=?", (wid,))
                    self.show_workshops()
            tk.Button(right, text="Удалить", font=self.label_font, bg="#c0392b", fg="white",
                      command=confirm_and_delete_ws).pack(anchor="e", pady=(0, 5))

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        frame.grid_rowconfigure(3, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig("all", width=e.width))

    def add_workshop_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить цех")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.primary_bg)

        tk.Label(dialog, text="ID", font=self.label_font, bg=self.primary_bg).grid(row=0, column=0, sticky="e", pady=3, padx=5)
        id_var = tk.StringVar()
        tk.Entry(dialog, font=self.label_font, textvariable=id_var).grid(row=0, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Название цеха", font=self.label_font, bg=self.primary_bg).grid(row=1, column=0, sticky="e", pady=3, padx=5)
        name_var = tk.StringVar()
        tk.Entry(dialog, font=self.label_font, textvariable=name_var).grid(row=1, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Тип цеха", font=self.label_font, bg=self.primary_bg).grid(row=2, column=0, sticky="e", pady=3, padx=5)
        type_var = tk.StringVar()
        tk.Entry(dialog, font=self.label_font, textvariable=type_var).grid(row=2, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Кол-во человек для производства", font=self.label_font, bg=self.primary_bg).grid(row=3, column=0, sticky="e", pady=3, padx=5)
        count_var = tk.StringVar()
        tk.Entry(dialog, font=self.label_font, textvariable=count_var).grid(row=3, column=1, pady=3, padx=5, sticky="ew")

        dialog.grid_columnconfigure(1, weight=1)

        def save():
            try:
                self.db.execute_query(
                    "INSERT INTO Workshops_import (ID, [Название цеха], [Тип цеха], [Количество человек для производства]) VALUES (?, ?, ?, ?)",
                    (id_var.get(), name_var.get(), type_var.get(), count_var.get())
                )
                messagebox.showinfo("Успех", "Цех добавлен")
                dialog.destroy()
                self.show_workshops()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка добавления: {e}")

        tk.Button(dialog, text="Сохранить", font=self.label_font, bg=self.accent_color, fg="white", command=save).grid(row=4, column=0, columnspan=2, pady=10)

    def edit_workshop_dialog(self, values):
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать цех")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.primary_bg)

        tk.Label(dialog, text="ID", font=self.label_font, bg=self.primary_bg).grid(row=0, column=0, sticky="e", pady=3, padx=5)
        id_var = tk.StringVar(value=values[0])
        tk.Entry(dialog, font=self.label_font, textvariable=id_var, state="readonly").grid(row=0, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Название цеха", font=self.label_font, bg=self.primary_bg).grid(row=1, column=0, sticky="e", pady=3, padx=5)
        name_var = tk.StringVar(value=values[1])
        tk.Entry(dialog, font=self.label_font, textvariable=name_var).grid(row=1, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Тип цеха", font=self.label_font, bg=self.primary_bg).grid(row=2, column=0, sticky="e", pady=3, padx=5)
        type_var = tk.StringVar(value=values[2])
        tk.Entry(dialog, font=self.label_font, textvariable=type_var).grid(row=2, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Кол-во человек для производства", font=self.label_font, bg=self.primary_bg).grid(row=3, column=0, sticky="e", pady=3, padx=5)
        count_var = tk.StringVar(value=values[3])
        tk.Entry(dialog, font=self.label_font, textvariable=count_var).grid(row=3, column=1, pady=3, padx=5, sticky="ew")

        dialog.grid_columnconfigure(1, weight=1)

        def save():
            try:
                self.db.execute_query(
                    "UPDATE Workshops_import SET [Название цеха]=?, [Тип цеха]=?, [Количество человек для производства]=? WHERE ID=?",
                    (name_var.get(), type_var.get(), count_var.get(), id_var.get())
                )
                messagebox.showinfo("Успех", "Цех обновлен")
                dialog.destroy()
                self.show_workshops()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка обновления: {e}")

        tk.Button(dialog, text="Сохранить", font=self.label_font, bg=self.accent_color, fg="white", command=save).grid(row=4, column=0, columnspan=2, pady=10)

    def show_users(self):
        self.clear_main_area()
        frame = tk.Frame(self.root, bg=self.primary_bg, padx=20, pady=20)
        frame.grid(row=2, column=0, sticky="nsew")
        tk.Label(frame, text="Пользователи", font=self.title_font, bg=self.primary_bg, fg=self.accent_color).grid(row=0, column=0, sticky="w", pady=(0, 15))

        search_frame = tk.Frame(frame, bg=self.primary_bg)
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        tk.Label(search_frame, text="Поиск по логину:", font=self.label_font, bg=self.primary_bg).pack(side="left")
        search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=search_var, font=self.label_font, width=20).pack(side="left", padx=5)
        def reload():
            self.show_users_filtered(search_var.get(), parent=frame)
        tk.Button(search_frame, text="Поиск", font=self.label_font, command=reload).pack(side="left", padx=10)

        self.show_users_filtered("", parent=frame)

    def show_users_filtered(self, search, parent=None):
        if parent:
            for widget in parent.pack_slaves():
                if isinstance(widget, tk.Frame) and widget not in [parent.children.get('!frame'), parent.children.get('!button')]:
                    widget.destroy()
        frame = parent if parent else self.root

        # --- Скроллируемая область ---
        canvas = tk.Canvas(frame, bg=self.primary_bg, highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.primary_bg)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Получаем список ролей (добавлено)
        roles = self.db.execute_query("SELECT RoleID, RoleName FROM Roles")
        role_names = [r[1] for r in roles] if roles else []
        role_ids = {r[1]: r[0] for r in roles} if roles else {}

        query = """
        SELECT u.UserID, u.Username, r.RoleName, u.RoleID
        FROM Users u
        JOIN Roles r ON u.RoleID = r.RoleID
        WHERE (? = '' OR u.Username LIKE ?)
        """
        params = (search, f"%{search}%")
        rows = self.db.execute_query(query, params)

        if not rows:
            tk.Label(scrollable_frame, text="Нет данных", font=self.label_font, bg=self.primary_bg).pack()
            return

        for user in rows:
            card = tk.Frame(scrollable_frame, bg=self.primary_bg, highlightbackground="#888", highlightthickness=1, bd=0)
            card.pack(fill="x", pady=10, padx=5)
            left = tk.Frame(card, bg=self.primary_bg)
            left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            right = tk.Frame(card, bg=self.primary_bg)
            right.pack(side="right", fill="y", padx=10, pady=10)

            tk.Label(left, text=f"ID: {user[0]}", font=self.card_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            tk.Label(left, text=f"Логин: {user[1]}", font=self.card_title_font, bg=self.primary_bg, anchor="w").pack(anchor="w")

            # Смена роли
            role_var = tk.StringVar(value=user[2])
            role_combo = ttk.Combobox(left, font=self.card_font, values=role_names, textvariable=role_var, state="readonly")
            role_combo.pack(anchor="w", pady=(5, 0))

            def save_role(user_id=user[0], var=role_var):
                role_id = role_ids.get(var.get())
                if role_id:
                    self.db.execute_query("UPDATE Users SET RoleID=? WHERE UserID=?", (role_id, user_id))
                    messagebox.showinfo("Успех", "Роль пользователя обновлена")
                else:
                    messagebox.showerror("Ошибка", "Роль не найдена")

            tk.Button(left, text="Сохранить роль", font=self.label_font, bg=self.accent_color, fg="white",
                      command=save_role).pack(anchor="w", pady=(5, 0))

            tk.Label(left, text=f"Роль: {user[2]}", font=self.card_font, bg=self.primary_bg, anchor="w").pack(anchor="w")

            def confirm_and_delete_user(uid=user[0]):
                if messagebox.askyesno("Подтвердите", "Удалить пользователя?"):
                    self.db.execute_query("DELETE FROM Users WHERE UserID=?", (uid,))
                    messagebox.showinfo("Удалено", "Пользователь удален")
                    self.show_users()

            tk.Button(right, text="Удалить", font=self.label_font, bg="#c0392b", fg="white",
                      command=confirm_and_delete_user).pack(anchor="e", pady=(0, 5))

        # --- Прокрутка колесом мыши только для этого canvas ---
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # Сделать frame адаптивным по ширине
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig("all", width=e.width))

    def add_user_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить пользователя")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.primary_bg)

        tk.Label(dialog, text="Логин", font=self.label_font, bg=self.primary_bg).grid(row=0, column=0, sticky="e", pady=3, padx=5)
        username_var = tk.StringVar()
        tk.Entry(dialog, font=self.label_font, textvariable=username_var).grid(row=0, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Пароль", font=self.label_font, bg=self.primary_bg).grid(row=1, column=0, sticky="e", pady=3, padx=5)
        password_var = tk.StringVar()
        tk.Entry(dialog, font=self.label_font, textvariable=password_var, show="*").grid(row=1, column=1, pady=3, padx=5, sticky="ew")

        # Получаем список ролей
        roles = self.db.execute_query("SELECT RoleID, RoleName FROM Roles")
        role_names = [r[1] for r in roles] if roles else []
        role_ids = {r[1]: r[0] for r in roles} if roles else {}
        role_var = tk.StringVar(value=role_names[0] if role_names else "")

        tk.Label(dialog, text="Роль", font=self.label_font, bg=self.primary_bg).grid(row=2, column=0, sticky="e", pady=3, padx=5)
        role_combo = ttk.Combobox(dialog, font=self.label_font, values=role_names, textvariable=role_var, state="readonly")
        role_combo.grid(row=2, column=1, pady=3, padx=5, sticky="ew")

        dialog.grid_columnconfigure(1, weight=1)

        def save():
            username = username_var.get()
            password = password_var.get()
            role_name = role_var.get()
            role_id = role_ids.get(role_name)
            if not username or not password or not role_id:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return
            try:
                self.db.execute_query(
                    "INSERT INTO Users (Username, Password, RoleID) VALUES (?, ?, ?)",
                    (username, password, role_id)
                )
                messagebox.showinfo("Успех", "Пользователь добавлен")
                dialog.destroy()
                self.show_users()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка добавления: {e}")

        tk.Button(dialog, text="Сохранить", font=self.label_font, bg=self.accent_color, fg="white", command=save).grid(row=3, column=0, columnspan=2, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
