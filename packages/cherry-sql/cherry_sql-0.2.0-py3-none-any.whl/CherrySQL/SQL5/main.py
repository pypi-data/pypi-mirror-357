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
        self.secondary_bg = "#BFD6F6"
        self.accent_color = "#405C73"
        self.font_family = "Constantia"
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

        self.setup_login_frame()

    def setup_login_frame(self):
        self.login_frame = tk.Frame(self.root, bg=self.primary_bg, padx=20, pady=20)
        self.login_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        header = tk.Frame(self.login_frame, bg=self.secondary_bg)
        header.pack(fill=tk.X, pady=(0, 20))
        tk.Label(header, text="Вход в систему", font=self.title_font,
                bg=self.secondary_bg, fg=self.accent_color).pack(pady=10)

        # Поля ввода
        tk.Label(self.login_frame, text="Логин:", font=self.label_font,
                bg=self.primary_bg).pack(anchor=tk.W, pady=5)
        self.username_entry = ttk.Entry(self.login_frame, font=self.label_font)
        self.username_entry.pack(fill=tk.X, pady=5)

        tk.Label(self.login_frame, text="Пароль:", font=self.label_font,
                bg=self.primary_bg).pack(anchor=tk.W, pady=5)
        self.password_entry = ttk.Entry(self.login_frame, show="*", font=self.label_font)
        self.password_entry.pack(fill=tk.X, pady=5)

        login_btn = tk.Button(self.login_frame, text="Войти", command=self.login,
                            font=self.label_font, bg=self.accent_color, fg="white")
        login_btn.pack(pady=20, ipadx=10)

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

        # Шапка
        self.header_frame = tk.Frame(self.root, bg=self.secondary_bg)
        self.header_frame.pack(fill=tk.X)

        # Логотип
        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        if os.path.exists(logo_path):
            img = Image.open(logo_path)
            img = img.resize((40, 40), Image.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img)
            tk.Label(self.header_frame, image=self.logo_img,
                    bg=self.secondary_bg).pack(side=tk.LEFT, padx=10, pady=5)

        # Главная надпись
        tk.Label(self.header_frame, text="Главное меню", font=self.title_font,
                bg=self.secondary_bg, fg=self.accent_color).pack(side=tk.LEFT, expand=True)

        # Имя пользователя
        user_info = f"{self.current_user['username']} ({self.current_user['role']})"
        tk.Label(self.header_frame, text=user_info, font=self.label_font,
                bg=self.secondary_bg, fg=self.accent_color).pack(side=tk.RIGHT, padx=10)

        # Меню
        self.menu_frame = tk.Frame(self.root, bg=self.secondary_bg, pady=10)
        self.menu_frame.pack(fill=tk.X)

        btns = [
            ("Материалы", self.show_materials),
            ("Типы материалов", self.show_material_types),
            ("Продукция", self.show_products),
            ("Типы продукции", self.show_product_types),
        ]

        for text, cmd in btns:
            btn = tk.Button(self.menu_frame, text=text, command=cmd,
                           font=self.label_font, bg=self.accent_color,
                           fg="white", padx=10, pady=5)
            btn.pack(side=tk.LEFT, padx=5)

        if self.current_user['role'] == 'Администратор':
            btn = tk.Button(self.menu_frame, text="Пользователи", command=self.show_users,
                          font=self.label_font, bg=self.accent_color,
                          fg="white", padx=10, pady=5)
            btn.pack(side=tk.LEFT, padx=5)

        # Основная область для контента
        self.content_frame = tk.Frame(self.root, bg=self.primary_bg)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def create_scrollable_area(self, parent):
        # Основной контейнер
        container = tk.Frame(parent, bg=self.primary_bg)
        container.pack(fill=tk.BOTH, expand=True)

        # Канвас для прокрутки
        canvas = tk.Canvas(container, bg=self.primary_bg, highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Полоса прокрутки
        scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Фрейм для контента
        scrollable_frame = tk.Frame(canvas, bg=self.primary_bg)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Обработка колеса мыши
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        return scrollable_frame

    def create_search_panel(self, parent, search_callback):
        search_frame = tk.Frame(parent, bg=self.primary_bg)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(search_frame, text="Поиск:", font=self.label_font,
                bg=self.primary_bg).pack(side=tk.LEFT)

        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var,
                               font=self.label_font, width=20)
        search_entry.pack(side=tk.LEFT, padx=5)

        search_btn = tk.Button(search_frame, text="Поиск", font=self.label_font,
                             command=lambda: search_callback(search_var.get()))
        search_btn.pack(side=tk.LEFT, padx=5)

        return search_var

    def create_card(self, parent, data, edit_callback, delete_callback):
        card = tk.Frame(parent, bg=self.primary_bg, bd=1,
                       highlightbackground="#888", highlightthickness=1)
        card.pack(fill=tk.X, pady=5, padx=5)

        # Левая часть карточки с данными
        left_frame = tk.Frame(card, bg=self.primary_bg)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Правая часть с кнопками
        right_frame = tk.Frame(card, bg=self.primary_bg)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        # Отображение данных в левой части
        for i, (label, value) in enumerate(data.items()):
            if i == 0:  # Первый элемент - заголовок
                tk.Label(left_frame, text=value, font=self.card_title_font,
                        bg=self.primary_bg, anchor="w").pack(anchor="w")
            else:
                tk.Label(left_frame, text=f"{label}: {value}", font=self.card_font,
                        bg=self.primary_bg, anchor="w").pack(anchor="w")

        # Кнопки в правой части
        edit_btn = tk.Button(right_frame, text="Редактировать", font=self.label_font,
                           bg="#888", fg="white", command=edit_callback)
        edit_btn.pack(pady=5)

        delete_btn = tk.Button(right_frame, text="Удалить", font=self.label_font,
                             bg="#c0392b", fg="white", command=delete_callback)
        delete_btn.pack(pady=5)

    # Методы для работы с материалами
    def show_materials(self):
        self.clear_content()

        # Заголовок
        tk.Label(self.content_frame, text="Материалы", font=self.title_font,
                bg=self.primary_bg, fg=self.accent_color).pack(anchor=tk.W, pady=(0, 15))

        # Панель поиска
        def search_callback(search_text):
            self.show_materials_filtered(search_text, sort_var.get())

        search_var = self.create_search_panel(self.content_frame, search_callback)

        # Сортировка
        sort_frame = tk.Frame(self.content_frame, bg=self.primary_bg)
        sort_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(sort_frame, text="Сортировка:", font=self.label_font,
                bg=self.primary_bg).pack(side=tk.LEFT)

        sort_options = ["Без сортировки", "По возрастанию цены", "По убыванию цены"]
        sort_var = tk.StringVar(value=sort_options[0])
        sort_combobox = ttk.Combobox(sort_frame, values=sort_options,
                                   textvariable=sort_var, state="readonly", width=22)
        sort_combobox.pack(side=tk.LEFT, padx=5)

        # Кнопка добавления
        add_btn = tk.Button(self.content_frame, text="Добавить материал",
                          font=self.label_font, bg=self.accent_color, fg="white",
                          command=self.add_material_dialog)
        add_btn.pack(anchor=tk.E, pady=10)

        # Область прокрутки
        scrollable_frame = self.create_scrollable_area(self.content_frame)
        self.show_materials_filtered("", "Без сортировки", scrollable_frame)

    def show_materials_filtered(self, search_text, sort_mode, parent=None):
        if parent:
            for widget in parent.winfo_children():
                widget.destroy()

        # Получаем данные из БД
        order_clause = ""
        if sort_mode == "По возрастанию цены":
            order_clause = "ORDER BY [Цена единицы материала] ASC"
        elif sort_mode == "По убыванию цены":
            order_clause = "ORDER BY [Цена единицы материала] DESC"

        query = f"""
        SELECT m.ID, m.[Наименование материала], t.[Тип материала],
               m.[Цена единицы материала], m.[Количество на складе],
               m.[Минимальное количество], m.[Количество в упаковке],
               m.[Единица измерения]
        FROM Materials_import m
        JOIN Material_type_import t ON m.[Тип материала] = t.ID
        WHERE (? = '' OR m.[Наименование материала] LIKE ?)
        {order_clause}
        """
        params = (search_text, f"%{search_text}%")
        rows = self.db.execute_query(query, params)

        if not rows:
            tk.Label(parent, text="Нет данных", font=self.label_font,
                    bg=self.primary_bg).pack()
            return

        for row in rows:
            data = {
                "ID": row[0],
                "Наименование": row[1],
                "Тип материала": row[2],
                "Цена": row[3],
                "Количество на складе": row[4],
                "Минимальное количество": row[5],
                "Количество в упаковке": row[6],
                "Единица измерения": row[7]
            }

            self.create_card(
                parent,
                data,
                lambda r=row: self.edit_material_dialog(r),
                lambda id=row[0]: self.confirm_delete("материал", id, self.show_materials)
            )

    def add_material_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить материал")
        dialog.transient(self.root)
        dialog.grab_set()

        # Получаем типы материалов
        types = self.db.execute_query("SELECT ID, [Тип материала] FROM Material_type_import")
        type_names = [t[1] for t in types] if types else []

        # Форма добавления
        form = tk.Frame(dialog, bg=self.primary_bg, padx=20, pady=20)
        form.pack(fill=tk.BOTH, expand=True)

        fields = [
            ("ID:", tk.StringVar()),
            ("Наименование:", tk.StringVar()),
            ("Тип материала:", tk.StringVar(value=type_names[0] if type_names else "")),
            ("Цена:", tk.StringVar()),
            ("Количество на складе:", tk.StringVar()),
            ("Минимальное количество:", tk.StringVar()),
            ("Количество в упаковке:", tk.StringVar()),
            ("Единица измерения:", tk.StringVar())
        ]

        for i, (label, var) in enumerate(fields):
            tk.Label(form, text=label, font=self.label_font,
                    bg=self.primary_bg).grid(row=i, column=0, sticky=tk.E, pady=5)

            if label == "Тип материала:":
                combobox = ttk.Combobox(form, textvariable=var, values=type_names,
                                      state="readonly", font=self.label_font)
                combobox.grid(row=i, column=1, sticky=tk.EW, pady=5)
            else:
                entry = tk.Entry(form, textvariable=var, font=self.label_font)
                entry.grid(row=i, column=1, sticky=tk.EW, pady=5)

        form.grid_columnconfigure(1, weight=1)

        def save():
            try:
                self.db.execute_query(
                    """INSERT INTO Materials_import
                    (ID, [Наименование материала], [Тип материала], [Цена единицы материала],
                    [Количество на складе], [Минимальное количество], [Количество в упаковке],
                    [Единица измерения]) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    tuple(var.get() for label, var in fields)
                )
                messagebox.showinfo("Успех", "Материал добавлен")
                dialog.destroy()
                self.show_materials()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка добавления: {e}")

        save_btn = tk.Button(form, text="Сохранить", font=self.label_font,
                           bg=self.accent_color, fg="white", command=save)
        save_btn.grid(row=len(fields), column=0, columnspan=2, pady=10)

    def edit_material_dialog(self, material):
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать материал")
        dialog.transient(self.root)
        dialog.grab_set()

        # Получаем типы материалов
        types = self.db.execute_query("SELECT ID, [Тип материала] FROM Material_type_import")
        type_names = [t[1] for t in types] if types else []

        # Форма редактирования
        form = tk.Frame(dialog, bg=self.primary_bg, padx=20, pady=20)
        form.pack(fill=tk.BOTH, expand=True)

        fields = [
            ("ID:", tk.StringVar(value=material[0]), True),
            ("Наименование:", tk.StringVar(value=material[1]), False),
            ("Тип материала:", tk.StringVar(value=material[2]), False),
            ("Цена:", tk.StringVar(value=material[3]), False),
            ("Количество на складе:", tk.StringVar(value=material[4]), False),
            ("Минимальное количество:", tk.StringVar(value=material[5]), False),
            ("Количество в упаковке:", tk.StringVar(value=material[6]), False),
            ("Единица измерения:", tk.StringVar(value=material[7]), False)
        ]

        for i, (label, var, readonly) in enumerate(fields):
            tk.Label(form, text=label, font=self.label_font,
                    bg=self.primary_bg).grid(row=i, column=0, sticky=tk.E, pady=5)

            if label == "Тип материала:":
                combobox = ttk.Combobox(form, textvariable=var, values=type_names,
                                      state="readonly", font=self.label_font)
                combobox.grid(row=i, column=1, sticky=tk.EW, pady=5)
            else:
                entry = tk.Entry(form, textvariable=var, font=self.label_font,
                               state="readonly" if readonly else "normal")
                entry.grid(row=i, column=1, sticky=tk.EW, pady=5)

        form.grid_columnconfigure(1, weight=1)

        def save():
            try:
                self.db.execute_query(
                    """UPDATE Materials_import SET
                    [Наименование материала]=?, [Тип материала]=?, [Цена единицы материала]=?,
                    [Количество на складе]=?, [Минимальное количество]=?,
                    [Количество в упаковке]=?, [Единица измерения]=?
                    WHERE ID=?""",
                    tuple(var.get() for label, var, _ in fields[1:]) + (fields[0][1].get(),)
                )
                messagebox.showinfo("Успех", "Материал обновлен")
                dialog.destroy()
                self.show_materials()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка обновления: {e}")

        save_btn = tk.Button(form, text="Сохранить", font=self.label_font,
                           bg=self.accent_color, fg="white", command=save)
        save_btn.grid(row=len(fields), column=0, columnspan=2, pady=10)

    # Методы для работы с типами материалов
    def show_material_types(self):
        self.clear_content()

        # Заголовок
        tk.Label(self.content_frame, text="Типы материалов", font=self.title_font,
                bg=self.primary_bg, fg=self.accent_color).pack(anchor=tk.W, pady=(0, 15))

        # Панель поиска
        def search_callback(search_text):
            self.show_material_types_filtered(search_text, sort_var.get())

        search_var = self.create_search_panel(self.content_frame, search_callback)

        # Сортировка
        sort_frame = tk.Frame(self.content_frame, bg=self.primary_bg)
        sort_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(sort_frame, text="Сортировка:", font=self.label_font,
                bg=self.primary_bg).pack(side=tk.LEFT)

        sort_options = ["Без сортировки", "По возрастанию % потерь", "По убыванию % потерь"]
        sort_var = tk.StringVar(value=sort_options[0])
        sort_combobox = ttk.Combobox(sort_frame, values=sort_options,
                                   textvariable=sort_var, state="readonly", width=22)
        sort_combobox.pack(side=tk.LEFT, padx=5)

        # Кнопка добавления
        add_btn = tk.Button(self.content_frame, text="Добавить тип материала",
                          font=self.label_font, bg=self.accent_color, fg="white",
                          command=self.add_material_type_dialog)
        add_btn.pack(anchor=tk.E, pady=10)

        # Область прокрутки
        scrollable_frame = self.create_scrollable_area(self.content_frame)
        self.show_material_types_filtered("", "Без сортировки", scrollable_frame)

    def show_material_types_filtered(self, search_text, sort_mode, parent=None):
        if parent:
            for widget in parent.winfo_children():
                widget.destroy()

        # Получаем данные из БД
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
        params = (search_text, f"%{search_text}%")
        rows = self.db.execute_query(query, params)

        if not rows:
            tk.Label(parent, text="Нет данных", font=self.label_font,
                    bg=self.primary_bg).pack()
            return

        for row in rows:
            data = {
                "ID": row[0],
                "Тип материала": row[1],
                "Процент потерь сырья": row[2]
            }

            self.create_card(
                parent,
                data,
                lambda r=row: self.edit_material_type_dialog(r),
                lambda id=row[0]: self.confirm_delete("тип материала", id, self.show_material_types)
            )

    def add_material_type_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить тип материала")
        dialog.transient(self.root)
        dialog.grab_set()

        # Форма добавления
        form = tk.Frame(dialog, bg=self.primary_bg, padx=20, pady=20)
        form.pack(fill=tk.BOTH, expand=True)

        fields = [
            ("ID:", tk.StringVar()),
            ("Тип материала:", tk.StringVar()),
            ("Процент потерь сырья:", tk.StringVar())
        ]

        for i, (label, var) in enumerate(fields):
            tk.Label(form, text=label, font=self.label_font,
                    bg=self.primary_bg).grid(row=i, column=0, sticky=tk.E, pady=5)
            entry = tk.Entry(form, textvariable=var, font=self.label_font)
            entry.grid(row=i, column=1, sticky=tk.EW, pady=5)

        form.grid_columnconfigure(1, weight=1)

        def save():
            try:
                self.db.execute_query(
                    "INSERT INTO Material_type_import (ID, [Тип материала], [Процент потерь сырья]) VALUES (?, ?, ?)",
                    tuple(var.get() for label, var in fields)
                )
                messagebox.showinfo("Успех", "Тип материала добавлен")
                dialog.destroy()
                self.show_material_types()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка добавления: {e}")

        save_btn = tk.Button(form, text="Сохранить", font=self.label_font,
                           bg=self.accent_color, fg="white", command=save)
        save_btn.grid(row=len(fields), column=0, columnspan=2, pady=10)

    def edit_material_type_dialog(self, material_type):
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать тип материала")
        dialog.transient(self.root)
        dialog.grab_set()

        # Форма редактирования
        form = tk.Frame(dialog, bg=self.primary_bg, padx=20, pady=20)
        form.pack(fill=tk.BOTH, expand=True)

        fields = [
            ("ID:", tk.StringVar(value=material_type[0]), True),
            ("Тип материала:", tk.StringVar(value=material_type[1]), False),
            ("Процент потерь сырья:", tk.StringVar(value=material_type[2]), False)
        ]

        for i, (label, var, readonly) in enumerate(fields):
            tk.Label(form, text=label, font=self.label_font,
                    bg=self.primary_bg).grid(row=i, column=0, sticky=tk.E, pady=5)
            entry = tk.Entry(form, textvariable=var, font=self.label_font,
                           state="readonly" if readonly else "normal")
            entry.grid(row=i, column=1, sticky=tk.EW, pady=5)

        form.grid_columnconfigure(1, weight=1)

        def save():
            try:
                self.db.execute_query(
                    "UPDATE Material_type_import SET [Тип материала]=?, [Процент потерь сырья]=? WHERE ID=?",
                    (fields[1][1].get(), fields[2][1].get(), fields[0][1].get())
                )
                messagebox.showinfo("Успех", "Тип материала обновлен")
                dialog.destroy()
                self.show_material_types()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка обновления: {e}")

        save_btn = tk.Button(form, text="Сохранить", font=self.label_font,
                           bg=self.accent_color, fg="white", command=save)
        save_btn.grid(row=len(fields), column=0, columnspan=2, pady=10)

    # Методы для работы с продукцией
    def show_products(self):
        self.clear_content()

        # Заголовок
        tk.Label(self.content_frame, text="Продукция", font=self.title_font,
                bg=self.primary_bg, fg=self.accent_color).pack(anchor=tk.W, pady=(0, 15))

        # Панель поиска
        def search_callback(search_text):
            self.show_products_filtered(search_text, sort_var.get())

        search_var = self.create_search_panel(self.content_frame, search_callback)

        # Сортировка
        sort_frame = tk.Frame(self.content_frame, bg=self.primary_bg)
        sort_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(sort_frame, text="Сортировка:", font=self.label_font,
                bg=self.primary_bg).pack(side=tk.LEFT)

        sort_options = ["Без сортировки", "По возрастанию цены", "По убыванию цены"]
        sort_var = tk.StringVar(value=sort_options[0])
        sort_combobox = ttk.Combobox(sort_frame, values=sort_options,
                                   textvariable=sort_var, state="readonly", width=22)
        sort_combobox.pack(side=tk.LEFT, padx=5)

        # Кнопка добавления
        add_btn = tk.Button(self.content_frame, text="Добавить продукцию",
                          font=self.label_font, bg=self.accent_color, fg="white",
                          command=self.add_product_dialog)
        add_btn.pack(anchor=tk.E, pady=10)

        # Область прокрутки
        scrollable_frame = self.create_scrollable_area(self.content_frame)
        self.show_products_filtered("", "Без сортировки", scrollable_frame)

    def show_products_filtered(self, search_text, sort_mode, parent=None):
        if parent:
            for widget in parent.winfo_children():
                widget.destroy()

        # Получаем данные из БД
        order_clause = ""
        if sort_mode == "По возрастанию цены":
            order_clause = "ORDER BY [Минимальная стоимость для партнера] ASC"
        elif sort_mode == "По убыванию цены":
            order_clause = "ORDER BY [Минимальная стоимость для партнера] DESC"

        query = f"""
        SELECT p.ID, p.[Наименование продукции], pt.[Тип продукции],
               p.Артикул, p.[Минимальная стоимость для партнера]
        FROM Products_import p
        JOIN Product_type_import pt ON p.[Тип продукции] = pt.ID
        WHERE (? = '' OR p.[Наименование продукции] LIKE ?)
        {order_clause}
        """
        params = (search_text, f"%{search_text}%")
        rows = self.db.execute_query(query, params)

        if not rows:
            tk.Label(parent, text="Нет данных", font=self.label_font,
                    bg=self.primary_bg).pack()
            return

        for row in rows:
            data = {
                "ID": row[0],
                "Наименование": row[1],
                "Тип продукции": row[2],
                "Артикул": row[3],
                "Минимальная стоимость": row[4]
            }

            self.create_card(
                parent,
                data,
                lambda r=row: self.edit_product_dialog(r),
                lambda id=row[0]: self.confirm_delete("продукцию", id, self.show_products)
            )

    def add_product_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить продукцию")
        dialog.transient(self.root)
        dialog.grab_set()

        # Получаем типы продукции
        types = self.db.execute_query("SELECT ID, [Тип продукции] FROM Product_type_import")
        type_names = [t[1] for t in types] if types else []

        # Форма добавления
        form = tk.Frame(dialog, bg=self.primary_bg, padx=20, pady=20)
        form.pack(fill=tk.BOTH, expand=True)

        fields = [
            ("ID:", tk.StringVar()),
            ("Тип продукции:", tk.StringVar(value=type_names[0] if type_names else "")),
            ("Наименование продукции:", tk.StringVar()),
            ("Артикул:", tk.StringVar()),
            ("Минимальная стоимость:", tk.StringVar())
        ]

        for i, (label, var) in enumerate(fields):
            tk.Label(form, text=label, font=self.label_font,
                    bg=self.primary_bg).grid(row=i, column=0, sticky=tk.E, pady=5)

            if label == "Тип продукции:":
                combobox = ttk.Combobox(form, textvariable=var, values=type_names,
                                      state="readonly", font=self.label_font)
                combobox.grid(row=i, column=1, sticky=tk.EW, pady=5)
            else:
                entry = tk.Entry(form, textvariable=var, font=self.label_font)
                entry.grid(row=i, column=1, sticky=tk.EW, pady=5)

        form.grid_columnconfigure(1, weight=1)

        def save():
            try:
                # Получаем ID типа продукции
                type_id = next((t[0] for t in types if t[1] == fields[1][1].get()), None)
                if not type_id:
                    messagebox.showerror("Ошибка", "Выберите тип продукции")
                    return

                self.db.execute_query(
                    """INSERT INTO Products_import
                    (ID, [Тип продукции], [Наименование продукции], Артикул,
                    [Минимальная стоимость для партнера]) VALUES (?, ?, ?, ?, ?)""",
                    (fields[0][1].get(), type_id, fields[2][1].get(),
                     fields[3][1].get(), fields[4][1].get())
                )
                messagebox.showinfo("Успех", "Продукция добавлена")
                dialog.destroy()
                self.show_products()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка добавления: {e}")

        save_btn = tk.Button(form, text="Сохранить", font=self.label_font,
                           bg=self.accent_color, fg="white", command=save)
        save_btn.grid(row=len(fields), column=0, columnspan=2, pady=10)

    def edit_product_dialog(self, product):
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать продукцию")
        dialog.transient(self.root)
        dialog.grab_set()

        # Получаем типы продукции
        types = self.db.execute_query("SELECT ID, [Тип продукции] FROM Product_type_import")
        type_names = [t[1] for t in types] if types else []
        type_id_names = {t[0]: t[1] for t in types} if types else {}

        # Форма редактирования
        form = tk.Frame(dialog, bg=self.primary_bg, padx=20, pady=20)
        form.pack(fill=tk.BOTH, expand=True)

        current_type_name = type_id_names.get(product[2], "")

        fields = [
            ("ID:", tk.StringVar(value=product[0]), True),
            ("Тип продукции:", tk.StringVar(value=current_type_name), False),
            ("Наименование продукции:", tk.StringVar(value=product[1]), False),
            ("Артикул:", tk.StringVar(value=product[3] if product[3] else ""), False),
            ("Минимальная стоимость:", tk.StringVar(value=str(product[4])), False)
        ]

        for i, (label, var, readonly) in enumerate(fields):
            tk.Label(form, text=label, font=self.label_font,
                    bg=self.primary_bg).grid(row=i, column=0, sticky=tk.E, pady=5)

            if label == "Тип продукции:":
                combobox = ttk.Combobox(form, textvariable=var, values=type_names,
                                      state="readonly", font=self.label_font)
                combobox.grid(row=i, column=1, sticky=tk.EW, pady=5)
            else:
                entry = tk.Entry(form, textvariable=var, font=self.label_font,
                               state="readonly" if readonly else "normal")
                entry.grid(row=i, column=1, sticky=tk.EW, pady=5)

        form.grid_columnconfigure(1, weight=1)

        def save():
            try:
                # Получаем ID типа продукции
                type_id = next((t[0] for t in types if t[1] == fields[1][1].get()), None)
                if not type_id:
                    messagebox.showerror("Ошибка", "Выберите тип продукции")
                    return

                self.db.execute_query(
                    """UPDATE Products_import SET
                    [Тип продукции]=?, [Наименование продукции]=?, Артикул=?,
                    [Минимальная стоимость для партнера]=? WHERE ID=?""",
                    (type_id, fields[2][1].get(), fields[3][1].get(),
                     fields[4][1].get(), fields[0][1].get())
                )
                messagebox.showinfo("Успех", "Продукция обновлена")
                dialog.destroy()
                self.show_products()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка обновления: {e}")

        save_btn = tk.Button(form, text="Сохранить", font=self.label_font,
                           bg=self.accent_color, fg="white", command=save)
        save_btn.grid(row=len(fields), column=0, columnspan=2, pady=10)

    # Методы для работы с типами продукции
    def show_product_types(self):
        self.clear_content()

        # Заголовок
        tk.Label(self.content_frame, text="Типы продукции", font=self.title_font,
                bg=self.primary_bg, fg=self.accent_color).pack(anchor=tk.W, pady=(0, 15))

        # Панель поиска
        def search_callback(search_text):
            self.show_product_types_filtered(search_text, sort_var.get())

        search_var = self.create_search_panel(self.content_frame, search_callback)

        # Сортировка
        sort_frame = tk.Frame(self.content_frame, bg=self.primary_bg)
        sort_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(sort_frame, text="Сортировка:", font=self.label_font,
                bg=self.primary_bg).pack(side=tk.LEFT)

        sort_options = ["Без сортировки", "По возрастанию коэффициента", "По убыванию коэффициента"]
        sort_var = tk.StringVar(value=sort_options[0])
        sort_combobox = ttk.Combobox(sort_frame, values=sort_options,
                                   textvariable=sort_var, state="readonly", width=25)
        sort_combobox.pack(side=tk.LEFT, padx=5)

        # Кнопка добавления
        add_btn = tk.Button(self.content_frame, text="Добавить тип продукции",
                          font=self.label_font, bg=self.accent_color, fg="white",
                          command=self.add_product_type_dialog)
        add_btn.pack(anchor=tk.E, pady=10)

        # Область прокрутки
        scrollable_frame = self.create_scrollable_area(self.content_frame)
        self.show_product_types_filtered("", "Без сортировки", scrollable_frame)

    def show_product_types_filtered(self, search_text, sort_mode, parent=None):
        if parent:
            for widget in parent.winfo_children():
                widget.destroy()

        # Получаем данные из БД
        order_clause = ""
        if sort_mode == "По возрастанию коэффициента":
            order_clause = "ORDER BY [Коэффициент типа продукции] ASC"
        elif sort_mode == "По убыванию коэффициента":
            order_clause = "ORDER BY [Коэффициент типа продукции] DESC"

        query = f"""
        SELECT ID, [Тип продукции], [Коэффициент типа продукции]
        FROM Product_type_import
        WHERE (? = '' OR [Тип продукции] LIKE ?)
        {order_clause}
        """
        params = (search_text, f"%{search_text}%")
        rows = self.db.execute_query(query, params)

        if not rows:
            tk.Label(parent, text="Нет данных", font=self.label_font,
                    bg=self.primary_bg).pack()
            return

        for row in rows:
            data = {
                "ID": row[0],
                "Тип продукции": row[1],
                "Коэффициент": row[2]
            }

            self.create_card(
                parent,
                data,
                lambda r=row: self.edit_product_type_dialog(r),
                lambda id=row[0]: self.confirm_delete("тип продукции", id, self.show_product_types)
            )

    def add_product_type_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить тип продукции")
        dialog.transient(self.root)
        dialog.grab_set()

        # Форма добавления
        form = tk.Frame(dialog, bg=self.primary_bg, padx=20, pady=20)
        form.pack(fill=tk.BOTH, expand=True)

        fields = [
            ("ID:", tk.StringVar()),
            ("Тип продукции:", tk.StringVar()),
            ("Коэффициент типа продукции:", tk.StringVar())
        ]

        for i, (label, var) in enumerate(fields):
            tk.Label(form, text=label, font=self.label_font,
                    bg=self.primary_bg).grid(row=i, column=0, sticky=tk.E, pady=5)
            entry = tk.Entry(form, textvariable=var, font=self.label_font)
            entry.grid(row=i, column=1, sticky=tk.EW, pady=5)

        form.grid_columnconfigure(1, weight=1)

        def save():
            try:
                self.db.execute_query(
                    "INSERT INTO Product_type_import (ID, [Тип продукции], [Коэффициент типа продукции]) VALUES (?, ?, ?)",
                    tuple(var.get() for label, var in fields)
                )
                messagebox.showinfo("Успех", "Тип продукции добавлен")
                dialog.destroy()
                self.show_product_types()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка добавления: {e}")

        save_btn = tk.Button(form, text="Сохранить", font=self.label_font,
                           bg=self.accent_color, fg="white", command=save)
        save_btn.grid(row=len(fields), column=0, columnspan=2, pady=10)

    def edit_product_type_dialog(self, product_type):
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать тип продукции")
        dialog.transient(self.root)
        dialog.grab_set()

        # Форма редактирования
        form = tk.Frame(dialog, bg=self.primary_bg, padx=20, pady=20)
        form.pack(fill=tk.BOTH, expand=True)

        fields = [
            ("ID:", tk.StringVar(value=product_type[0]), True),
            ("Тип продукции:", tk.StringVar(value=product_type[1]), False),
            ("Коэффициент типа продукции:", tk.StringVar(value=str(product_type[2])), False)
        ]

        for i, (label, var, readonly) in enumerate(fields):
            tk.Label(form, text=label, font=self.label_font,
                    bg=self.primary_bg).grid(row=i, column=0, sticky=tk.E, pady=5)
            entry = tk.Entry(form, textvariable=var, font=self.label_font,
                           state="readonly" if readonly else "normal")
            entry.grid(row=i, column=1, sticky=tk.EW, pady=5)

        form.grid_columnconfigure(1, weight=1)

        def save():
            try:
                self.db.execute_query(
                    "UPDATE Product_type_import SET [Тип продукции]=?, [Коэффициент типа продукции]=? WHERE ID=?",
                    (fields[1][1].get(), fields[2][1].get(), fields[0][1].get())
                )
                messagebox.showinfo("Успех", "Тип продукции обновлен")
                dialog.destroy()
                self.show_product_types()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка обновления: {e}")

        save_btn = tk.Button(form, text="Сохранить", font=self.label_font,
                           bg=self.accent_color, fg="white", command=save)
        save_btn.grid(row=len(fields), column=0, columnspan=2, pady=10)

    # Методы для работы с пользователями
    def show_users(self):
        self.clear_content()

        # Заголовок
        tk.Label(self.content_frame, text="Пользователи", font=self.title_font,
                bg=self.primary_bg, fg=self.accent_color).pack(anchor=tk.W, pady=(0, 15))

        # Панель поиска
        def search_callback(search_text):
            self.show_users_filtered(search_text)

        self.create_search_panel(self.content_frame, search_callback)

        # Область прокрутки
        scrollable_frame = self.create_scrollable_area(self.content_frame)
        self.show_users_filtered("", scrollable_frame)

    def show_users_filtered(self, search_text, parent=None):
        if parent:
            for widget in parent.winfo_children():
                widget.destroy()

        # Получаем список ролей
        roles = self.db.execute_query("SELECT RoleID, RoleName FROM Roles")
        role_names = [r[1] for r in roles] if roles else []
        role_ids = {r[1]: r[0] for r in roles} if roles else {}

        query = """
        SELECT u.UserID, u.Username, r.RoleName, u.RoleID
        FROM Users u
        JOIN Roles r ON u.RoleID = r.RoleID
        WHERE (? = '' OR u.Username LIKE ?)
        """
        params = (search_text, f"%{search_text}%")
        rows = self.db.execute_query(query, params)

        if not rows:
            tk.Label(parent, text="Нет данных", font=self.label_font,
                    bg=self.primary_bg).pack()
            return

        for row in rows:
            data = {
                "ID": row[0],
                "Логин": row[1],
                "Роль": row[2]
            }

            def save_role(user_id=row[0], current_role=row[2]):
                role_dialog = tk.Toplevel(self.root)
                role_dialog.title("Изменить роль")
                role_dialog.transient(self.root)
                role_dialog.grab_set()

                frame = tk.Frame(role_dialog, bg=self.primary_bg, padx=20, pady=20)
                frame.pack()

                tk.Label(frame, text="Выберите новую роль:", font=self.label_font,
                        bg=self.primary_bg).pack()

                role_var = tk.StringVar(value=current_role)
                role_combo = ttk.Combobox(frame, textvariable=role_var,
                                         values=role_names, state="readonly")
                role_combo.pack(pady=10)

                def save():
                    role_id = role_ids.get(role_var.get())
                    if role_id:
                        self.db.execute_query(
                            "UPDATE Users SET RoleID=? WHERE UserID=?",
                            (role_id, user_id)
                        )
                        messagebox.showinfo("Успех", "Роль пользователя обновлена")
                        role_dialog.destroy()
                        self.show_users()
                    else:
                        messagebox.showerror("Ошибка", "Роль не найдена")

                save_btn = tk.Button(frame, text="Сохранить", font=self.label_font,
                                   bg=self.accent_color, fg="white", command=save)
                save_btn.pack(pady=10)

            card = tk.Frame(parent, bg=self.primary_bg, bd=1,
                         highlightbackground="#888", highlightthickness=1)
            card.pack(fill=tk.X, pady=5, padx=5)

            left_frame = tk.Frame(card, bg=self.primary_bg)
            left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

            right_frame = tk.Frame(card, bg=self.primary_bg)
            right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

            for label, value in data.items():
                if label == "ID":
                    tk.Label(left_frame, text=value, font=self.card_font,
                            bg=self.primary_bg, anchor="w").pack(anchor="w")
                else:
                    tk.Label(left_frame, text=f"{label}: {value}", font=self.card_font,
                            bg=self.primary_bg, anchor="w").pack(anchor="w")

            change_role_btn = tk.Button(right_frame, text="Изменить роль",
                                     font=self.label_font, bg="#888", fg="white",
                                     command=save_role)
            change_role_btn.pack(pady=5)

            def delete_user(user_id=row[0]):
                if messagebox.askyesno("Подтверждение", "Удалить пользователя?"):
                    self.db.execute_query("DELETE FROM Users WHERE UserID=?", (user_id,))
                    self.show_users()

            delete_btn = tk.Button(right_frame, text="Удалить", font=self.label_font,
                                 bg="#c0392b", fg="white", command=delete_user)
            delete_btn.pack(pady=5)

    # Вспомогательный метод для подтверждения удаления
    def confirm_delete(self, item_type, item_id, refresh_callback):
        def delete():
            if messagebox.askyesno("Подтверждение", f"Удалить {item_type}?"):
                try:
                    if item_type == "материал":
                        self.db.execute_query("DELETE FROM Materials_import WHERE ID=?", (item_id,))
                    elif item_type == "тип материала":
                        self.db.execute_query("DELETE FROM Material_type_import WHERE ID=?", (item_id,))
                    elif item_type == "продукцию":
                        self.db.execute_query("DELETE FROM Products_import WHERE ID=?", (item_id,))
                    elif item_type == "тип продукции":
                        self.db.execute_query("DELETE FROM Product_type_import WHERE ID=?", (item_id,))

                    refresh_callback()
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка при удалении: {e}")

        return delete

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
