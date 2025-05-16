from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import XSD

EX = Namespace("http://example.org/medical#")


def load_graph(filename="data/data.ttl"):
    """Загрузка графа из файла."""
    g = Graph()
    try:
        g.parse(filename, format="turtle")
    except FileNotFoundError:
        pass
    return g


def save_graph(g, filename="data/data.ttl"):
    """Сохранение графа в файл."""
    g.serialize(destination=filename, format="turtle")


def initialize_user_slots(g):
    """Инициализация пользовательских занятий."""
    user_slots = [
        ("2025-05-13T08:00:00", "2025-05-13T09:00:00", "Учёба", False),
        ("2025-05-13T15:00:00", "2025-05-13T17:00:00", "Работа", False),
        ("2025-05-14T09:00:00", "2025-05-14T10:00:00", "Спорт", False),
        ("2025-05-14T18:00:00", "2025-05-14T19:00:00", "Встреча с друзьями", False),
        ("2025-05-15T11:00:00", "2025-05-15T12:00:00", "Чтение", False),
    ]

    for i, (start_time, end_time, activity, is_free) in enumerate(user_slots, 1):
        user_slot = URIRef(EX + f"UserTimeSlot{i}")
        g.add((user_slot, RDF.type, EX.UserTimeSlot))
        g.add((user_slot, EX.timeStart, Literal(start_time, datatype=XSD.dateTime)))
        g.add((user_slot, EX.timeEnd, Literal(end_time, datatype=XSD.dateTime)))
        g.add((user_slot, EX.hasActivity, Literal(activity)))
        g.add((user_slot, EX.isFree, Literal(is_free)))


def add_user_time_slot(start_time, end_time, activity, is_free=True):
    """Добавление временного слота пользователя."""
    g = load_graph()
    user_slot = URIRef(EX + f"UserTimeSlot{len(g) + 1}")
    g.add((user_slot, RDF.type, EX.UserTimeSlot))
    g.add((user_slot, EX.timeStart, Literal(start_time, datatype=XSD.dateTime)))
    g.add((user_slot, EX.timeEnd, Literal(end_time, datatype=XSD.dateTime)))
    g.add((user_slot, EX.hasActivity, Literal(activity)))
    g.add((user_slot, EX.isFree, Literal(is_free)))
    save_graph(g)


def book_appointment(doctor_uri, slot_uri, start_time, end_time):
    """Запись на прием к врачу."""
    g = load_graph()
    slot = URIRef(slot_uri)
    g.remove((slot, EX.isFree, None))
    g.add((slot, EX.isFree, Literal(False)))

    user_slot = URIRef(EX + f"UserTimeSlot{len(g) + 1}")
    g.add((user_slot, RDF.type, EX.UserTimeSlot))
    g.add((user_slot, EX.timeStart, Literal(start_time, datatype=XSD.dateTime)))
    g.add((user_slot, EX.timeEnd, Literal(end_time, datatype=XSD.dateTime)))
    g.add((user_slot, EX.hasActivity, Literal("Визит к врачу")))
    g.add((user_slot, EX.isFree, Literal(False)))

    save_graph(g)