from .create_db import get_connection, create_tables


def seed_example_data():
    """
    Inserta la asignatura 'Riesgos químicos y biológicos ambientales'
    con el Tema 1 y el Tema 2, cada uno con sus 10 preguntas.
    Solo lo hace si la base de datos está vacía (sin asignaturas).
    """

    create_tables()
    conn = get_connection()
    c = conn.cursor()

    # Comprobamos si ya hay asignaturas
    c.execute("SELECT COUNT(*) FROM subject;")
    count_subjects = c.fetchone()[0]

    if count_subjects > 0:
        conn.close()
        return  # Ya hay datos, no hacemos nada

    # 1) Insertamos la asignatura
    c.execute(
        "INSERT INTO subject (name) VALUES (?)",
        ("Riesgos químicos y biológicos ambientales",)
    )
    subject_id = c.lastrowid

    # ==========================================================
    # TEMA 1
    # ==========================================================
    c.execute(
        "INSERT INTO topic (subject_id, number, title) VALUES (?, ?, ?)",
        (subject_id, 1, "Tema 1")
    )
    topic1_id = c.lastrowid

    # === PREGUNTA 1 TEMA 1 ===
    c.execute(
        "INSERT INTO question (topic_id, text) VALUES (?, ?)",
        (topic1_id, "¿Cuál es la vía de entrada más frecuente de los agentes químicos al organismo?")
    )
    q1_id = c.lastrowid
    options_q1 = [
        ("Ingestión accidental", 0),
        ("Inhalación", 1),  # correcta
        ("Contacto dérmico", 0),
        ("Inyección", 0),
    ]
    for text, is_correct in options_q1:
        c.execute(
            "INSERT INTO option (question_id, text, is_correct) VALUES (?, ?, ?)",
            (q1_id, text, is_correct)
        )

    # === PREGUNTA 2 TEMA 1 ===
    c.execute(
        "INSERT INTO question (topic_id, text) VALUES (?, ?)",
        (topic1_id, "¿Cuál de los siguientes agentes es un gas altamente tóxico e inodoro?")
    )
    q2_id = c.lastrowid
    options_q2 = [
        ("Dióxido de nitrógeno", 0),
        ("Amoníaco", 0),
        ("Monóxido de carbono", 1),  # correcta
        ("Cloro", 0),
    ]
    for text, is_correct in options_q2:
        c.execute(
            "INSERT INTO option (question_id, text, is_correct) VALUES (?, ?, ?)",
            (q2_id, text, is_correct)
        )

    # === PREGUNTA 3 TEMA 1 ===
    c.execute(
        "INSERT INTO question (topic_id, text) VALUES (?, ?)",
        (topic1_id, "¿Qué factor NO influye en los efectos que producen los agentes químicos en la salud?")
    )
    q3_id = c.lastrowid
    options_q3 = [
        ("Tiempo de exposición", 0),
        ("Estatura del trabajador", 1),  # correcta
        ("Concentración del agente", 0),
        ("Vía de entrada", 0),
    ]
    for text, is_correct in options_q3:
        c.execute(
            "INSERT INTO option (question_id, text, is_correct) VALUES (?, ?, ?)",
            (q3_id, text, is_correct)
        )

    # === PREGUNTA 4 TEMA 1 ===
    c.execute(
        "INSERT INTO question (topic_id, text) VALUES (?, ?)",
        (topic1_id, "¿Qué tipo de efecto es causado por una exposición prolongada y repetida a agentes químicos?")
    )
    q4_id = c.lastrowid
    options_q4 = [
        ("Efecto agudo", 0),
        ("Efecto irritante", 0),
        ("Efecto crónico", 1),  # correcta
        ("Efecto inmediato", 0),
    ]
    for text, is_correct in options_q4:
        c.execute(
            "INSERT INTO option (question_id, text, is_correct) VALUES (?, ?, ?)",
            (q4_id, text, is_correct)
        )

    # === PREGUNTA 5 TEMA 1 ===
    c.execute(
        "INSERT INTO question (topic_id, text) VALUES (?, ?)",
        (topic1_id, "¿Cuál de estas sustancias puede producir dermatitis de contacto en trabajadores?")
    )
    q5_id = c.lastrowid
    options_q5 = [
        ("Tolueno", 0),
        ("Níquel", 1),  # correcta
        ("Monóxido de carbono", 0),
        ("Helio", 0),
    ]
    for text, is_correct in options_q5:
        c.execute(
            "INSERT INTO option (question_id, text, is_correct) VALUES (?, ?, ?)",
            (q5_id, text, is_correct)
        )

    # === PREGUNTA 6 TEMA 1 ===
    c.execute(
        "INSERT INTO question (topic_id, text) VALUES (?, ?)",
        (topic1_id, "¿Qué contaminante químico se clasifica como un aerosol?")
    )
    q6_id = c.lastrowid
    options_q6 = [
        ("Polvo de sílice cristalina", 1),  # correcta
        ("Gas amoníaco", 0),
        ("Vapor de gasolina", 0),
        ("Ácido sulfúrico", 0),
    ]
    for text, is_correct in options_q6:
        c.execute(
            "INSERT INTO option (question_id, text, is_correct) VALUES (?, ?, ?)",
            (q6_id, text, is_correct)
        )

    # === PREGUNTA 7 TEMA 1 ===
    c.execute(
        "INSERT INTO question (topic_id, text) VALUES (?, ?)",
        (topic1_id, "¿Cuál de las siguientes medidas es fundamental para prevenir riesgos químicos en un laboratorio?")
    )
    q7_id = c.lastrowid
    options_q7 = [
        ("Uso exclusivo de productos naturales", 0),
        ("Uso de campanas extractoras", 1),  # correcta
        ("Evitar el uso de guantes", 0),
        ("Trabajar en espacios cerrados sin ventilación", 0),
    ]
    for text, is_correct in options_q7:
        c.execute(
            "INSERT INTO option (question_id, text, is_correct) VALUES (?, ?, ?)",
            (q7_id, text, is_correct)
        )

    # === PREGUNTA 8 TEMA 1 ===
    c.execute(
        "INSERT INTO question (topic_id, text) VALUES (?, ?)",
        (topic1_id, "¿Qué efecto producen los gases asfixiantes como el monóxido de carbono?")
    )
    q8_id = c.lastrowid
    options_q8 = [
        ("Irritación cutánea", 0),
        ("Inflamación pulmonar", 0),
        ("Desplazan el oxígeno o bloquean su uso en las células", 1),  # correcta
        ("Provocan alergias respiratorias", 0),
    ]
    for text, is_correct in options_q8:
        c.execute(
            "INSERT INTO option (question_id, text, is_correct) VALUES (?, ?, ?)",
            (q8_id, text, is_correct)
        )

    # === PREGUNTA 9 TEMA 1 ===
    c.execute(
        "INSERT INTO question (topic_id, text) VALUES (?, ?)",
        (topic1_id, "¿Qué factor es esencial para minimizar riesgos en la manipulación de productos químicos?")
    )
    q9_id = c.lastrowid
    options_q9 = [
        ("Formación y concienciación del personal", 1),  # correcta
        ("Almacenamiento inadecuado", 0),
        ("Eliminación sin protocolos", 0),
        ("Exposición prolongada sin protección", 0),
    ]
    for text, is_correct in options_q9:
        c.execute(
            "INSERT INTO option (question_id, text, is_correct) VALUES (?, ?, ?)",
            (q9_id, text, is_correct)
        )

    # === PREGUNTA 10 TEMA 1 ===
    c.execute(
        "INSERT INTO question (topic_id, text) VALUES (?, ?)",
        (topic1_id, "¿Cuál de estos contaminantes puede ser cancerígeno tras exposiciones prolongadas?")
    )
    q10_id = c.lastrowid
    options_q10 = [
        ("Isopropanol", 0),
        ("Ácido clorhídrico", 0),
        ("Benceno", 1),  # correcta
        ("Ácido sulfúrico", 0),
    ]
    for text, is_correct in options_q10:
        c.execute(
            "INSERT INTO option (question_id, text, is_correct) VALUES (?, ?, ?)",
            (q10_id, text, is_correct)
        )

    # ==========================================================
    # TEMA 2
    # ==========================================================
    c.execute(
        "INSERT INTO topic (subject_id, number, title) VALUES (?, ?, ?)",
        (subject_id, 2, "Tema 2. Prevención y actuación ante riesgos químicos en el entorno laboral")
    )
    topic2_id = c.lastrowid

    # === PREGUNTA 1 TEMA 2 ===
    c.execute(
        "INSERT INTO question (topic_id, text) VALUES (?, ?)",
        (topic2_id, "¿Cuál es una causa común de incidentes con productos químicos en el trabajo?")
    )
    q2_1_id = c.lastrowid
    options_t2_q1 = [
        ("Almacenamiento con control de temperatura", 0),
        ("Uso sin conocer las instrucciones del producto", 1),  # correcta
        ("Revisión periódica de los equipos", 0),
        ("Señalización visible en el área de trabajo", 0),
    ]
    for text, is_correct in options_t2_q1:
        c.execute(
            "INSERT INTO option (question_id, text, is_correct) VALUES (?, ?, ?)",
            (q2_1_id, text, is_correct)
        )

    # === PREGUNTA 2 TEMA 2 ===
    c.execute(
        "INSERT INTO question (topic_id, text) VALUES (?, ?)",
        (topic2_id, "¿Qué se debe hacer primero en una emergencia química?")
    )
    q2_2_id = c.lastrowid
    options_t2_q2 = [
        ("Investigar el origen del derrame", 0),
        ("Recoger pertenencias personales", 0),
        ("Evacuar la zona afectada", 1),  # correcta
        ("Llamar al proveedor del producto", 0),
    ]
    for text, is_correct in options_t2_q2:
        c.execute(
            "INSERT INTO option (question_id, text, is_correct) VALUES (?, ?, ?)",
            (q2_2_id, text, is_correct)
        )

    # === PREGUNTA 3 TEMA 2 ===
    c.execute(
        "INSERT INTO question (topic_id, text) VALUES (?, ?)",
        (topic2_id, "¿Qué indica una mala gestión de los EPIs?")
    )
    q2_3_id = c.lastrowid
    options_t2_q3 = [
        ("Usar guantes inadecuados para productos corrosivos", 1),  # correcta
        ("Llevar gafas de protección en todo momento", 0),
        ("Utilizar mascarillas con filtros certificados", 0),
        ("Desinfectar los EPIs tras su uso", 0),
    ]
    for text, is_correct in options_t2_q3:
        c.execute(
            "INSERT INTO option (question_id, text, is_correct) VALUES (?, ?, ?)",
            (q2_3_id, text, is_correct)
        )

    # === PREGUNTA 4 TEMA 2 ===
    c.execute(
        "INSERT INTO question (topic_id, text) VALUES (?, ?)",
        (topic2_id, "¿Qué riesgo genera una evaluación de riesgos desactualizada?")
    )
    q2_4_id = c.lastrowid
    options_t2_q4 = [
        ("Cumplimiento excesivo de normas", 0),
        ("Compra innecesaria de productos", 0),
        ("Omisión de peligros reales actuales", 1),  # correcta
        ("Mejora inmediata de la seguridad", 0),
    ]
    for text, is_correct in options_t2_q4:
        c.execute(
            "INSERT INTO option (question_id, text, is_correct) VALUES (?, ?, ?)",
            (q2_4_id, text, is_correct)
        )

    # === PREGUNTA 5 TEMA 2 ===
    c.execute(
        "INSERT INTO question (topic_id, text) VALUES (?, ?)",
        (topic2_id, "¿Qué nivel de emergencia química requiere evacuación general?")
    )
    q2_5_id = c.lastrowid
    options_t2_q5 = [
        ("Conato de emergencia", 0),
        ("Emergencia parcial", 0),
        ("Emergencia total", 1),  # correcta
        ("Emergencia temporal", 0),
    ]
    for text, is_correct in options_t2_q5:
        c.execute(
            "INSERT INTO option (question_id, text, is_correct) VALUES (?, ?, ?)",
            (q2_5_id, text, is_correct)
        )

    # === PREGUNTA 6 TEMA 2 ===
    c.execute(
        "INSERT INTO question (topic_id, text) VALUES (?, ?)",
        (topic2_id, "¿Cuál es un error frecuente en el almacenamiento de productos químicos?")
    )
    q2_6_id = c.lastrowid
    options_t2_q6 = [
        ("Guardarlos en armarios ventilados", 0),
        ("Mezclar sustancias incompatibles entre sí", 1),  # correcta
        ("Etiquetarlos con pictogramas", 0),
        ("Usar estanterías de seguridad", 0),
    ]
    for text, is_correct in options_t2_q6:
        c.execute(
            "INSERT INTO option (question_id, text, is_correct) VALUES (?, ?, ?)",
            (q2_6_id, text, is_correct)
        )

    # === PREGUNTA 7 TEMA 2 ===
    c.execute(
        "INSERT INTO question (topic_id, text) VALUES (?, ?)",
        (topic2_id, "¿Qué herramienta ayuda a conocer los riesgos de un producto químico?")
    )
    q2_7_id = c.lastrowid
    options_t2_q7 = [
        ("Hoja de trabajo semanal", 0),
        ("Manual del operario", 0),
        ("Ficha de Datos de Seguridad (FDS)", 1),  # correcta
        ("Plan de mantenimiento anual", 0),
    ]
    for text, is_correct in options_t2_q7:
        c.execute(
            "INSERT INTO option (question_id, text, is_correct) VALUES (?, ?, ?)",
            (q2_7_id, text, is_correct)
        )

    # === PREGUNTA 8 TEMA 2 ===
    c.execute(
        "INSERT INTO question (topic_id, text) VALUES (?, ?)",
        (topic2_id, "¿Cuál es una medida preventiva ante vapores tóxicos?")
    )
    q2_8_id = c.lastrowid
    options_t2_q8 = [
        ("Aislar el producto sin protección", 0),
        ("Usar ventilación adecuada", 1),  # correcta
        ("Desactivar alarmas por precaución", 0),
        ("Almacenar en zonas poco visibles", 0),
    ]
    for text, is_correct in options_t2_q8:
        c.execute(
            "INSERT INTO option (question_id, text, is_correct) VALUES (?, ?, ?)",
            (q2_8_id, text, is_correct)
        )

    # === PREGUNTA 9 TEMA 2 ===
    c.execute(
        "INSERT INTO question (topic_id, text) VALUES (?, ?)",
        (topic2_id, "¿Cuál es el error en esta práctica?: \"Uso una mascarilla autofiltrante con barba\"")
    )
    q2_9_id = c.lastrowid
    options_t2_q9 = [
        ("Se protege la boca correctamente", 0),
        ("Se evita la inhalación directa", 0),
        ("No hay sellado adecuado de la mascarilla", 1),  # correcta
        ("No hay riesgo si el lugar está ventilado", 0),
    ]
    for text, is_correct in options_t2_q9:
        c.execute(
            "INSERT INTO option (question_id, text, is_correct) VALUES (?, ?, ?)",
            (q2_9_id, text, is_correct)
        )

    # === PREGUNTA 10 TEMA 2 ===
    c.execute(
        "INSERT INTO question (topic_id, text) VALUES (?, ?)",
        (topic2_id, "¿Qué acción NO debe hacerse en caso de contacto químico con los ojos?")
    )
    q2_10_id = c.lastrowid
    options_t2_q10 = [
        ("Enjuagar con abundante agua", 0),
        ("Usar un lavaojos", 0),
        ("Frotarse los ojos", 1),  # correcta
        ("Mantener los párpados abiertos", 0),
    ]
    for text, is_correct in options_t2_q10:
        c.execute(
            "INSERT INTO option (question_id, text, is_correct) VALUES (?, ?, ?)",
            (q2_10_id, text, is_correct)
        )

    conn.commit()
    conn.close()
    print("Insertados Tema 1 y Tema 2 de 'Riesgos químicos y biológicos ambientales'.")


if __name__ == "__main__":
    seed_example_data()
