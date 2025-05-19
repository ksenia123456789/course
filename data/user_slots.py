from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import XSD
import os

EX = Namespace("http://example.org/medical#")

def get_data_file_path():
    """Возвращает абсолютный путь к файлу data.ttl."""
    current_file_path = os.path.abspath(os.path.dirname(__file__))
    data_file_path = os.path.join(current_file_path, "data.ttl")
    print(f"Формируемый путь к data.ttl: {data_file_path}")
    return data_file_path

def load_graph():
    g = Graph()
    data_file_path = get_data_file_path()
    if os.path.exists(data_file_path):
        print(f"Загружаем граф из {data_file_path}")
        g.parse(data_file_path, format="turtle")
    else:
        print(f"Файл {data_file_path} не найден, создаём новый граф")
    return g

def save_graph(g):
    """Сохраняет граф в файл, создавая директорию data, если её нет."""
    data_file_path = get_data_file_path()
    data_dir = os.path.dirname(data_file_path)
    if not os.path.exists(data_dir):
        print(f"Создаём директорию {data_dir}")
        os.makedirs(data_dir)
    print(f"Сохраняем граф в {data_file_path}")
    g.serialize(destination=data_file_path, format="turtle")

def initialize_user_slots(g):
    """Инициализация пользовательских временных слотов."""
    user_slots = [
        ("UserTimeSlot1", "Учёба", "2025-05-13T08:00:00", "2025-05-13T09:00:00"),
        ("UserTimeSlot2", "Работа", "2025-05-13T15:00:00", "2025-05-13T17:00:00"),
        ("UserTimeSlot3", "Спорт", "2025-05-14T09:00:00", "2025-05-14T10:00:00"),
        ("UserTimeSlot4", "Встреча с друзьями", "2025-05-14T18:00:00", "2025-05-14T19:00:00"),
        ("UserTimeSlot5", "Чтение", "2025-05-15T11:00:00", "2025-05-15T12:00:00"),
        ("UserTimeSlot6", "Прогулка", "2025-05-13T10:00:00", "2025-05-13T11:00:00"),
        ("UserTimeSlot7", "Работа", "2025-05-14T14:00:00", "2025-05-14T15:00:00"),
        ("UserTimeSlot8", "Йога", "2025-05-19T10:00:00", "2025-05-19T11:00:00"),
    ]

    for slot_id, activity, start, end in user_slots:
        slot = URIRef(EX + slot_id)
        g.add((slot, RDF.type, EX.UserTimeSlot))
        g.add((slot, EX.hasActivity, Literal(activity)))
        g.add((slot, EX.isFree, Literal(False, datatype=XSD.boolean)))
        g.add((slot, EX.timeStart, Literal(start, datatype=XSD.dateTime)))
        g.add((slot, EX.timeEnd, Literal(end, datatype=XSD.dateTime)))

def add_user_time_slot(time_start, time_end, activity, is_free=True):
    g = load_graph()
    slot_uri = EX[f"UserTimeSlot{len(list(g.subjects(RDF.type, EX.UserTimeSlot))) + 1}"]
    g.add((slot_uri, RDF.type, EX.UserTimeSlot))
    g.add((slot_uri, EX.timeStart, Literal(time_start, datatype=XSD.dateTime)))
    g.add((slot_uri, EX.timeEnd, Literal(time_end, datatype=XSD.dateTime)))
    g.add((slot_uri, EX.hasActivity, Literal(activity)))
    g.add((slot_uri, EX.isFree, Literal(is_free, datatype=XSD.boolean)))
    save_graph(g)

def book_appointment(doctor_uri, slot_uri, time_start, time_end, activity="Запись к врачу"):
    g = load_graph()
    # Преобразуем строку slot_uri в URIRef
    slot_uri = URIRef(slot_uri)
    g.set((slot_uri, EX.isFree, Literal(False, datatype=XSD.boolean)))
    slot_num = len(list(g.subjects(RDF.type, EX.UserTimeSlot))) + 1
    user_slot_uri = EX[f"UserTimeSlot{slot_num}"]
    g.add((user_slot_uri, RDF.type, EX.UserTimeSlot))
    g.add((user_slot_uri, EX.timeStart, Literal(time_start, datatype=XSD.dateTime)))
    g.add((user_slot_uri, EX.timeEnd, Literal(time_end, datatype=XSD.dateTime)))
    g.add((user_slot_uri, EX.hasActivity, Literal(activity)))
    g.add((user_slot_uri, EX.isFree, Literal(False, datatype=XSD.boolean)))
    g.add((user_slot_uri, EX.relatedDoctorSlot, slot_uri))
    save_graph(g)

def get_user_slots():
    g = load_graph()
    slots = []
    for s in g.subjects(RDF.type, EX.UserTimeSlot):
        activity = g.value(s, EX.hasActivity)
        time_start = g.value(s, EX.timeStart)
        time_end = g.value(s, EX.timeEnd)
        slots.append({
            'activity': str(activity),
            'time_start': str(time_start),
            'time_end': str(time_end)
        })
    return slots