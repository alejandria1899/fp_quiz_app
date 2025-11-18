import csv
from pathlib import Path
from .create_db import get_connection, create_tables

CSV_PATH = Path(__file__).resolve().parent / "quizzes.csv"


def open_csv_any_encoding(path: Path):
    """
    Intenta abrir el CSV probando varios encodings comunes.
    """
    encodings = [
        "utf-8",
        "utf-8-sig",
        "latin-1",
        "windows-1252",
        "macroman"
    ]

    for enc in encodings:
        try:
            f = path.open("r", encoding=enc, errors="replace")
            first = f.readline()
            f.seek(0)
            if first.strip():
                print(f"Usando encoding: {enc}")
                return f
        except Exception:
            pass

    print("No se detectó encoding, usando latin-1 por defecto.")
    return path.open("r", encoding="latin-1", errors="replace")


def clean_header(raw_header: list[str]) -> list[str]:
    """
    Limpia la cabecera del CSV:
    - elimina BOM
    - elimina comillas
    - separa correctamente si viene todo en una sola columna
    """
    header_line = ";".join(raw_header)
    header_line = header_line.replace("\ufeff", "")
    header_line = header_line.strip().strip('"')
    parts = [h.strip().strip('"').lower() for h in header_line.split(";")]
    return parts


def import_from_csv():
    # Aseguramos que las tablas existen
    create_tables()
    conn = get_connection()
    c = conn.cursor()

    # ==========================
    # LIMPIAR TABLAS Y RESETEAR AUTOINCREMENTOS
    # ==========================
    # Orden correcto por claves foráneas
    c.execute("DELETE FROM option;")
    c.execute("DELETE FROM question;")
    c.execute("DELETE FROM topic;")
    c.execute("DELETE FROM subject;")

    # Resetear contadores AUTOINCREMENT de SQLite
    try:
        c.execute(
            "DELETE FROM sqlite_sequence WHERE name IN ('option', 'question', 'topic', 'subject');"
        )
    except Exception:
        # Puede fallar si sqlite_sequence no existe aún, no pasa nada
        pass

    conn.commit()

    # ==========================
    # LEER CSV
    # ==========================
    f = open_csv_any_encoding(CSV_PATH)
    reader = csv.reader(f, delimiter=";")

    # Cabecera
    try:
        raw_header = next(reader)
    except StopIteration:
        print("CSV vacío.")
        conn.close()
        return

    fieldnames = clean_header(raw_header)
    print("Cabeceras detectadas:", fieldnames)

    def row_iter():
        for row in reader:
            line = ";".join(row).strip()
            if not line:
                continue
            parts = [p.strip().strip('"') for p in line.split(";")]
            if len(parts) != len(fieldnames):
                print("Fila ignorada (columnas incorrectas):", parts)
                continue
            yield dict(zip(fieldnames, parts))

    subjects_cache = {}
    topics_cache = {}

    # ==========================
    # INSERTAR FILAS
    # ==========================
    for row in row_iter():
        subject_name = row["subject"].strip()
        topic_number = int(row["topic_number"])
        topic_title = row["topic_title"].strip()
        question_text = row["question_text"].strip()

        option_a = row["option_a"].strip()
        option_b = row["option_b"].strip()
        option_c = row["option_c"].strip()
        option_d = row["option_d"].strip()
        correct_option = row["correct_option"].strip().upper()

        # 1) Asignatura
        if subject_name in subjects_cache:
            subject_id = subjects_cache[subject_name]
        else:
            c.execute("INSERT INTO subject (name) VALUES (?)", (subject_name,))
            subject_id = c.lastrowid
            subjects_cache[subject_name] = subject_id

        # 2) Tema
        t_key = (subject_id, topic_number)
        if t_key in topics_cache:
            topic_id = topics_cache[t_key]
        else:
            c.execute(
                "INSERT INTO topic (subject_id, number, title) VALUES (?, ?, ?)",
                (subject_id, topic_number, topic_title)
            )
            topic_id = c.lastrowid
            topics_cache[t_key] = topic_id

        # 3) Pregunta
        c.execute(
            "INSERT INTO question (topic_id, text) VALUES (?, ?)",
            (topic_id, question_text)
        )
        question_id = c.lastrowid

        # 4) Opciones
        options = [option_a, option_b, option_c, option_d]
        correct_index = {"A": 0, "B": 1, "C": 2, "D": 3}[correct_option]

        for idx, text in enumerate(options):
            c.execute(
                "INSERT INTO option (question_id, text, is_correct) VALUES (?, ?, ?)",
                (question_id, text, 1 if idx == correct_index else 0)
            )

    conn.commit()
    conn.close()
    print("\n✔ Importación completada sin errores.")


if __name__ == "__main__":
    import_from_csv()
