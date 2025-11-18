import os

from .create_db import get_connection, create_tables

CSV_PATH = os.path.join(os.path.dirname(__file__), "quizzes.csv")


def import_from_csv():
    print(f"📂 Importando datos desde: {CSV_PATH}")

    # Crear tablas si no existen
    create_tables()
    conn = get_connection()
    cur = conn.cursor()

    # Borrar datos existentes
    cur.execute("DELETE FROM option")
    cur.execute("DELETE FROM question")
    cur.execute("DELETE FROM topic")
    cur.execute("DELETE FROM subject")
    conn.commit()

    subject_ids = {}
    topic_ids = {}

    total_subjects = 0
    total_topics = 0
    total_questions = 0
    total_options = 0

    # Leer todas las líneas del CSV
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        print("⚠️ El CSV está vacío.")
        conn.close()
        return

    # Saltamos la cabecera (línea 1)
    for line_number, raw_line in enumerate(lines[1:], start=2):
        raw_line = raw_line.strip()
        if not raw_line:
            # Línea vacía
            print(f"↩️ Saltando línea {line_number}: línea vacía")
            continue

        # Separar por ';'
        row = raw_line.split(";")

        if len(row) < 10:
            print(f"↩️ Saltando línea {line_number}: fila incompleta -> {row}")
            continue

        # Limpiar espacios y comillas dobles alrededor de cada campo
        row = [col.strip().strip('"') for col in row]

        (
            subject_name,
            topic_number_str,
            topic_title,
            question_number_str,
            question_text,
            option_a,
            option_b,
            option_c,
            option_d,
            correct_letter,
            *rest,
        ) = row

        # Parsear números de tema y pregunta
        try:
            topic_number = int(topic_number_str)
            question_number = int(question_number_str)
        except ValueError:
            print(
                f"↩️ Saltando línea {line_number}: número de tema/pregunta inválido -> "
                f"topic_number='{topic_number_str}', question_number='{question_number_str}'"
            )
            continue

        # Normalizar letra correcta
        correct_letter_clean = correct_letter.strip().upper()

        if correct_letter_clean not in {"A", "B", "C", "D"}:
            print(
                f"⚠️ Línea {line_number}: opción correcta '{correct_letter}' inválida "
                f"(normalizada: '{correct_letter_clean}'). "
                "Se insertan opciones sin marcar correcta. "
                f"Fila: {row}"
            )
            is_correct_a = is_correct_b = is_correct_c = is_correct_d = 0
        else:
            is_correct_a = 1 if correct_letter_clean == "A" else 0
            is_correct_b = 1 if correct_letter_clean == "B" else 0
            is_correct_c = 1 if correct_letter_clean == "C" else 0
            is_correct_d = 1 if correct_letter_clean == "D" else 0

        # Insertar subject si no existe
        if subject_name not in subject_ids:
            cur.execute(
                "INSERT INTO subject (name) VALUES (?)",
                (subject_name,),
            )
            subject_id = cur.lastrowid
            subject_ids[subject_name] = subject_id
            total_subjects += 1
        else:
            subject_id = subject_ids[subject_name]

        # Clave del tema
        topic_key = (subject_name, topic_number)

        # Insertar topic si no existe
        if topic_key not in topic_ids:
            cur.execute(
                """
                INSERT INTO topic (subject_id, number, title)
                VALUES (?, ?, ?)
                """,
                (subject_id, topic_number, topic_title),
            )
            topic_id = cur.lastrowid
            topic_ids[topic_key] = topic_id
            total_topics += 1
        else:
            topic_id = topic_ids[topic_key]

        # Insertar question
        cur.execute(
            """
            INSERT INTO question (topic_id, number, text)
            VALUES (?, ?, ?)
            """,
            (topic_id, question_number, question_text),
        )
        question_id = cur.lastrowid
        total_questions += 1

        # Insertar opciones
        cur.executemany(
            """
            INSERT INTO option (question_id, text, is_correct)
            VALUES (?, ?, ?)
            """,
            [
                (question_id, option_a, is_correct_a),
                (question_id, option_b, is_correct_b),
                (question_id, option_c, is_correct_c),
                (question_id, option_d, is_correct_d),
            ],
        )
        total_options += 4

    conn.commit()
    conn.close()

    print("✅ Importación terminada.")
    print(f"   Asignaturas insertadas: {total_subjects}")
    print(f"   Temas insertados:       {total_topics}")
    print(f"   Preguntas insertadas:   {total_questions}")
    print(f"   Opciones insertadas:    {total_options}")


if __name__ == "__main__":
    import_from_csv()
