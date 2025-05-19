from rdflib import Graph, Literal, RDF, URIRef, Namespace

EX = Namespace("http://example.org/medical#")

def initialize_hospitals(g):
    """Инициализация данных о поликлиниках."""
    hospitals = [
        ("Hospital1", "ул. Ленина, 10"),
        ("Hospital2", "ул. Мира, 5"),
        ("Hospital3", "ул. Победы, 25"),
        ("Hospital4", "ул. Советская, 15"),
        ("Hospital5", "ул. Зеленая, 8"),
        ("Hospital6", "ул. Гагарина, 12"),
        ("Hospital7", "ул. Молодёжная, 3"),
        ("Hospital8", "ул. Солнечная, 20"),
        ("Hospital9", "ул. Центральная, 7"),
        ("Hospital10", "ул. Парковая, 14"),
    ]

    for hospital_id, address in hospitals:
        hospital = URIRef(EX + hospital_id)
        g.add((hospital, RDF.type, EX.Hospital))
        g.add((hospital, EX.address, Literal(address)))