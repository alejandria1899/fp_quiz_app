import sqlite3
import random
from db.create_db import get_connection


# ---------- ASIGNATURAS ---------- #

def get_subjects():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, name
        FROM subject
        ORDER BY name
        """
    )
    rows = cur.fetchall()
    conn.close()

    return [{"id": r["id"], "name": r["name"]} for r in rows]


def get_subject_name(subject_id: int):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        "SELECT name FROM subject WHERE id = ?",
        (subject_id,),
    )
    row = cur.fetchone()
    conn.close()

    return row["name"] if row else None


# ---------- TEMAS ---------- #

def get_topics_by_subject(subject_id: int):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
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
        {
            "id": r["id"],
            "number": r["number"],
            "name": r["title"],
        }
        for r in rows
    ]


def get_topic_name(topic_id: int):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        "SELECT title FROM topic WHERE id = ?",
        (topic_id,),
    )
    row = cur.fetchone()
    conn.close()

    return row["title"] if row else None


# ---------- PREGUNTAS Y OPCIONES ---------- #

def get_questions_by_topic(topic_id: int):
    """
    Devuelve una lista de preguntas de un tema con sus opciones barajadas.
    """

    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Preguntas del tema
    cur.execute(
        """
        SELECT id, text, number
        FROM question
        WHERE topic_id = ?
        ORDER BY number
        """,
        (topic_id,),
    )
    question_rows = cur.fetchall()

    questions = []

    for q_row in question_rows:
        q_id = q_row["id"]

        # =====================================================
        # 🔥 CAMBIO: ahora NO ordenamos por ID en la consulta
        # =====================================================
        cur.execute(
            """
            SELECT id, text, is_correct
            FROM option
            WHERE question_id = ?
            """,
            (q_id,),
        )
        option_rows = cur.fetchall()

        # =====================================================
        # 🔥 CAMBIO: barajar aleatoriamente las opciones
        # =====================================================
        option_rows = list(option_rows)   # convertir Row a lista normal
        random.shuffle(option_rows)

        # Volver a asignar etiquetas A, B, C, D según el nuevo orden
        options = []
        for idx, o in enumerate(option_rows):
            label = chr(ord("A") + idx)
            options.append(
                {
                    "id": o["id"],
                    "text": o["text"],
                    "label": label,
                    "is_correct": bool(o["is_correct"]),
                }
            )

        questions.append(
            {
                "id": q_row["id"],
                "text": q_row["text"],
                "number": q_row["number"],
                "options": options,
            }
        )

    conn.close()
    return questions


# ---------- RESULTADOS / HISTORIAL ---------- #

def _ensure_quiz_result_table(cur):
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS quiz_result (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER,
            topic_id INTEGER,
            score INTEGER,
            total_questions INTEGER,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        )
        """
    )


def save_quiz_result(subject_id: int, topic_id: int, score: int, total_questions: int):
    conn = get_connection()
    cur = conn.cursor()

    _ensure_quiz_result_table(cur)

    cur.execute(
        """
        INSERT INTO quiz_result (subject_id, topic_id, score, total_questions)
        VALUES (?, ?, ?, ?)
        """,
        (subject_id, topic_id, score, total_questions),
    )

    conn.commit()
    conn.close()


def get_quiz_history(subject_id: int):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    _ensure_quiz_result_table(cur)

    cur.execute(
        """
        SELECT
            qr.score,
            qr.total_questions,
            qr.created_at,
            t.title AS topic_name
        FROM quiz_result qr
        LEFT JOIN topic t ON qr.topic_id = t.id
        WHERE qr.subject_id = ?
        ORDER BY datetime(qr.created_at) DESC
        LIMIT 50
        """,
        (subject_id,),
    )

    rows = cur.fetchall()
    conn.close()

    return [dict(r) for r in rows]
