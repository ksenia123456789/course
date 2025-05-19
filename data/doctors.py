from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import XSD

EX = Namespace("http://example.org/medical#")

def initialize_doctors(g):
    """Инициализация данных о врачах."""
    doctors = [
        ("Doctor1", "Иванов Иван Иванович", "Кардиолог", EX.Hospital1),
        ("Doctor2", "Петров Алексей Сергеевич", "Терапевт", EX.Hospital1),
        ("Doctor3", "Сидорова Мария Петровна", "Невролог", EX.Hospital2),
        ("Doctor4", "Козлов Дмитрий Викторович", "Хирург", EX.Hospital2),
        ("Doctor5", "Смирнова Елена Викторовна", "Кардиолог", EX.Hospital2),
        ("Doctor6", "Николаева Анна Павловна", "Терапевт", EX.Hospital3),
        ("Doctor7", "Морозов Сергей Иванович", "Ортопед", EX.Hospital3),
        ("Doctor8", "Васильева Ольга Николаевна", "Невролог", EX.Hospital4),
        ("Doctor9", "Федоров Михаил Юрьевич", "Хирург", EX.Hospital4),
        ("Doctor10", "Кузнецова Екатерина Андреевна", "Ортопед", EX.Hospital5),
        ("Doctor11", "Лебедева Наталья Ивановна", "Педиатр", EX.Hospital6),
        ("Doctor12", "Григорьев Павел Александрович", "Офтальмолог", EX.Hospital6),
        ("Doctor13", "Зайцева Юлия Сергеевна", "Дерматолог", EX.Hospital7),
        ("Doctor14", "Соколов Артём Михайлович", "Кардиолог", EX.Hospital7),
        ("Doctor15", "Егорова Светлана Викторовна", "Терапевт", EX.Hospital8),
        ("Doctor16", "Белов Игорь Николаевич", "Невролог", EX.Hospital8),
        ("Doctor17", "Крылова Алина Дмитриевна", "Хирург", EX.Hospital9),
        ("Doctor18", "Михайлов Олег Петрович", "Ортопед", EX.Hospital9),
        ("Doctor19", "Титова Екатерина Павловна", "Педиатр", EX.Hospital10),
        ("Doctor20", "Романов Денис Андреевич", "Офтальмолог", EX.Hospital10),
    ]

    slot_counter = 1
    for doc_id, name, specialty, hospital in doctors:
        doctor = URIRef(EX + doc_id)
        g.add((doctor, RDF.type, EX.Doctor))
        g.add((doctor, EX.name, Literal(name)))
        g.add((doctor, EX.specialty, Literal(specialty)))
        g.add((doctor, EX.worksIn, hospital))

        # Добавление 2–3 слотов на врача
        slots = [
            ("2025-05-13T10:00:00", "2025-05-13T11:00:00"),
            ("2025-05-14T14:00:00", "2025-05-14T15:00:00"),
        ]
        if specialty in ["Кардиолог", "Ортопед", "Педиатр", "Офтальмолог"]:  # Дополнительный слот для некоторых специальностей
            slots.append(("2025-05-15T09:00:00", "2025-05-15T10:00:00"))
        # Новые даты для новых врачей (Doctor11–Doctor20)
        if int(doc_id.replace("Doctor", "")) > 10:
            slots.extend([
                ("2025-05-16T11:00:00", "2025-05-16T12:00:00"),
                ("2025-05-17T13:00:00", "2025-05-17T14:00:00"),
            ])
            if specialty in ["Педиатр", "Офтальмолог"]:
                slots.append(("2025-05-18T08:00:00", "2025-05-18T09:00:00"))

        for start, end in slots:
            slot = URIRef(EX + f"DoctorTimeSlot{slot_counter}")
            g.add((slot, RDF.type, EX.DoctorTimeSlot))
            g.add((slot, EX.hasDoctor, doctor))
            g.add((slot, EX.timeStart, Literal(start, datatype=XSD.dateTime)))
            g.add((slot, EX.timeEnd, Literal(end, datatype=XSD.dateTime)))
            g.add((slot, EX.isFree, Literal(True)))
            slot_counter += 1

def get_doctors_by_specialty(specialty, g):
    """Получение врачей по специальности."""
    query = """
        PREFIX ex: <http://example.org/medical#>
        SELECT ?doctor ?name ?specialty ?hospital ?address ?slot ?timeStart ?timeEnd
        WHERE {
            ?doctor a ex:Doctor .
            ?doctor ex:name ?name .
            ?doctor ex:specialty ?specialty .
            ?doctor ex:worksIn ?hospital .
            ?hospital ex:address ?address .
            ?slot ex:hasDoctor ?doctor .
            ?slot ex:timeStart ?timeStart .
            ?slot ex:timeEnd ?timeEnd .
            ?slot ex:isFree ?isFree .
            FILTER (?specialty = %s && ?isFree = true)
        }
    """
    q = query % f'"{specialty}"'
    results = g.query(q)
    print("SPARQL results:", list(results))  # Отладочный вывод
    return [
        {
            "doctor_uri": str(row.doctor),
            "doctor": str(row.name),
            "hospital": str(row.address),
            "slot_uri": str(row.slot),
            "time_start": str(row.timeStart),
            "time_end": str(row.timeEnd),
            "specialty": str(row.specialty)  # Добавляем specialty в результат
        }
        for row in results
    ]