from rdflib import Graph
from data.hospitals import initialize_hospitals
from data.doctors import initialize_doctors
from data.user_slots import initialize_user_slots, get_data_file_path
import os

def initialize_data():
    try:
        print(f"Текущая рабочая директория: {os.getcwd()}")
        g = Graph()
        initialize_hospitals(g)
        initialize_doctors(g)
        initialize_user_slots(g)
        g.serialize(destination=get_data_file_path(), format="turtle")
        print(f"Данные успешно инициализированы в {get_data_file_path()}")
    except Exception as e:
        print(f"Ошибка при инициализации данных: {e}")

if __name__ == "__main__":
    initialize_data()