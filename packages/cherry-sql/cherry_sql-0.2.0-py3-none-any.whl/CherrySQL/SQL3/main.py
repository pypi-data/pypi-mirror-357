import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from datetime import datetime
from PIL import Image, ImageTk  # pip install pillow
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
        self.secondary_bg = "#BBDCFA"
        self.accent_color = "#0C4882"
        self.font_family = "Bahnschrift Light SemiCondensed"
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
            ("Партнеры", self.show_partners),
            ("Продукция", self.show_products),
            ("Заявки", self.show_requests),
        ]
        for idx, (text, cmd) in enumerate(btns):
            tk.Button(self.menu_frame, text=text, command=cmd, font=self.label_font, bg=self.accent_color, fg="white", activebackground=self.secondary_bg).grid(row=0, column=idx, padx=5, pady=2, ipadx=5, sticky="ew")

        if self.current_user['role'] == 'Администратор':
            tk.Button(self.menu_frame, text="Управление пользователями", command=self.show_users, font=self.label_font, bg=self.accent_color, fg="white", activebackground=self.secondary_bg).grid(row=0, column=len(btns), padx=5, pady=2, ipadx=5, sticky="ew")

        for i in range(len(btns) + 1):
            self.menu_frame.grid_columnconfigure(i, weight=1)

    def clear_main_area(self):
        # Удаляет все виджеты кроме шапки и меню
        for widget in self.root.winfo_children():
            if widget not in (self.header_frame, self.menu_frame):
                widget.destroy()

    def show_partners(self):
        self.clear_main_area()
        frame = tk.Frame(self.root, bg=self.primary_bg, padx=20, pady=20)
        frame.grid(row=2, column=0, sticky="nsew")
        tk.Label(frame, text="Партнеры", font=self.title_font, bg=self.primary_bg, fg=self.accent_color)\
            .grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        # --- Поиск и сортировка ---
        search_frame = tk.Frame(frame, bg=self.primary_bg)
        search_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        tk.Label(search_frame, text="Поиск по наименованию:", font=self.label_font, bg=self.primary_bg).pack(side="left")
        search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=search_var, font=self.label_font, width=20).pack(side="left", padx=5)
        tk.Label(search_frame, text="Сортировка:", font=self.label_font, bg=self.primary_bg).pack(side="left", padx=(20,0))
        sort_options = ["Без сортировки", "По возрастанию", "По убыванию"]
        sort_var = tk.StringVar(value=sort_options[0])
        ttk.Combobox(search_frame, values=sort_options, textvariable=sort_var, state="readonly", width=18).pack(side="left", padx=5)
        def reload():
            self.show_partners_filtered(search_var.get(), sort_var.get(), parent=frame)
        tk.Button(search_frame, text="Поиск", font=self.label_font, command=reload).pack(side="left", padx=10)

        add_btn = tk.Button(frame, text="Добавить партнера", font=self.label_font, bg=self.accent_color, fg="white",
                            command=self.add_partner_dialog)
        add_btn.grid(row=2, column=1, sticky="e", pady=(0, 10))

        self.show_partners_filtered("", "Без сортировки", parent=frame)

    def show_partners_filtered(self, search, sort_mode, parent=None):
        # ...remove previous cards if parent is given...
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
        # Используем grid вместо pack
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Сортировка по рейтингу
        order_clause = ""
        if sort_mode == "По возрастанию":
            order_clause = "ORDER BY Рейтинг ASC"
        elif sort_mode == "По убыванию":
            order_clause = "ORDER BY Рейтинг DESC"

        query = f"""
        SELECT 
            ID,
            Тип_партнера,
            Наименование_партнера,
            Директор,
            Электронная_почта_партнера,
            Телефон_партнера,
            Юридический_адрес_партнера,
            ИНН,
            Рейтинг
        FROM Partners_import
        WHERE (? = '' OR Наименование_партнера LIKE ?)
        {order_clause}
        """
        params = (search, f"%{search}%")
        rows = self.db.execute_query(query, params)

        if not rows:
            tk.Label(scrollable_frame, text="Нет данных", font=self.label_font, bg=self.primary_bg).pack()
            return

        for partner in rows:
            card = tk.Frame(scrollable_frame, bg=self.primary_bg, highlightbackground="#888", highlightthickness=1, bd=0)
            card.pack(fill="x", pady=10, padx=5)
            left = tk.Frame(card, bg=self.primary_bg)
            left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            right = tk.Frame(card, bg=self.primary_bg)
            right.pack(side="right", fill="y", padx=10, pady=10)

            # Левая часть карточки
            tk.Label(left, text=f"ID: {partner[0]}", font=self.card_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            tk.Label(left, text=f"Тип: {partner[1]}", font=self.card_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            tk.Label(left, text=f"Наименование: {partner[2]}", font=self.card_title_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            tk.Label(left, text=f"Директор: {partner[3]}", font=self.card_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            tk.Label(left, text=f"Email: {partner[4]}", font=self.card_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            tk.Label(left, text=f"Телефон: {partner[5]}", font=self.card_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            tk.Label(left, text=f"Юр. адрес: {partner[6]}", font=self.card_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            tk.Label(left, text=f"ИНН: {partner[7]}", font=self.card_font, bg=self.primary_bg, anchor="w").pack(anchor="w")

            # Правая часть карточки
            tk.Label(right, text="Рейтинг", font=self.card_title_font, bg=self.primary_bg, anchor="e").pack(anchor="e")
            rating_var = tk.IntVar(value=partner[8])
            rating_spin = tk.Spinbox(right, from_=0, to=10, width=3, font=self.card_font, textvariable=rating_var, justify="center")
            rating_spin.pack(anchor="e", pady=(0, 5))

            def save_rating(partner_id=partner[0], var=rating_var):
                try:
                    new_rating = int(var.get())
                    self.db.execute_query("UPDATE Partners_import SET Рейтинг=? WHERE ID=?", (new_rating, partner_id))
                    messagebox.showinfo("Успех", "Рейтинг обновлен")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка обновления рейтинга: {e}")

            tk.Button(right, text="Сохранить", font=self.label_font, bg=self.accent_color, fg="white",
                      command=save_rating).pack(anchor="e", pady=(0, 5))

            tk.Button(right, text="Редактировать", font=self.label_font, bg="#888", fg="white",
                      command=lambda p=partner: self.edit_partner_dialog(p)).pack(anchor="e", pady=(0, 5))

            def confirm_and_delete_partner(pid=partner[0]):
                if messagebox.askyesno("Подтвердите", "Удалить партнера?"):
                    self.db.execute_query("DELETE FROM Partners_import WHERE ID=?", (pid,))
                    messagebox.showinfo("Удалено", "Партнер удален")
                    self.show_partners()

            tk.Button(right, text="Удалить", font=self.label_font, bg="#c0392b", fg="white",
                      command=confirm_and_delete_partner).pack(anchor="e", pady=(0, 5))

        # --- Прокрутка колесом мыши только для этого canvas ---
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # Сделать frame адаптивным по ширине
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig("all", width=e.width))

    def add_partner_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить партнера")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.primary_bg)
        fields = [
            ("Тип партнера", ""),
            ("Наименование", ""),
            ("Директор", ""),
            ("Email", ""),
            ("Телефон", ""),
            ("Юр. адрес", ""),
            ("ИНН", ""),
            ("Рейтинг", 0)
        ]
        entries = []
        for idx, (label, default) in enumerate(fields):
            tk.Label(dialog, text=label, font=self.label_font, bg=self.primary_bg).grid(row=idx, column=0, sticky="e", pady=3, padx=5)
            if label == "Рейтинг":
                var = tk.IntVar(value=default)
                entry = tk.Spinbox(dialog, from_=0, to=10, width=3, font=self.label_font, textvariable=var)
            else:
                var = tk.StringVar(value=default)
                entry = tk.Entry(dialog, font=self.label_font, textvariable=var)
            entry.grid(row=idx, column=1, pady=3, padx=5, sticky="ew")
            entries.append((label, var))
        dialog.grid_columnconfigure(1, weight=1)

        def save():
            values = [v.get() for _, v in entries]
            try:
                self.db.execute_query(
                    "INSERT INTO Partners_import (Тип_партнера, Наименование_партнера, Директор, Электронная_почта_партнера, Телефон_партнера, Юридический_адрес_партнера, ИНН, Рейтинг) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    tuple(values)
                )
                messagebox.showinfo("Успех", "Партнер добавлен")
                dialog.destroy()
                self.show_partners()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка добавления: {e}")

        tk.Button(dialog, text="Сохранить", font=self.label_font, bg=self.accent_color, fg="white", command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def edit_partner_dialog(self, partner):
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать партнера")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.primary_bg)
        labels = [
            "Тип партнера", "Наименование", "Директор", "Email", "Телефон", "Юр. адрес", "ИНН", "Рейтинг"
        ]
        db_fields = [
            "Тип_партнера", "Наименование_партнера", "Директор", "Электронная_почта_партнера",
            "Телефон_партнера", "Юридический_адрес_партнера", "ИНН", "Рейтинг"
        ]
        entries = []
        for idx, label in enumerate(labels):
            tk.Label(dialog, text=label, font=self.label_font, bg=self.primary_bg).grid(row=idx, column=0, sticky="e", pady=3, padx=5)
            if label == "Рейтинг":
                var = tk.IntVar(value=partner[8])
                entry = tk.Spinbox(dialog, from_=0, to=10, width=3, font=self.label_font, textvariable=var)
            else:
                var = tk.StringVar(value=partner[idx+1])
                entry = tk.Entry(dialog, font=self.label_font, textvariable=var)
            entry.grid(row=idx, column=1, pady=3, padx=5, sticky="ew")
            entries.append(var)
        dialog.grid_columnconfigure(1, weight=1)

        def save():
            values = [v.get() for v in entries]
            try:
                self.db.execute_query(
                    f"UPDATE Partners_import SET {', '.join([f'{f}=?' for f in db_fields])} WHERE ID=?",
                    tuple(values) + (partner[0],)
                )
                messagebox.showinfo("Успех", "Партнер обновлен")
                dialog.destroy()
                self.show_partners()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка обновления: {e}")

        tk.Button(dialog, text="Сохранить", font=self.label_font, bg=self.accent_color, fg="white", command=save).grid(row=len(labels), column=0, columnspan=2, pady=10)

    def show_products(self):
        self.clear_main_area()
        frame = tk.Frame(self.root, bg=self.primary_bg, padx=20, pady=20)
        frame.grid(row=2, column=0, sticky="nsew")
        tk.Label(frame, text="Продукция", font=self.title_font, bg=self.primary_bg, fg=self.accent_color)\
            .grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        search_frame = tk.Frame(frame, bg=self.primary_bg)
        search_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        tk.Label(search_frame, text="Поиск по наименованию:", font=self.label_font, bg=self.primary_bg).pack(side="left")
        search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=search_var, font=self.label_font, width=20).pack(side="left", padx=5)
        tk.Label(search_frame, text="Сортировка:", font=self.label_font, bg=self.primary_bg).pack(side="left", padx=(20,0))
        sort_options = ["Без сортировки", "По возрастанию", "По убыванию"]
        sort_var = tk.StringVar(value=sort_options[0])
        ttk.Combobox(search_frame, values=sort_options, textvariable=sort_var, state="readonly", width=18).pack(side="left", padx=5)
        def reload():
            self.show_products_filtered(search_var.get(), sort_var.get(), parent=frame)
        tk.Button(search_frame, text="Поиск", font=self.label_font, command=reload).pack(side="left", padx=10)

        add_btn = tk.Button(frame, text="Добавить продукцию", font=self.label_font, bg=self.accent_color, fg="white",
                            command=self.add_product_dialog)
        add_btn.grid(row=2, column=1, sticky="e", pady=(0, 10))

        self.show_products_filtered("", "Без сортировки", parent=frame)

    def show_products_filtered(self, search, sort_mode, parent=None):
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

        # Сортировка по цене
        order_clause = ""
        if sort_mode == "По возрастанию":
            order_clause = "ORDER BY p.Минимальная_стоимость_для_партнера ASC"
        elif sort_mode == "По убыванию":
            order_clause = "ORDER BY p.Минимальная_стоимость_для_партнера DESC"

        query = f"""
        SELECT p.ID, p.Наименование_продукции, p.Артикул, p.Минимальная_стоимость_для_партнера, t.Тип_продукции, p.Тип_продукции
        FROM Products_import p
        JOIN Product_type_import t ON p.Тип_продукции = t.ID
        WHERE (? = '' OR p.Наименование_продукции LIKE ?)
        {order_clause}
        """
        params = (search, f"%{search}%")
        rows = self.db.execute_query(query, params)

        if not rows:
            tk.Label(scrollable_frame, text="Нет данных", font=self.label_font, bg=self.primary_bg).pack()
            return

        for product in rows:
            card = tk.Frame(scrollable_frame, bg=self.primary_bg, highlightbackground="#888", highlightthickness=1, bd=0)
            card.pack(fill="x", pady=10, padx=5)
            left = tk.Frame(card, bg=self.primary_bg)
            left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            right = tk.Frame(card, bg=self.primary_bg)
            right.pack(side="right", fill="y", padx=10, pady=10)

            tk.Label(left, text=product[1], font=self.card_title_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            tk.Label(left, text=f"Артикул: {product[2]}", font=self.card_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            tk.Label(left, text=f"Тип: {product[4]}", font=self.card_font, bg=self.primary_bg, anchor="w").pack(anchor="w")

            tk.Label(right, text="Цена", font=self.card_title_font, bg=self.primary_bg, anchor="e").pack(anchor="e")
            tk.Label(right, text=f"{product[3]}", font=self.card_font, bg=self.primary_bg, anchor="e").pack(anchor="e")

            tk.Button(right, text="Редактировать", font=self.label_font, bg="#888", fg="white",
                      command=lambda p=product: self.edit_product_dialog(p)).pack(anchor="e", pady=(10, 0))

            def confirm_and_delete_product(pid=product[0]):
                if messagebox.askyesno("Подтвердите", "Удалить продукцию?"):
                    self.db.execute_query("DELETE FROM Products_import WHERE ID=?", (pid,))
                    messagebox.showinfo("Удалено", "Продукция удалена")
                    self.show_products()

            tk.Button(right, text="Удалить", font=self.label_font, bg="#c0392b", fg="white",
                      command=confirm_and_delete_product).pack(anchor="e", pady=(0, 5))

        # --- Прокрутка колесом мыши только для этого canvas ---
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # Сделать frame адаптивным по ширине
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig("all", width=e.width))

    def add_product_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить продукцию")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.primary_bg)

        # Получить список типов продукции
        type_rows = self.db.execute_query("SELECT ID, Тип_продукции FROM Product_type_import")
        type_names = [row[1] for row in type_rows] if type_rows else []
        type_ids = {row[1]: row[0] for row in type_rows} if type_rows else {}

        # Генерация артикула
        def generate_article():
            import random, string
            article = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            article_var.set(article)

        fields = [
            ("Наименование", ""),
            ("Артикул", ""),
            ("Мин. стоимость", ""),
            ("Тип продукции", type_names[0] if type_names else "")
        ]
        entries = []
        name_var = tk.StringVar(value=fields[0][1])
        article_var = tk.StringVar(value=fields[1][1])
        price_var = tk.StringVar(value=fields[2][1])
        type_var = tk.StringVar(value=fields[3][1])

        tk.Label(dialog, text="Наименование", font=self.label_font, bg=self.primary_bg).grid(row=0, column=0, sticky="e", pady=3, padx=5)
        tk.Entry(dialog, font=self.label_font, textvariable=name_var).grid(row=0, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Артикул", font=self.label_font, bg=self.primary_bg).grid(row=1, column=0, sticky="e", pady=3, padx=5)
        art_frame = tk.Frame(dialog, bg=self.primary_bg)
        art_frame.grid(row=1, column=1, sticky="ew", pady=3, padx=5)
        art_entry = tk.Entry(art_frame, font=self.label_font, textvariable=article_var)
        art_entry.pack(side="left", fill="x", expand=True)
        tk.Button(art_frame, text="Сгенерировать", font=self.label_font, bg=self.accent_color, fg="white", command=generate_article).pack(side="left", padx=(5,0))

        tk.Label(dialog, text="Мин. стоимость", font=self.label_font, bg=self.primary_bg).grid(row=2, column=0, sticky="e", pady=3, padx=5)
        tk.Entry(dialog, font=self.label_font, textvariable=price_var).grid(row=2, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Тип продукции", font=self.label_font, bg=self.primary_bg).grid(row=3, column=0, sticky="e", pady=3, padx=5)
        type_combo = ttk.Combobox(dialog, font=self.label_font, values=type_names, textvariable=type_var, state="readonly")
        type_combo.grid(row=3, column=1, pady=3, padx=5, sticky="ew")
        dialog.grid_columnconfigure(1, weight=1)

        def save():
            name = name_var.get()
            article = article_var.get()
            price = price_var.get()
            type_name = type_var.get()
            if not name or not article or not price or not type_name:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return
            type_id = type_ids.get(type_name)
            if not type_id:
                messagebox.showerror("Ошибка", "Тип продукции не найден")
                return
            try:
                self.db.execute_query(
                    "INSERT INTO Products_import (Наименование_продукции, Артикул, Минимальная_стоимость_для_партнера, Тип_продукции) VALUES (?, ?, ?, ?)",
                    (name, article, price, type_id)
                )
                messagebox.showinfo("Успех", "Продукция добавлена")
                dialog.destroy()
                self.show_products()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка добавления: {e}")

        tk.Button(dialog, text="Сохранить", font=self.label_font, bg=self.accent_color, fg="white", command=save).grid(row=4, column=0, columnspan=2, pady=10)

    def edit_product_dialog(self, product):
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать продукцию")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.primary_bg)

        # Получить список типов продукции
        type_rows = self.db.execute_query("SELECT ID, Тип_продукции FROM Product_type_import")
        type_names = [row[1] for row in type_rows] if type_rows else []
        type_ids = {row[1]: row[0] for row in type_rows} if type_rows else {}

        # Определить текущее название типа по ID
        current_type_name = ""
        for row in type_rows:
            if row[0] == product[5]:
                current_type_name = row[1]
                break

        name_var = tk.StringVar(value=product[1])
        article_var = tk.StringVar(value=product[2])
        price_var = tk.StringVar(value=product[3])
        type_var = tk.StringVar(value=current_type_name)

        tk.Label(dialog, text="Наименование", font=self.label_font, bg=self.primary_bg).grid(row=0, column=0, sticky="e", pady=3, padx=5)
        tk.Entry(dialog, font=self.label_font, textvariable=name_var).grid(row=0, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Артикул", font=self.label_font, bg=self.primary_bg).grid(row=1, column=0, sticky="e", pady=3, padx=5)
        tk.Entry(dialog, font=self.label_font, textvariable=article_var).grid(row=1, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Мин. стоимость", font=self.label_font, bg=self.primary_bg).grid(row=2, column=0, sticky="e", pady=3, padx=5)
        tk.Entry(dialog, font=self.label_font, textvariable=price_var).grid(row=2, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Тип продукции", font=self.label_font, bg=self.primary_bg).grid(row=3, column=0, sticky="e", pady=3, padx=5)
        type_combo = ttk.Combobox(dialog, font=self.label_font, values=type_names, textvariable=type_var, state="readonly")
        type_combo.grid(row=3, column=1, pady=3, padx=5, sticky="ew")
        dialog.grid_columnconfigure(1, weight=1)

        def save():
            name = name_var.get()
            article = article_var.get()
            price = price_var.get()
            type_name = type_var.get()
            if not name or not article or not price or not type_name:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return
            type_id = type_ids.get(type_name)
            if not type_id:
                messagebox.showerror("Ошибка", "Тип продукции не найден")
                return
            try:
                self.db.execute_query(
                    "UPDATE Products_import SET Наименование_продукции=?, Артикул=?, Минимальная_стоимость_для_партнера=?, Тип_продукции=? WHERE ID=?",
                    (name, article, price, type_id, product[0])
                )
                messagebox.showinfo("Успех", "Продукция обновлена")
                dialog.destroy()
                self.show_products()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка обновления: {e}")

        tk.Button(dialog, text="Сохранить", font=self.label_font, bg=self.accent_color, fg="white", command=save).grid(row=4, column=0, columnspan=2, pady=10)

    def show_requests(self):
        self.clear_main_area()
        frame = tk.Frame(self.root, bg=self.primary_bg, padx=20, pady=20)
        frame.grid(row=2, column=0, sticky="nsew")
        tk.Label(frame, text="Заявки", font=self.title_font, bg=self.primary_bg, fg=self.accent_color)\
            .grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        search_frame = tk.Frame(frame, bg=self.primary_bg)
        search_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        tk.Label(search_frame, text="Поиск по партнеру:", font=self.label_font, bg=self.primary_bg).pack(side="left")
        search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=search_var, font=self.label_font, width=20).pack(side="left", padx=5)
        tk.Label(search_frame, text="Сортировка:", font=self.label_font, bg=self.primary_bg).pack(side="left", padx=(20,0))
        sort_options = ["Без сортировки", "По возрастанию", "По убыванию"]
        sort_var = tk.StringVar(value=sort_options[0])
        ttk.Combobox(search_frame, values=sort_options, textvariable=sort_var, state="readonly", width=18).pack(side="left", padx=5)
        def reload():
            self.show_requests_filtered(search_var.get(), sort_var.get(), parent=frame)
        tk.Button(search_frame, text="Поиск", font=self.label_font, command=reload).pack(side="left", padx=10)

        add_btn = tk.Button(frame, text="Создать заявку", font=self.label_font, bg=self.accent_color, fg="white",
                            command=self.add_request_dialog)
        add_btn.grid(row=2, column=1, sticky="e", pady=(0, 10))

        self.show_requests_filtered("", "Без сортировки", parent=frame)

    def show_requests_filtered(self, search, sort_mode, parent=None):
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

        # Сортировка по сумме (количество * цена)
        order_clause = ""
        if sort_mode == "По возрастанию":
            order_clause = "ORDER BY (r.Количество_продукции * p.Минимальная_стоимость_для_партнера) ASC"
        elif sort_mode == "По убыванию":
            order_clause = "ORDER BY (r.Количество_продукции * p.Минимальная_стоимость_для_партнера) DESC"

        query = f"""
        SELECT r.ID, p.Наименование_продукции, pr.Наименование_партнера, r.Количество_продукции, p.Минимальная_стоимость_для_партнера
        FROM Partner_products_request_import r
        JOIN Products_import p ON r.Продукция = p.ID
        JOIN Partners_import pr ON r.Наименование_партнера = pr.ID
        WHERE (? = '' OR pr.Наименование_партнера LIKE ?)
        {order_clause}
        """
        params = (search, f"%{search}%")
        rows = self.db.execute_query(query, params)

        if not rows:
            tk.Label(scrollable_frame, text="Нет данных", font=self.label_font, bg=self.primary_bg).pack()
            return

        for req in rows:
            req_id, prod_name, partner_name, qty, price = req
            try:
                qty_val = float(qty)
                price_val = float(price)
                total = qty_val * price_val
            except Exception:
                total = "Ошибка"

            card = tk.Frame(scrollable_frame, bg=self.primary_bg, highlightbackground="#888", highlightthickness=1, bd=0)
            card.pack(fill="x", pady=10, padx=5)
            left = tk.Frame(card, bg=self.primary_bg)
            left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            right = tk.Frame(card, bg=self.primary_bg)
            right.pack(side="right", fill="y", padx=10, pady=10)

            # Левая часть карточки
            tk.Label(left, text=f"ID: {req_id}", font=self.card_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            tk.Label(left, text=f"Продукция: {prod_name}", font=self.card_title_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            tk.Label(left, text=f"Партнер: {partner_name}", font=self.card_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            tk.Label(left, text=f"Количество: {qty}", font=self.card_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            tk.Label(left, text=f"Цена за ед.: {price}", font=self.card_font, bg=self.primary_bg, anchor="w").pack(anchor="w")
            tk.Label(left, text=f"Сумма: {total}", font=self.card_title_font, bg=self.primary_bg, anchor="w").pack(anchor="w")

            # Правая часть карточки
            def confirm_and_execute(req_id=req_id):
                if messagebox.askyesno("Подтвердите", "Выполнить заявку?"):
                    self.db.execute_query("UPDATE Partner_products_request_import SET Статус='Выполнена' WHERE ID=?", (req_id,))
                    messagebox.showinfo("Успех", "Заявка выполнена")
                    self.show_requests()

            def confirm_and_delete(req_id=req_id):
                if messagebox.askyesno("Подтвердите", "Отклонить и удалить заявку?"):
                    self.db.execute_query("DELETE FROM Partner_products_request_import WHERE ID=?", (req_id,))
                    messagebox.showinfo("Удалено", "Заявка удалена")
                    self.show_requests()

            tk.Button(right, text="Выполнить", font=self.label_font, bg=self.accent_color, fg="white",
                      command=confirm_and_execute).pack(anchor="e", pady=(0, 5))
            tk.Button(right, text="Отклонить", font=self.label_font, bg="#888", fg="white",
                      command=confirm_and_delete).pack(anchor="e", pady=(0, 5))

        # --- Прокрутка колесом мыши только для этого canvas ---
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # Сделать frame адаптивным по ширине
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig("all", width=e.width))

    def add_request_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Создать заявку")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.primary_bg)

        # Получить список продукции и партнеров
        products = self.db.execute_query("SELECT ID, Наименование_продукции FROM Products_import")
        partners = self.db.execute_query("SELECT ID, Наименование_партнера FROM Partners_import")
        product_names = [p[1] for p in products] if products else []
        partner_names = [p[1] for p in partners] if partners else []
        product_ids = {p[1]: p[0] for p in products} if products else {}
        partner_ids = {p[1]: p[0] for p in partners} if partners else {}

        product_var = tk.StringVar(value=product_names[0] if product_names else "")
        partner_var = tk.StringVar(value=partner_names[0] if partner_names else "")
        qty_var = tk.StringVar(value="1")

        tk.Label(dialog, text="Продукция", font=self.label_font, bg=self.primary_bg).grid(row=0, column=0, sticky="e", pady=3, padx=5)
        product_combo = ttk.Combobox(dialog, font=self.label_font, values=product_names, textvariable=product_var, state="readonly")
        product_combo.grid(row=0, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Партнер", font=self.label_font, bg=self.primary_bg).grid(row=1, column=0, sticky="e", pady=3, padx=5)
        partner_combo = ttk.Combobox(dialog, font=self.label_font, values=partner_names, textvariable=partner_var, state="readonly")
        partner_combo.grid(row=1, column=1, pady=3, padx=5, sticky="ew")

        tk.Label(dialog, text="Количество", font=self.label_font, bg=self.primary_bg).grid(row=2, column=0, sticky="e", pady=3, padx=5)
        tk.Entry(dialog, font=self.label_font, textvariable=qty_var).grid(row=2, column=1, pady=3, padx=5, sticky="ew")

        dialog.grid_columnconfigure(1, weight=1)

        def save():
            prod_name = product_var.get()
            partner_name = partner_var.get()
            qty = qty_var.get()
            prod_id = product_ids.get(prod_name)
            partner_id = partner_ids.get(partner_name)
            if not prod_id or not partner_id or not qty:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return
            try:
                self.db.execute_query(
                    "INSERT INTO Partner_products_request_import (Продукция, Наименование_партнера, Количество_продукции) VALUES (?, ?, ?)",
                    (prod_id, partner_id, qty)
                )
                messagebox.showinfo("Успех", "Заявка создана")
                dialog.destroy()
                self.show_requests()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка создания заявки: {e}")

        tk.Button(dialog, text="Сохранить", font=self.label_font, bg=self.accent_color, fg="white", command=save).grid(row=3, column=0, columnspan=2, pady=10)

    def show_warehouse_materials(self):
        self.clear_main_area()
        frame = tk.Frame(self.root, bg=self.primary_bg, padx=20, pady=20)
        frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tk.Label(frame, text="Склад и материалы", font=self.title_font, bg=self.primary_bg, fg=self.accent_color).pack(anchor="w", pady=(0, 15))

        # Получаем данные
        query = """
        SELECT m.Наименование, m.Количество_на_складе, t.Тип_материала, s.Наименование, m.Количество_в_упаковке, m.Единица_измерения, m.Описание, m.Стоимость, m.Количество_на_складе, m.Минимальное_количество
        FROM Materials_import m
        JOIN Material_type_import t ON m.Тип = t.ID
        JOIN Suppliers_import s ON m.Поставщик = s.ID
        """
        rows = self.db.execute_query(query)

        if not rows:
            tk.Label(frame, text="Нет данных", font=self.label_font, bg=self.primary_bg).pack()
            return

        tree = ttk.Treeview(frame, columns=(
            "ID", "Тип", "Наименование", "Поставщик", "Кол-во в упаковке", "Ед. изм.", "Описание", "Стоимость", "Кол-во на складе", "Мин. кол-во"
        ), show="headings")
        for col in tree["columns"]:
            tree.heading(col, text=col)
        tree.pack(fill=tk.BOTH, expand=True)

        for row in rows:
            tree.insert("", tk.END, values=row)

    def show_production(self):
        self.clear_main_area()
        frame = tk.Frame(self.root, bg=self.primary_bg, padx=20, pady=20)
        frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tk.Label(frame, text="Производство", font=self.title_font, bg=self.primary_bg, fg=self.accent_color).pack(anchor="w", pady=(0, 15))

        # Получаем данные
        query = """
        SELECT p.ID, pr.Наименование_продукции, p.Номер_цеха, p.Время_изготовления, p.Себестоимость, p.Количество_человек, p.Необходимые_материалы
        FROM Production_import p
        JOIN Products_import pr ON p.Продукция = pr.ID
        """
        rows = self.db.execute_query(query)

        if not rows:
            tk.Label(frame, text="Нет данных", font=self.label_font, bg=self.primary_bg).pack()
            return

        tree = ttk.Treeview(frame, columns=(
            "ID", "Продукция", "Цех", "Время изготовления", "Себестоимость", "Кол-во сотрудников", "Необходимые материалы"
        ), show="headings")
        for col in tree["columns"]:
            tree.heading(col, text=col)
        tree.pack(fill=tk.BOTH, expand=True)

        for row in rows:
            tree.insert("", tk.END, values=row)

    def show_employees(self):
        self.clear_main_area()
        frame = tk.Frame(self.root, bg=self.primary_bg, padx=20, pady=20)
        frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tk.Label(frame, text="Сотрудники", font=self.title_font, bg=self.primary_bg, fg=self.accent_color).pack(anchor="w", pady=(0, 15))

        # Получаем данные
        query = """
        SELECT ID, ФИО, Дата_рождения, Паспортные_данные, Банковские_реквизиты, Наличие_семьи, Состояние_здоровья
        FROM Employees_import
        """
        rows = self.db.execute_query(query)

        if not rows:
            tk.Label(frame, text="Нет данных", font=self.label_font, bg=self.primary_bg).pack()
            return

        tree = ttk.Treeview(frame, columns=(
            "ID", "ФИО", "Дата рождения", "Паспорт", "Банк. реквизиты", "Семья", "Здоровье"
        ), show="headings")
        for col in tree["columns"]:
            tree.heading(col, text=col)
        tree.pack(fill=tk.BOTH, expand=True)

        for row in rows:
            tree.insert("", tk.END, values=row)

    def show_suppliers(self):
        self.clear_main_area()
        frame = tk.Frame(self.root, bg=self.primary_bg, padx=20, pady=20)
        frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tk.Label(frame, text="Поставщики", font=self.title_font, bg=self.primary_bg, fg=self.accent_color).pack(anchor="w", pady=(0, 15))

        # Получаем данные
        query = """
        SELECT s.ID, t.Тип_поставщика, s.Наименование, s.ИНН, s.История_поставок
        FROM Suppliers_import s
        JOIN Supplier_type_import t ON s.Тип = t.ID
        """
        rows = self.db.execute_query(query)

        if not rows:
            tk.Label(frame, text="Нет данных", font=self.label_font, bg=self.primary_bg).pack()
            return

        tree = ttk.Treeview(frame, columns=(
            "ID", "Тип", "Наименование", "ИНН", "История поставок"
        ), show="headings")
        for col in tree["columns"]:
            tree.heading(col, text=col)
        tree.pack(fill=tk.BOTH, expand=True)

        for row in rows:
            tree.insert("", tk.END, values=row)

    def show_users(self):
        self.clear_main_area()
        frame = tk.Frame(self.root, bg=self.primary_bg, padx=20, pady=20)
        frame.grid(row=2, column=0, sticky="nsew")
        tk.Label(frame, text="Пользователи", font=self.title_font, bg=self.primary_bg, fg=self.accent_color)\
            .grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        # --- Только поиск ---
        search_frame = tk.Frame(frame, bg=self.primary_bg)
        search_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        tk.Label(search_frame, text="Поиск по логину:", font=self.label_font, bg=self.primary_bg).pack(side="left")
        search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=search_var, font=self.label_font, width=20).pack(side="left", padx=5)
        def reload():
            self.show_users_filtered(search_var.get(), parent=frame)
        tk.Button(search_frame, text="Поиск", font=self.label_font, command=reload).pack(side="left", padx=10)

        add_btn = tk.Button(frame, text="Добавить пользователя", font=self.label_font, bg=self.accent_color, fg="white",
                            command=self.add_user_dialog)
        add_btn.grid(row=2, column=1, sticky="e", pady=(0, 10))

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
    root = tk.Tk()
    app = App(root)
    root.mainloop()
