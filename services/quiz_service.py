# services/quiz_service.py

"""
Capa de acceso a datos para los cuestionarios.

Aquí NO se hace nada raro: solo usamos sqlite3 a través de
get_connection() para leer subjects, topics, questions y options.
"""

from db.create_db import get_connection


def get_subjects():
    """
    Devuelve lista de asignaturas:
    [
      {"id": 1, "name": "Riesgos químicos y biológicos ambientales"},
      ...
    ]
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM subject ORDER BY name")
    rows = cur.fetchall()
    conn.close()

    # rows deberían ser sqlite3.Row (create_db pone row_factory),
    # así que podemos acceder por nombre de columna.
    return [{"id": r["id"], "name": r["name"]} for r in rows]


def get_topics_by_subject(subject_id: int):
    """
    Devuelve lista de temas de una asignatura:
    [
      {"id": 1, "number": 1, "title": "Tema 1"},
      ...
    ]
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, number, title
        FROM topic
        WHERE subject_id = ?
        ORDER BY number
        """,
        (subject_id,),
    )
    rows = cur.fetchall()
    conn.close()

    return [
        {"id": r["id"], "number": r["number"], "title": r["title"]}
        for r in rows
    ]


def get_questions_with_options_by_topic(topic_id: int):
    """
    Devuelve lista de preguntas con sus opciones, por ejemplo:

    [
      {
        "id": 10,
        "number": 1,
        "text": "¿Cuál es la vía de entrada...?",
        "options": [
          {"id": 101, "text": "Ingestión...", "is_correct": 0},
          {"id": 102, "text": "Inhalación", "is_correct": 1},
          ...
        ]
      },
      ...
    ]
    """
    conn = get_connection()
    cur = conn.cursor()

    # Primero sacamos las preguntas del tema
    cur.execute(
        """
        SELECT id, number, text
        FROM question
        WHERE topic_id = ?
        ORDER BY number
        """,
        (topic_id,),
    )
    q_rows = cur.fetchall()

    questions = []
    for q in q_rows:
        qid = q["id"]

        # Opciones de esta pregunta
        cur.execute(
            """
            SELECT id, text, is_correct
            FROM option
            WHERE question_id = ?
            ORDER BY id
            """,
            (qid,),
        )
        o_rows = cur.fetchall()
        options = [
            {
                "id": o["id"],
                "text": o["text"],
                "is_correct": o["is_correct"],
            }
            for o in o_rows
        ]

        questions.append(
            {
                "id": qid,
                "number": q["number"],
                "text": q["text"],
                "options": options,
            }
        )

    conn.close()
    return questions
