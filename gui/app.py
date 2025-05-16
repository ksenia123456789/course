import tkinter as tk
from tkinter import ttk, messagebox
from data.scheduler import find_matching_slots
from data.user_slots import add_user_time_slot, book_appointment
from datetime import datetime
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class PlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Медицинский Планировщик")
        self.root.geometry("800x700")
        self.root.configure(bg="#f5f7fa")  # Мягкий серо-голубой фон
        try:
            self.root.iconbitmap("data/medical.ico")  # Иконка окна
        except:
            pass

        # Настройка стилей ttkbootstrap
        style = ttk.Style("flatly")
        style.configure("TButton", font=("Arial", 11, "bold"))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
        style.configure("Treeview", font=("Arial", 11), rowheight=35)
        style.map("Treeview", background=[("selected", "#e9ecef")])

        # Секция для добавления занятия
        activity_frame = ttk.Frame(root, style="Card", padding=15)
        activity_frame.pack(pady=15, padx=15, fill="x")

        tk.Label(activity_frame, text="Добавить занятие", font=("Arial", 16, "bold"), fg="#333333", bg="#ffffff").pack(
            anchor="w", pady=5)

        tk.Label(activity_frame, text="Род занятий:", font=("Arial", 11), fg="#333333", bg="#ffffff").pack(anchor="w",
                                                                                                           pady=5)
        self.activity_entry = ttk.Entry(activity_frame, font=("Arial", 11), width=50, style="primary")
        self.activity_entry.pack(pady=5, fill="x")

        tk.Label(activity_frame, text="Дата (ГГГГ-ММ-ДД):", font=("Arial", 11), fg="#333333", bg="#ffffff").pack(
            anchor="w", pady=5)
        self.date_entry = ttk.Entry(activity_frame, font=("Arial", 11), width=50, style="primary")
        self.date_entry.pack(pady=5, fill="x")
        tk.Label(activity_frame, text="Пример: 2025-05-16", font=("Arial", 10, "italic"), fg="#666666",
                 bg="#ffffff").pack(anchor="w", pady=2)

        tk.Label(activity_frame, text="Время начала (ЧЧ:ММ):", font=("Arial", 11), fg="#333333", bg="#ffffff").pack(
            anchor="w", pady=5)
        self.start_time_entry = ttk.Entry(activity_frame, font=("Arial", 11), width=50, style="primary")
        self.start_time_entry.pack(pady=5, fill="x")

        tk.Label(activity_frame, text="Время окончания (ЧЧ:ММ):", font=("Arial", 11), fg="#333333", bg="#ffffff").pack(
            anchor="w", pady=5)
        self.end_time_entry = ttk.Entry(activity_frame, font=("Arial", 11), width=50, style="primary")
        self.end_time_entry.pack(pady=5, fill="x")

        ttk.Button(activity_frame, text="Добавить занятие", style="primary.TButton", command=self.add_activity).pack(
            pady=15)

        # Секция для записи к врачу
        doctor_frame = ttk.Frame(root, style="Card", padding=15)
        doctor_frame.pack(pady=15, padx=15, fill="x")

        tk.Label(doctor_frame, text="Запись к врачу", font=("Arial", 16, "bold"), fg="#333333", bg="#ffffff").pack(
            anchor="w", pady=5)
        tk.Label(doctor_frame, text="Выберите специализацию:", font=("Arial", 11), fg="#333333", bg="#ffffff").pack(
            anchor="w", pady=5)
        self.specialty_var = tk.StringVar()
        specialties = ["Кардиолог", "Терапевт", "Невролог", "Хирург", "Ортопед"]
        self.specialty_combo = ttk.Combobox(doctor_frame, textvariable=self.specialty_var, values=specialties,
                                            font=("Arial", 11), width=48)
        self.specialty_combo.pack(pady=5, fill="x")

        ttk.Button(doctor_frame, text="Найти слоты", style="primary.TButton", command=self.find_slots).pack(pady=15)

        # Таблица для результатов
        self.result_tree = ttk.Treeview(doctor_frame, columns=("Врач", "Поликлиника", "Время", "Действие"),
                                        show="headings", style="Treeview")
        self.result_tree.heading("Врач", text="Врач")
        self.result_tree.heading("Поликлиника", text="Поликлиника")
        self.result_tree.heading("Время", text="Время")
        self.result_tree.heading("Действие", text="Действие")
        self.result_tree.column("Врач", width=200)
        self.result_tree.column("Поликлиника", width=170)
        self.result_tree.column("Время", width=220)
        self.result_tree.column("Действие", width=120)
        self.result_tree.pack(pady=10, fill="both", expand=True)

        # Чередование цветов строк
        self.result_tree.tag_configure("oddrow", background="#ffffff")
        self.result_tree.tag_configure("evenrow", background="#f8f9fa")

        # Список для хранения кнопок
        self.buttons = []

    def add_activity(self):
        """Обработчик добавления занятия."""
        activity = self.activity_entry.get()
        date = self.date_entry.get()
        start_time = self.start_time_entry.get()
        end_time = self.end_time_entry.get()

        if not (activity and date and start_time and end_time):
            messagebox.showwarning("Ошибка", "Заполните все поля!")
            return

        try:
            # Валидация формата даты (ГГГГ-ММ-ДД)
            datetime.strptime(date, "%Y-%m-%d")
            # Валидация формата времени (ЧЧ:ММ)
            datetime.strptime(start_time, "%H:%M")
            datetime.strptime(end_time, "%H:%M")
            start_datetime = f"{date}T{start_time}:00"
            end_datetime = f"{date}T{end_time}:00"
            datetime.fromisoformat(start_datetime)
            datetime.fromisoformat(end_datetime)
            add_user_time_slot(start_datetime, end_datetime, activity, is_free=False)
            messagebox.showinfo("Успех", "Занятие добавлено!")
            self.activity_entry.delete(0, tk.END)
            self.date_entry.delete(0, tk.END)
            self.start_time_entry.delete(0, tk.END)
            self.end_time_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты (ГГГГ-ММ-ДД) или времени (ЧЧ:ММ)!")

    def find_slots(self):
        """Обработчик поиска слотов."""
        specialty = self.specialty_var.get()
        if not specialty:
            messagebox.showwarning("Ошибка", "Выберите специализацию!")
            return

        # Очистка таблицы и кнопок
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        for button in self.buttons:
            button.destroy()
        self.buttons.clear()

        # Поиск слотов
        matches = find_matching_slots(specialty)
        print("Matches:", matches)  # Отладочный вывод

        # Отображение результатов
        if not matches:
            messagebox.showinfo("Результат", f"Нет доступных слотов для {specialty}.")
            return

        for i, match in enumerate(matches):
            start = datetime.fromisoformat(match['time_start'])
            end = datetime.fromisoformat(match['time_end'])
            time = f"{start.strftime('%d %b %Y, %H:%M')} - {end.strftime('%H:%M')}"
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            item = self.result_tree.insert("", "end", values=(match['doctor'], match['hospital'], time, ""),
                                           tags=(tag,))
            # Получаем координаты ячейки для кнопки
            self.root.update()  # Обновляем интерфейс
            bbox = self.result_tree.bbox(item, column="Действие")
            if bbox:
                button = ttk.Button(self.result_tree, text="Записаться", style="primary.Outline.TButton",
                                    command=lambda m=match: self.book_slot(m))
                button.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
                self.buttons.append(button)

    def book_slot(self, match):
        """Обработчик записи на слот."""
        print("Booking slot:", match)  # Отладочный вывод
        if messagebox.askyesno("Подтверждение",
                               f"Записаться к {match['doctor']} в {match['hospital']} на {match['time_start']}?"):
            book_appointment(match['doctor_uri'], match['slot_uri'], match['time_start'], match['time_end'])
            messagebox.showinfo("Успех", "Запись подтверждена!")
            self.find_slots()  # Обновить таблицу