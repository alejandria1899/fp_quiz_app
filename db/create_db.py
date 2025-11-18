import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "quizzes.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_tables():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS subject (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS topic (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL,
        number INTEGER NOT NULL,
        title TEXT NOT NULL,
        FOREIGN KEY (subject_id) REFERENCES subject(id)
    );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS question (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        FOREIGN KEY (topic_id) REFERENCES topic(id)
    );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS option (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        is_correct INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (question_id) REFERENCES question(id)
    );
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()
    print(f"Tablas creadas en {DB_PATH}")
