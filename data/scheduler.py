from data.doctors import get_doctors_by_specialty
from data.user_slots import load_graph, get_user_slots
from datetime import datetime


def find_matching_slots(specialty):
    """Поиск подходящих временных слотов для записи к врачу."""
    g = load_graph()
    doctor_slots = get_doctors_by_specialty(specialty, g)
    user_slots = get_user_slots()
    matches = []

    for slot in doctor_slots:
        try:
            slot_start = datetime.fromisoformat(slot['time_start'])
            slot_end = datetime.fromisoformat(slot['time_end'])

            # Проверка пересечений с пользовательскими слотами
            overlap = False
            for user_slot in user_slots:
                user_start = datetime.fromisoformat(user_slot['time_start'])
                user_end = datetime.fromisoformat(user_slot['time_end'])
                if not (slot_end <= user_start or slot_start >= user_end):
                    overlap = True
                    break
            if not overlap:
                matches.append(slot)
        except ValueError:
            continue

    print("Filtered matches:", matches)  # Отладка
    return matches