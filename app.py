import streamlit as st

from db.create_db import create_tables
from services.quiz_service import (
    get_subjects,
    get_topics_by_subject,
    get_questions_with_options_by_topic,
)


# ------------------------------
# Inicialización de base de datos
# ------------------------------

def init_db():
    """
    En producción (Streamlit Cloud) NO importamos desde el CSV.
    Solo nos aseguramos de que las tablas existan en quizzes.db.

    Los datos de preguntas ya están dentro de quizzes.db,
    que lo has generado en local ejecutando:
        python -m db.import_from_csv
    """
    create_tables()


# ------------------------------
# Estado de sesión
# ------------------------------

def init_session_state():
    st.session_state.step = "select_subject"
    st.session_state.selected_subject_id = None
    st.session_state.selected_topic_id = None
    st.session_state.user_answers = {}
    st.session_state.corrections = None


# ------------------------------
# Paso 1: elegir asignatura
# ------------------------------

def select_subject_step():
    st.header("1️⃣ Elige una asignatura")

    subjects = get_subjects()

    if not subjects:
        st.error("No hay asignaturas en la base de datos.")
        st.info("Asegúrate de haber importado datos desde el CSV en local.")
        return

    subject_names = [s["name"] for s in subjects]
    subject_ids = [s["id"] for s in subjects]

    # Valor por defecto: el que esté ya en session_state si existe
    if st.session_state.get("selected_subject_id") in subject_ids:
        default_index = subject_ids.index(st.session_state["selected_subject_id"])
    else:
        default_index = 0

    selected_name = st.selectbox(
        "Asignatura:",
        subject_names,
        index=default_index,
    )

    selected_subject_id = subject_ids[subject_names.index(selected_name)]

    if st.button("➡️ Elegir tema"):
        st.session_state.selected_subject_id = selected_subject_id
        st.session_state.selected_topic_id = None
        st.session_state.user_answers = {}
        st.session_state.corrections = None
        st.session_state.step = "select_topic"
        st.experimental_rerun()


# ------------------------------
# Paso 2: elegir tema
# ------------------------------

def select_topic_step():
    st.header("2️⃣ Elige un tema")

    subject_id = st.session_state.get("selected_subject_id")
    if subject_id is None:
        st.warning("Primero elige una asignatura.")
        st.session_state.step = "select_subject"
        st.experimental_rerun()
        return

    topics = get_topics_by_subject(subject_id)

    if not topics:
        st.error("Esta asignatura aún no tiene temas.")
        if st.button("⬅️ Volver a asignaturas"):
            st.session_state.step = "select_subject"
            st.experimental_rerun()
        return

    topic_labels = [f"Tema {t['number']}: {t['title']}" for t in topics]
    topic_ids = [t["id"] for t in topics]

    if st.session_state.get("selected_topic_id") in topic_ids:
        default_index = topic_ids.index(st.session_state["selected_topic_id"])
    else:
        default_index = 0

    selected_label = st.selectbox(
        "Tema:",
        topic_labels,
        index=default_index,
    )

    selected_topic_id = topic_ids[topic_labels.index(selected_label)]

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Cambiar asignatura"):
            st.session_state.step = "select_subject"
            st.session_state.selected_subject_id = None
            st.session_state.selected_topic_id = None
            st.session_state.user_answers = {}
            st.session_state.corrections = None
            st.experimental_rerun()

    with col2:
        if st.button("➡️ Empezar cuestionario"):
            st.session_state.selected_topic_id = selected_topic_id
            st.session_state.user_answers = {}
            st.session_state.corrections = None
            st.session_state.step = "do_quiz"
            st.experimental_rerun()


# ------------------------------
# Paso 3: realizar cuestionario
# ------------------------------

def do_quiz_step():
    st.header("3️⃣ Cuestionario")

    topic_id = st.session_state.get("selected_topic_id")
    if topic_id is None:
        st.warning("Primero elige un tema.")
        st.session_state.step = "select_topic"
        st.experimental_rerun()
        return

    questions = get_questions_with_options_by_topic(topic_id)

    if not questions:
        st.error("Este tema no tiene preguntas aún.")
        if st.button("⬅️ Volver a temas"):
            st.session_state.step = "select_topic"
            st.experimental_rerun()
        return

    st.write(
        "Responde a todas las preguntas y, cuando termines, pulsa **Corregir**."
    )

    user_answers = st.session_state.get("user_answers", {})

    # Mostramos las 10 preguntas seguidas
    for q in questions:
        qid = q["id"]
        st.markdown(f"**Pregunta {q['number']}**")
        st.write(q["text"])

        options = q["options"]  # lista de dicts con id, text, is_correct
        option_labels = [opt["text"] for opt in options]
        option_ids = [opt["id"] for opt in options]

        # Usamos claves únicas por pregunta en session_state
        state_key = f"q_{qid}_answer"

        # Recuperar respuesta previa si existe
        prev_answer_id = user_answers.get(qid)
        if prev_answer_id in option_ids:
            prev_index = option_ids.index(prev_answer_id)
        else:
            prev_index = None  # Nada seleccionado

        # Radio sin opción marcada por defecto
        selected_label = st.radio(
            "Elige una respuesta:",
            option_labels,
            index=prev_index if prev_index is not None else 0,
            key=state_key,
        )

        # Importante: si queremos "sin marcar" de verdad,
        # ponemos el valor solo cuando el usuario interactúe.
        # Pero Streamlit obliga a tener un valor; así que
        # lo que hacemos es guardar lo que haya en session_state
        # al final del render.

        selected_idx = option_labels.index(selected_label)
        selected_option_id = option_ids[selected_idx]
        user_answers[qid] = selected_option_id

        st.markdown("---")

    # Actualizamos en session_state
    st.session_state.user_answers = user_answers

    if st.button("✅ Corregir"):
        corrections = []
        score = 0

        for q in questions:
            qid = q["id"]
            options = q["options"]
            option_ids = [opt["id"] for opt in options]

            correct_option = next(
                opt for opt in options if opt["is_correct"] == 1
            )

            user_option_id = user_answers.get(qid)
            is_correct = user_option_id == correct_option["id"]

            if is_correct:
                score += 1

            user_letter = None
            if user_option_id in option_ids:
                idx = option_ids.index(user_option_id)
                user_letter = ["A", "B", "C", "D"][idx]

            correct_idx = option_ids.index(correct_option["id"])
            correct_letter = ["A", "B", "C", "D"][correct_idx]

            corrections.append(
                {
                    "question_number": q["number"],
                    "question_text": q["text"],
                    "is_correct": is_correct,
                    "correct_text": correct_option["text"],
                    "correct_letter": correct_letter,
                    "user_letter": user_letter,
                }
            )

        st.session_state.corrections = {
            "score": score,
            "total": len(questions),
            "results": corrections,
        }
        st.session_state.step = "show_results"
        st.experimental_rerun()


# ------------------------------
# Paso 4: mostrar resultados
# ------------------------------

def show_results_step():
    st.header("4️⃣ Resultados")

    corrections = st.session_state.get("corrections")
    if not corrections:
        st.warning("Todavía no has corregido un cuestionario.")
        st.session_state.step = "select_subject"
        st.experimental_rerun()
        return

    score = corrections["score"]
    total = corrections["total"]

    st.markdown(f"### Has acertado **{score} / {total}**")

    for idx, r in enumerate(corrections["results"], start=1):
        if r["is_correct"]:
            st.success(f"✅ Pregunta {idx}: correcta")
        else:
            st.error(f"❌ Pregunta {idx}: incorrecta")

        st.write(r["question_text"])
        st.write(f"   - Respuesta correcta: **{r['correct_letter']}) {r['correct_text']}**")
        if r["user_letter"] is None:
            st.write("   - Tu respuesta: *(sin contestar)*")
        else:
            st.write(f"   - Tu respuesta: **{r['user_letter']})**")
        st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔁 Repetir este cuestionario"):
            # Limpia solo respuestas y correcciones, mantiene asignatura/tema
            st.session_state.user_answers = {}
            st.session_state.corrections = None
            st.session_state.step = "do_quiz"
            st.experimental_rerun()

    with col2:
        if st.button("📚 Elegir otro tema"):
            st.session_state.selected_topic_id = None
            st.session_state.user_answers = {}
            st.session_state.corrections = None
            st.session_state.step = "select_topic"
            st.experimental_rerun()

    with col3:
        if st.button("🏫 Elegir otra asignatura"):
            init_session_state()
            st.experimental_rerun()


# ------------------------------
# main
# ------------------------------

def main():
    st.title("Cuestionarios FP con Streamlit")

    # 🔹 Inicializar DB (solo asegura tablas, NO importa CSV aquí)
    init_db()

    # 🔹 Inicializar estado de sesión
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
