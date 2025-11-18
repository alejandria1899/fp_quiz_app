# db/import_from_csv.py

import os
import csv

from .create_db import get_connection, create_tables

# Ruta al CSV (está en la misma carpeta que este archivo)
CSV_PATH = os.path.join(os.path.dirname(__file__), "quizzes.csv")


def import_from_csv():
    """
    Borra todos los datos de la base de datos y los vuelve a cargar
    desde quizzes.csv.

    Se asume el siguiente formato de columnas en el CSV (separador ';'):

    subject;topic_number;topic_title;question_number;question_text;
    option_a;option_b;option_c;option_d;correct_option

    donde correct_option es A, B, C o D.
    """

    # Nos aseguramos de que las tablas existen
    create_tables()

    conn = get_connection()
    cur = conn.cursor()

    # 1) Borrar datos en orden de dependencias (options -> questions -> topics -> subjects)
    cur.execute("DELETE FROM option")
    cur.execute("DELETE FROM question")
    cur.execute("DELETE FROM topic")
    cur.execute("DELETE FROM subject")
    conn.commit()

    # 2) Mapas para no repetir inserts de subjects y topics
    subject_ids = {}  # nombre_asignatura -> id
    topic_ids = {}    # (nombre_asignatura, num_tema) -> id_tema

    # 3) Leer el CSV
    expected_header = [
        "subject",
        "topic_number",
        "topic_title",
        "question_number",
        "question_text",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "correct_option",
    ]

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        # Leemos y limpiamos la cabecera (por si tiene BOM)
        first_line = f.readline()
        header = [h.replace("\ufeff", "").strip() for h in first_line.strip().split(";")]

        if header != expected_header:
            raise ValueError(
                f"Cabecera del CSV incorrecta.\n"
                f"Esperado: {expected_header}\n"
                f"Encontrado: {header}"
            )

        reader = csv.DictReader(
            f,
            fieldnames=expected_header,
            delimiter=";",
        )

        for row in reader:
            subject_name = row["subject"].strip()
            topic_number = int(row["topic_number"])
            topic_title = row["topic_title"].strip()
            # question_number lo tenemos por si lo quieres usar en el futuro
            question_text = row["question_text"].strip()

            option_a = row["option_a"].strip()
            option_b = row["option_b"].strip()
            option_c = row["option_c"].strip()
            option_d = row["option_d"].strip()
            correct_letter = row["correct_option"].strip().upper()

            # 3.1) Insertar subject si hace falta
            if subject_name not in subject_ids:
                cur.execute(
                    "INSERT INTO subject (name) VALUES (?)",
                    (subject_name,),
                )
                subject_ids[subject_name] = cur.lastrowid

            subject_id = subject_ids[subject_name]

            # 3.2) Insertar topic si hace falta
            topic_key = (subject_name, topic_number)
            if topic_key not in topic_ids:
                cur.execute(
                    """
                    INSERT INTO topic (subject_id, number, title)
                    VALUES (?, ?, ?)
                    """,
                    (subject_id, topic_number, topic_title),
                )
                topic_ids[topic_key] = cur.lastrowid

            topic_id = topic_ids[topic_key]

            # 3.3) Insertar pregunta
            cur.execute(
                """
                INSERT INTO question (topic_id, number, text)
                VALUES (?, ?, ?)
                """,
                (topic_id, int(row["question_number"]), question_text),
            )
            question_id = cur.lastrowid

            # 3.4) Insertar opciones
            options = [option_a, option_b, option_c, option_d]
            letters_to_index = {"A": 0, "B": 1, "C": 2, "D": 3}

            if correct_letter not in letters_to_index:
                raise ValueError(
                    f"Opción correcta inválida '{correct_letter}' "
                    f"en la pregunta: {question_text}"
                )

            correct_index = letters_to_index[correct_letter]

            for idx, text in enumerate(options):
                is_correct = 1 if idx == correct_index else 0
                cur.execute(
                    """
                    INSERT INTO option (question_id, text, is_correct)
                    VALUES (?, ?, ?)
                    """,
                    (question_id, text, is_correct),
                )

    conn.commit()
    conn.close()
    print("✅ Datos importados desde quizzes.csv")


if __name__ == "__main__":
    # Permite ejecutar: python -m db.import_from_csv
    import_from_csv()
