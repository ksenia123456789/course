from rdflib import Graph
from data.doctors import initialize_doctors
from data.hospitals import initialize_hospitals
from data.user_slots import initialize_user_slots

def initialize_data():
    """Инициализация всех данных."""
    g = Graph()
    initialize_hospitals(g)
    initialize_doctors(g)
    initialize_user_slots(g)
    g.serialize(destination="data.ttl", format="turtle")

if __name__ == "__main__":
    initialize_data()