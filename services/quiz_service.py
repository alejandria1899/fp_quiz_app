import sqlite3
from pathlib import Path

# Ruta al archivo de la base de datos (db/quizzes.db)
DB_PATH = Path(__file__).resolve().parent.parent / "db" / "quizzes.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def get_subjects():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, name FROM subject ORDER BY name;")
    rows = c.fetchall()
    conn.close()
    return rows  # [(id, name), ...]


def get_topics_by_subject(subject_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, number, title 
        FROM topic 
        WHERE subject_id = ?
        ORDER BY number;
    """, (subject_id,))
    rows = c.fetchall()
    conn.close()
    return rows  # [(id, number, title), ...]


def get_questions_with_options(topic_id: int):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT q.id, q.text
        FROM question q
        WHERE q.topic_id = ?
        ORDER BY q.id;
    """, (topic_id,))
    questions = c.fetchall()

    result = []
    for q_id, q_text in questions:
        c.execute("""
            SELECT id, text, is_correct
            FROM option
            WHERE question_id = ?
            ORDER BY id;
        """, (q_id,))
        options = c.fetchall()
        result.append(
            {
                "id": q_id,
                "text": q_text,
                "options": [
                    {
                        "id": opt_id,
                        "text": opt_text,
                        "is_correct": bool(is_corr),
                    }
                    for (opt_id, opt_text, is_corr) in options
                ],
            }
        )

    conn.close()
    return result
