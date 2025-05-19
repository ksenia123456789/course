import tkinter as tk
from tkinter import ttk, messagebox
from data.scheduler import find_matching_slots
from data.user_slots import add_user_time_slot, book_appointment, get_user_slots, load_graph, save_graph
from datetime import datetime
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from rdflib import Literal, RDF, URIRef, Namespace
from rdflib.namespace import XSD

EX = Namespace("http://example.org/medical#")

class PlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Медицинский Планировщик")
        self.root.geometry("900x800")
        self.root.configure(bg="#f5f7fa")
        try:
            self.root.iconbitmap("data/medical.ico")
        except:
            pass

        # Инициализация стилей
        style = ttk.Style("flatly")
        style.configure("TButton", font=("Arial", 11, "bold"))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
        style.configure("Treeview", font=("Arial", 11), rowheight=40, foreground="black")
        style.map("Treeview", background=[("selected", "#e9ecef")])

        # Создаём Canvas с прокруткой для всего содержимого
        self.canvas = tk.Canvas(self.root, bg="#f5f7fa")
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        # Настраиваем Canvas
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Размещаем Canvas и Scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Создаём окно внутри Canvas
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Обработка прокрутки
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Секция для добавления занятия
        activity_frame = ttk.Frame(self.scrollable_frame, style="Card", padding=15)
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

        # Таблица пользовательских занятий с прокруткой
        tree_frame = ttk.Frame(activity_frame)
        tree_frame.pack(pady=10, fill="both", expand=True)
        self.schedule_tree = ttk.Treeview(tree_frame, columns=("Занятие", "Дата", "Время", "Действие"), show="headings",
                                          style="Treeview")
        self.schedule_tree.heading("Занятие", text="Занятие")
        self.schedule_tree.heading("Дата", text="Дата")
        self.schedule_tree.heading("Время", text="Время")
        self.schedule_tree.heading("Действие", text="Действие")
        self.schedule_tree.column("Занятие", width=300)
        self.schedule_tree.column("Дата", width=150)
        self.schedule_tree.column("Время", width=200)
        self.schedule_tree.column("Действие", width=140)
        self.schedule_tree.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=self.schedule_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.schedule_tree.configure(yscrollcommand=scrollbar.set)
        self.schedule_tree.tag_configure("oddrow", background="#ffffff")
        self.schedule_tree.tag_configure("evenrow", background="#f8f9fa")
        self.schedule_buttons = {}
        self.schedule_tree.bind("<Configure>", self.update_buttons_on_scroll)
        self.schedule_tree.bind("<MouseWheel>", self.update_buttons_on_scroll)
        self.update_schedule()

        # Секция для записи к врачу
        doctor_frame = ttk.Frame(self.scrollable_frame, style="Card", padding=15)
        doctor_frame.pack(pady=15, padx=15, fill="x")

        tk.Label(doctor_frame, text="Запись к врачу", font=("Arial", 16, "bold"), fg="#333333", bg="#ffffff").pack(
            anchor="w", pady=5)
        tk.Label(doctor_frame, text="Выберите специализацию:", font=("Arial", 11), fg="#333333", bg="#ffffff").pack(
            anchor="w", pady=5)
        self.specialty_var = tk.StringVar()
        specialties = ["Кардиолог", "Терапевт", "Невролог", "Хирург", "Ортопед", "Педиатр", "Офтальмолог", "Дерматолог"]
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
        self.result_tree.column("Врач", width=300)
        self.result_tree.column("Поликлиника", width=200)
        self.result_tree.column("Время", width=250)
        self.result_tree.column("Действие", width=140)
        self.result_tree.pack(pady=10, fill="both", expand=True)

        self.result_tree.tag_configure("oddrow", background="#ffffff")
        self.result_tree.tag_configure("evenrow", background="#f8f9fa")

        self.buttons = []

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def check_overlap(self, new_start, new_end):
        existing_slots = get_user_slots()
        new_start_dt = datetime.fromisoformat(new_start)
        new_end_dt = datetime.fromisoformat(new_end)

        for slot in existing_slots:
            exist_start = datetime.fromisoformat(slot['time_start'])
            exist_end = datetime.fromisoformat(slot['time_end'])
            if not (new_end_dt <= exist_start or new_start_dt >= exist_end):
                return True
        return False

    def update_schedule(self):
        for item in self.schedule_tree.get_children():
            self.schedule_tree.delete(item)
        for button in self.schedule_buttons.values():
            button.destroy()
        self.schedule_buttons.clear()

        slots = get_user_slots()
        slots.sort(key=lambda x: datetime.fromisoformat(x['time_start']))
        print("Updating schedule with slots:", slots)

        for i, slot in enumerate(slots):
            start = datetime.fromisoformat(slot['time_start'])
            end = datetime.fromisoformat(slot['time_end'])
            date = start.strftime('%Y-%m-%d')
            time = f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}"
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.schedule_tree.insert("", "end", values=(slot['activity'], date, time, ""), tags=(tag,))

        self.root.after(100, self.add_schedule_buttons)

    def add_schedule_buttons(self):
        visible_items = self.schedule_tree.get_children()
        slots = get_user_slots()

        for item in visible_items:
            values = self.schedule_tree.item(item, "values")
            slot = next(s for s in slots if s['activity'] == values[0] and
                        datetime.fromisoformat(s['time_start']).strftime('%Y-%m-%d') == values[1])
            bbox = self.schedule_tree.bbox(item, column="Действие")
            print(f"Bbox for item {item}: {bbox}")

            if item in self.schedule_buttons:
                self.schedule_buttons[item].destroy()
                del self.schedule_buttons[item]

            if bbox:
                button = ttk.Button(self.schedule_tree, text="Удалить", style="danger.TButton",
                                   command=lambda s=slot: self.delete_activity(s))
                button.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
                self.schedule_buttons[item] = button
                print(f"Button created for {slot['activity']} at {slot['time_start']}")
            else:
                print(f"Skipped button for {slot['activity']} at {slot['time_start']}: empty bbox")

    def update_buttons_on_scroll(self, event):
        self.root.after(100, self.add_schedule_buttons)

    def delete_activity(self, slot):
        if not messagebox.askyesno("Подтверждение", f"Удалить занятие '{slot['activity']}' на {slot['time_start']}?"):
            return

        print(f"Deleting activity: {slot['activity']} at {slot['time_start']}")
        g = load_graph()
        slot_uri = None
        for s, p, o in g.triples((None, RDF.type, EX.UserTimeSlot)):
            if (s, EX.timeStart, Literal(slot['time_start'], datatype=XSD.dateTime)) in g and \
                    (s, EX.hasActivity, Literal(slot['activity'])) in g:
                slot_uri = s
                break

        if slot_uri:
            # Если это запись к врачу, восстанавливаем свободное время врача
            if slot['activity'].startswith("Запись к врачу"):
                doctor_slot_uri = g.value(slot_uri, EX.relatedDoctorSlot)
                if doctor_slot_uri:
                    g.set((doctor_slot_uri, EX.isFree, Literal(True, datatype=XSD.boolean)))
                    print(f"Restored DoctorTimeSlot: {doctor_slot_uri} to isFree=True")

            g.remove((slot_uri, None, None))
            save_graph(g)
            print(f"Removed UserTimeSlot: {slot_uri}")
            messagebox.showinfo("Успех", "Занятие удалено!")
            self.update_schedule()
            if self.specialty_var.get():
                self.find_slots()
        else:
            messagebox.showerror("Ошибка", "Не удалось найти занятие для удаления!")
            print(f"Failed to find UserTimeSlot for {slot['activity']} at {slot['time_start']}")

    def add_activity(self):
        activity = self.activity_entry.get()
        date = self.date_entry.get()
        start_time = self.start_time_entry.get()
        end_time = self.end_time_entry.get()

        if not (activity and date and start_time and end_time):
            messagebox.showwarning("Ошибка", "Заполните все поля!")
            return

        try:
            datetime.strptime(date, "%Y-%m-%d")
            datetime.strptime(start_time, "%H:%M")
            datetime.strptime(end_time, "%H:%M")
            start_datetime = f"{date}T{start_time}:00"
            end_datetime = f"{date}T{end_time}:00"
            datetime.fromisoformat(start_datetime)
            datetime.fromisoformat(end_datetime)

            if self.check_overlap(start_datetime, end_datetime):
                messagebox.showerror("Ошибка", "Время пересекается с существующим занятием!")
                return

            add_user_time_slot(start_datetime, end_datetime, activity, is_free=False)
            messagebox.showinfo("Успех", "Занятие добавлено!")
            self.activity_entry.delete(0, tk.END)
            self.date_entry.delete(0, tk.END)
            self.start_time_entry.delete(0, tk.END)
            self.end_time_entry.delete(0, tk.END)
            self.update_schedule()
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты (ГГГГ-ММ-ДД) или времени (ЧЧ:ММ)!")

    def find_slots(self):
        specialty = self.specialty_var.get()
        if not specialty:
            messagebox.showwarning("Ошибка", "Выберите специализацию!")
            return

        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        for button in self.buttons:
            button.destroy()
        self.buttons.clear()

        matches = find_matching_slots(specialty)
        print("Matches:", matches)

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
            self.root.update()
            bbox = self.result_tree.bbox(item, column="Действие")
            if bbox:
                button = ttk.Button(self.result_tree, text="Записаться", style="primary.Outline.TButton",
                                    command=lambda m=match: self.book_slot(m))
                button.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
                self.buttons.append(button)

    def book_slot(self, match):
        print("Booking slot:", match)
        start_datetime = match['time_start']
        end_datetime = match['time_end']
        if self.check_overlap(start_datetime, end_datetime):
            messagebox.showerror("Ошибка", "Время записи к врачу пересекается с существующим занятием!")
            return
        if messagebox.askyesno("Подтверждение",
                               f"Записаться к {match['doctor']} в {match['hospital']} на {match['time_start']}?"):
            # Формируем activity с именем врача и специализацией
            activity = f"Запись к врачу: {match['doctor']}, {match['specialty']}"
            book_appointment(match['doctor_uri'], match['slot_uri'], match['time_start'], match['time_end'], activity=activity)
            messagebox.showinfo("Успех", "Запись подтверждена!")
            self.find_slots()
            self.update_schedule()