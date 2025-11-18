import streamlit as st

from db.create_db import create_tables
from db.import_from_csv import import_from_csv
from services.quiz_service import (
    get_subjects,
    get_topics_by_subject,
    get_questions_with_options,
)

# ---------------------------------------------------------
#  Inicialización de base de datos (solo una vez por proceso)
# ---------------------------------------------------------

DB_INITIALIZED = False


def init_db():
    """
    Crea las tablas si no existen y carga los datos del CSV.
    Solo se ejecuta una vez por proceso en Streamlit.
    """
    global DB_INITIALIZED
    if not DB_INITIALIZED:
        create_tables()
        import_from_csv()
        DB_INITIALIZED = True


# ---------------------------------------------------------
#  Utilidades para el estado de la sesión
# ---------------------------------------------------------


def init_session_state():
    st.session_state.step = "select_subject"
    st.session_state.selected_subject_id = None
    st.session_state.selected_topic_id = None
    st.session_state.user_answers = {}
    st.session_state.corrections = None


# ---------------------------------------------------------
#  Paso 1: elegir asignatura
# ---------------------------------------------------------


def select_subject_step():
    subjects = get_subjects()

    if not subjects:
        st.warning("No hay asignaturas en la base de datos.")
        return

    st.subheader("1️⃣ Elige una asignatura")

    # Mapeamos nombre -> id
    options_labels = [s["name"] for s in subjects]
    label_to_id = {s["name"]: s["id"] for s in subjects}

    selected_label = st.selectbox(
        "Asignatura:",
        options_labels,
        key="subject_select",
    )

    if st.button("Continuar con esta asignatura"):
        st.session_state.selected_subject_id = label_to_id[selected_label]
        st.session_state.selected_topic_id = None
        st.session_state.user_answers = {}
        st.session_state.corrections = None
        st.session_state.step = "select_topic"
        st.experimental_rerun()


# ---------------------------------------------------------
#  Paso 2: elegir tema
# ---------------------------------------------------------


def select_topic_step():
    subject_id = st.session_state.get("selected_subject_id")

    if subject_id is None:
        st.warning("Primero elige una asignatura.")
        st.session_state.step = "select_subject"
        st.experimental_rerun()
        return

    topics = get_topics_by_subject(subject_id)

    if not topics:
        st.warning("No hay temas para esta asignatura.")
        return

    st.subheader("2️⃣ Elige un tema")

    labels = [
        f"Tema {t['number']}: {t['title']}"
        for t in topics
    ]
    label_to_id = {label: t["id"] for label, t in zip(labels, topics)}

    selected_label = st.selectbox(
        "Tema:",
        labels,
        key="topic_select",
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Volver a asignaturas"):
            init_session_state()
            st.experimental_rerun()

    with col2:
        if st.button("Empezar cuestionario ✅"):
            st.session_state.selected_topic_id = label_to_id[selected_label]
            # Limpiar respuestas anteriores
            for k in list(st.session_state.keys()):
                if k.startswith("q_"):
                    del st.session_state[k]
            st.session_state.user_answers = {}
            st.session_state.corrections = None
            st.session_state.step = "do_quiz"
            st.experimental_rerun()


# ---------------------------------------------------------
#  Paso 3: hacer el cuestionario (10 preguntas de golpe)
# ---------------------------------------------------------


def do_quiz_step():
    topic_id = st.session_state.get("selected_topic_id")

    if topic_id is None:
        st.warning("Primero elige un tema.")
        st.session_state.step = "select_topic"
        st.experimental_rerun()
        return

    questions = get_questions_with_options(topic_id)

    if not questions:
        st.warning("No hay preguntas para este tema.")
        return

    st.subheader("3️⃣ Responde al cuestionario")

    # Mostramos todas las preguntas
    letters = ["A", "B", "C", "D"]

    for idx, q in enumerate(questions, start=1):
        st.markdown(f"### Pregunta {idx}")
        st.write(q["question_text"])

        option_labels = []
        for i, opt in enumerate(q["options"]):
            letter = letters[i]
            option_labels.append(f"{letter}. {opt['text']}")

        # Radio sin opción seleccionada por defecto
        st.radio(
            "Selecciona una opción:",
            option_labels,
            key=f"q_{q['question_id']}",
            index=None,
        )
        st.markdown("---")

    # Botones de navegación
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Cambiar de tema"):
            st.session_state.step = "select_topic"
            st.session_state.selected_topic_id = None
            st.session_state.user_answers = {}
            st.session_state.corrections = None
            # Limpiamos respuestas
            for k in list(st.session_state.keys()):
                if k.startswith("q_"):
                    del st.session_state[k]
            st.experimental_rerun()

    with col2:
        if st.button("Corregir ✅"):
            evaluate_quiz(questions)
            st.session_state.step = "show_results"
            st.experimental_rerun()


# ---------------------------------------------------------
#  Corrección del cuestionario
# ---------------------------------------------------------


def evaluate_quiz(questions):
    letters = ["A", "B", "C", "D"]
    results = []
    correct_count = 0

    for q in questions:
        qid = q["question_id"]
        key = f"q_{qid}"
        selected_label = st.session_state.get(key)

        # Obtener índice de la opción correcta
        correct_idx = None
        for i, opt in enumerate(q["options"]):
            if opt.get("is_correct") in (1, True):
                correct_idx = i
                break

        correct_letter = letters[correct_idx] if correct_idx is not None else "?"

        if not selected_label:
            user_letter = None
            is_correct = False
        else:
            user_letter = selected_label.split(".", 1)[0]
            is_correct = user_letter == correct_letter

        if is_correct:
            correct_count += 1

        results.append(
            {
                "question_text": q["question_text"],
                "correct_letter": correct_letter,
                "user_letter": user_letter,
                "is_correct": is_correct,
            }
        )

    st.session_state.corrections = {
        "results": results,
        "score": correct_count,
        "total": len(questions),
    }


# ---------------------------------------------------------
#  Paso 4: mostrar resultados
# ---------------------------------------------------------


def show_results_step():
    corrections = st.session_state.get("corrections")

    if not corrections:
        st.warning("Aún no has corregido el cuestionario.")
        st.session_state.step = "do_quiz"
        st.experimental_rerun()
        return

    score = corrections["score"]
    total = corrections["total"]

    st.subheader("4️⃣ Resultados")

    st.markdown(f"### Has acertado **{score} / {total}** preguntas")

    for idx, r in enumerate(corrections["results"], start=1):
        if r["is_correct"]:
            st.success(f"✔ Pregunta {idx}: correcta")
        else:
            st.error(f"✘ Pregunta {idx}: incorrecta")

        st.write(r["question_text"])
        st.write(f"   - Respuesta correcta: **{r['correct_letter']}**")
        if r["user_letter"] is None:
            st.write("   - Tu respuesta: *(sin contestar)*")
        else:
            st.write(f"   - Tu respuesta: **{r['user_letter']}**")
        st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔁 Repetir este cuestionario"):
            # Solo limpiamos respuestas a preguntas
            for k in list(st.session_state.keys()):
                if k.startswith("q_"):
                    del st.session_state[k]
            st.session_state.corrections = None
            st.session_state.step = "do_quiz"
            st.experimental_rerun()

    with col2:
        if st.button("📚 Elegir otro tema"):
            # Reseteamos estado excepto asignatura
            for k in list(st.session_state.keys()):
                if k.startswith("q_"):
                    del st.session_state[k]
            st.session_state.selected_topic_id = None
            st.session_state.corrections = None
            st.session_state.step = "select_topic"
            st.experimental_rerun()


# ---------------------------------------------------------
#  MAIN
# ---------------------------------------------------------


def main():
    st.title("Cuestionarios FP con Streamlit")

    # Inicializar BD (solo la primera vez por proceso)
    init_db()

    # Inicializar estado de sesión
    if "step" not in st.session_state:
        init_session_state()

    step = st.session_state.step

    if step == "select_subject":
        select_subject_step()
    elif step == "select_topic":
        select_topic_step()
    elif step == "do_quiz":
        do_quiz_step()
    elif step == "show_results":
        show_results_step()
    else:
        st.error("Estado desconocido. Reiniciando.")
        init_session_state()
        select_subject_step()


if __name__ == "__main__":
    main()
