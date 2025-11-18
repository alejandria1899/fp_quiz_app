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

    Se asume el siguiente formato lógico de columnas en el CSV
    (separadas por ';'):

    subject;topic_number;topic_title;question_number;question_text;
    option_a;option_b;option_c;option_d;correct_option

    donde correct_option es A, B, C o D.
    """

    # 0) Aseguramos tablas
    create_tables()

    conn = get_connection()
    cur = conn.cursor()

    # 1) Borrar datos existentes (en orden de dependencias)
    cur.execute("DELETE FROM option")
    cur.execute("DELETE FROM question")
    cur.execute("DELETE FROM topic")
    cur.execute("DELETE FROM subject")
    conn.commit()

    # 2) Diccionarios para no duplicar inserts
    subject_ids = {}  # nombre_asignatura -> id
    topic_ids = {}    # (nombre_asignatura, num_tema) -> id_tema

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

    # 3) Leer CSV con DictReader y normalizar las cabeceras
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")

        if reader.fieldnames is None:
            raise ValueError("El CSV no tiene cabecera o está vacío.")

        # Normalizamos los nombres de columna
        raw_fieldnames = reader.fieldnames
        clean_fieldnames = [
            name.replace("\ufeff", "").replace('"', "").strip()
            for name in raw_fieldnames
        ]

        # Mapa de nombre original -> nombre limpio
        name_map = {raw: clean for raw, clean in zip(raw_fieldnames, clean_fieldnames)}

        # Comprobamos que al menos existen las columnas que necesitamos
        missing = [col for col in expected_header if col not in clean_fieldnames]
        if missing:
            raise ValueError(
                f"Faltan columnas en el CSV: {missing}. "
                f"Cabeceras detectadas: {clean_fieldnames}"
            )

        for raw_row in reader:
            # Normalizamos el diccionario de la fila
            row = {
                name_map[key]: (value.strip() if value is not None else "")
                for key, value in raw_row.items()
            }

            subject_name = row["subject"]
            topic_number = int(row["topic_number"])
            topic_title = row["topic_title"]
            question_number = int(row["question_number"])
            question_text = row["question_text"]

            option_a = row["option_a"]
            option_b = row["option_b"]
            option_c = row["option_c"]
            option_d = row["option_d"]
            correct_letter = row["correct_option"].upper()

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
                (topic_id, question_number, question_text),
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
