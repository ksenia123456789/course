from data.doctors import get_doctors_by_specialty
from data.user_slots import load_graph
from datetime import datetime


def find_matching_slots(specialty):
    """Поиск подходящих временных слотов для записи к врачу."""
    g = load_graph()
    doctor_slots = get_doctors_by_specialty(specialty, g)
    matches = []

    for slot in doctor_slots:
        try:
            start = datetime.fromisoformat(slot['time_start'])
            end = datetime.fromisoformat(slot['time_end'])
            matches.append(slot)
        except ValueError:
            continue

    return matches