import os
import sqlite3

# Ruta al archivo de base de datos SQLite
DB_PATH = os.path.join(os.path.dirname(__file__), "quizzes.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 👈 ESTO ES LO IMPORTANTE
    return conn


def create_tables():
    """
    Crea las tablas necesarias si no existen.
    Estructura:
      - subject(id, name)
      - topic(id, subject_id, number, title)
      - question(id, topic_id, number, text)
      - option(id, question_id, text, is_correct)
    """
    conn = get_connection()
    cur = conn.cursor()

    # Tabla de asignaturas
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS subject (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        """
    )

    # Tabla de temas
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS topic (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            number     INTEGER NOT NULL,
            title      TEXT NOT NULL,
            FOREIGN KEY(subject_id) REFERENCES subject(id)
        )
        """
    )

    # Tabla de preguntas
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS question (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER NOT NULL,
            number   INTEGER NOT NULL,
            text     TEXT NOT NULL,
            FOREIGN KEY(topic_id) REFERENCES topic(id)
        )
        """
    )

    # Tabla de opciones
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS option (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            text        TEXT NOT NULL,
            is_correct  INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(question_id) REFERENCES question(id)
        )
        """
    )

    conn.commit()
    conn.close()
