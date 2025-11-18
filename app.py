import streamlit as st

from db.create_db import create_tables, get_connection
from db.import_from_csv import import_from_csv
from services.quiz_service import (
    get_subjects,
    get_topics_by_subject,
    get_questions_with_options,
)

def init_db():
    create_tables()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM subject;")
    count = c.fetchone()[0]
    conn.close()

    # Si no hay asignaturas, importamos desde el CSV
    if count == 0:
        import_from_csv()


st.set_page_config(page_title="Cuestionarios FP", page_icon="✅")


# =========================
# ESTADO DE LA APLICACIÓN
# =========================

def init_session_state():
    if "step" not in st.session_state:
        st.session_state.step = "select_subject"
    if "selected_subject_id" not in st.session_state:
        st.session_state.selected_subject_id = None
    if "selected_topic_id" not in st.session_state:
        st.session_state.selected_topic_id = None
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}  # question_id -> option_id


# =========================
# PASO 1: ELEGIR ASIGNATURA
# =========================

def select_subject_step():
    st.header("1. Elige la asignatura")

    subjects = get_subjects()
    if not subjects:
        st.warning("No hay asignaturas en la base de datos.")
        st.info("Importa datos con:  python -m db.import_from_csv")
        return

    subject_names = [s[1] for s in subjects]
    subject_ids = [s[0] for s in subjects]

    selected = st.selectbox("Asignatura", subject_names, key="select_subject")

    if st.button("Confirmar asignatura", key="btn_confirm_subject"):
        idx = subject_names.index(selected)
        st.session_state.selected_subject_id = subject_ids[idx]
        st.session_state.selected_topic_id = None
        st.session_state.questions = []
        st.session_state.user_answers = {}
        st.session_state.step = "select_topic"
        st.rerun()


# =========================
# PASO 2: ELEGIR TEMA
# =========================

def select_topic_step():
    st.header("2. Elige el tema")

    subject_id = st.session_state.selected_subject_id
    topics = get_topics_by_subject(subject_id)

    if not topics:
        st.warning("No hay temas para esta asignatura.")
        if st.button("Volver a asignaturas", key="btn_back_subjects_no_topics"):
            st.session_state.step = "select_subject"
            st.session_state.selected_subject_id = None
            st.session_state.selected_topic_id = None
            st.session_state.questions = []
            st.session_state.user_answers = {}
            st.rerun()
        return

    topic_labels = [f"Tema {t[1]} - {t[2]}" for t in topics]
    topic_ids = [t[0] for t in topics]

    selected = st.selectbox("Tema", topic_labels, key="select_topic")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Volver a asignaturas", key="btn_back_subjects"):
            st.session_state.step = "select_subject"
            st.session_state.selected_subject_id = None
            st.session_state.selected_topic_id = None
            st.session_state.questions = []
            st.session_state.user_answers = {}
            st.rerun()

    with col2:
        if st.button("Empezar cuestionario", key="btn_start_quiz"):
            idx = topic_labels.index(selected)
            topic_id = topic_ids[idx]
            st.session_state.selected_topic_id = topic_id

            st.session_state.questions = get_questions_with_options(topic_id)
            st.session_state.user_answers = {}
            st.session_state.step = "do_quiz"
            st.rerun()


# =========================
# PASO 3: HACER EL CUESTIONARIO
# (todas las preguntas a la vez)
# =========================

def do_quiz_step():
    st.header("3. Cuestionario")

    questions = st.session_state.questions

    if not questions:
        st.warning("No hay preguntas para este tema.")
        if st.button("Volver a temas", key="btn_back_topics_no_questions"):
            st.session_state.step = "select_topic"
            st.session_state.selected_topic_id = None
            st.session_state.questions = []
            st.session_state.user_answers = {}
            st.rerun()
        return

    st.info("Responde todas las preguntas y luego pulsa **Corregir cuestionario**.")

    # Mostramos TODAS las preguntas seguidas
    for idx, q in enumerate(questions):
        st.subheader(f"Pregunta {idx + 1} de {len(questions)}")
        st.write(q["text"])

        options = q["options"]
        option_labels = [opt["text"] for opt in options]
        option_ids = [opt["id"] for opt in options]

        # Recuperar respuesta previa si la hubiera
        prev_answer = st.session_state.user_answers.get(q["id"])
        if prev_answer is not None and prev_answer in option_ids:
            default_idx = option_ids.index(prev_answer)
        else:
            default_idx = None  # ninguna seleccionada por defecto

        selected_label = st.radio(
            "Elige una respuesta:",
            option_labels,
            index=default_idx,
            key=f"q_{q['id']}"
        )

        # Solo procesamos si el usuario ha elegido algo
        if selected_label is not None:
            selected_idx = option_labels.index(selected_label)
            selected_option_id = option_ids[selected_idx]
            st.session_state.user_answers[q["id"]] = selected_option_id
        else:
            # Si no hay selección, eliminamos posible respuesta antigua
            st.session_state.user_answers.pop(q["id"], None)

        st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Volver a temas", key="btn_back_topics_from_quiz"):
            st.session_state.step = "select_topic"
            st.session_state.selected_topic_id = None
            st.session_state.questions = []
            st.session_state.user_answers = {}
            st.rerun()

    with col2:
        if st.button("Corregir cuestionario", key="btn_correct_quiz"):
            st.session_state.step = "show_results"
            st.rerun()


# =========================
# PASO 4: MOSTRAR RESULTADOS
# =========================

def show_results_step():
    st.header("4. Resultados")

    questions = st.session_state.questions
    answers = st.session_state.user_answers

    correct_count = 0
    details = []

    for q in questions:
        q_id = q["id"]
        user_option_id = answers.get(q_id)
        correct_option = next(opt for opt in q["options"] if opt["is_correct"])
        is_correct = user_option_id == correct_option["id"]

        if is_correct:
            correct_count += 1

        user_option = next(
            (o for o in q["options"] if o["id"] == user_option_id),
            None
        )

        details.append(
            {
                "question": q["text"],
                "user_option": user_option,
                "correct_option": correct_option,
                "is_correct": is_correct,
            }
        )

    score = correct_count
    total = len(questions)

    st.subheader(f"Has acertado {score} de {total} preguntas.")
    st.write(f"Nota: **{score}/{total}**")

    with st.expander("Ver correcciones en detalle"):
        for item in details:
            st.markdown(f"**Pregunta:** {item['question']}")
            if item["user_option"]:
                if item["is_correct"]:
                    st.markdown(f"- ✅ Tu respuesta: **{item['user_option']['text']}**")
                else:
                    st.markdown(f"- ❌ Tu respuesta: {item['user_option']['text']}")
            else:
                st.markdown("- ❌ Tu respuesta: (sin responder)")

            st.markdown(f"- ✔ Respuesta correcta: **{item['correct_option']['text']}**")
            st.markdown("---")

    st.info("Las respuestas NO se guardan en la base de datos. Solo sirven para esta corrección.")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Repetir este cuestionario", key="btn_repeat_quiz"):
            st.session_state.user_answers = {}
            st.session_state.step = "do_quiz"
            st.rerun()

    with col2:
        if st.button("Elegir otro tema", key="btn_other_topic"):
            st.session_state.step = "select_topic"
            st.session_state.selected_topic_id = None
            st.session_state.questions = []
            st.session_state.user_answers = {}
            st.rerun()

    with col3:
        if st.button("Cambiar de asignatura", key="btn_other_subject"):
            st.session_state.step = "select_subject"
            st.session_state.selected_subject_id = None
            st.session_state.selected_topic_id = None
            st.session_state.questions = []
            st.session_state.user_answers = {}
            st.rerun()


# =========================
# MAIN
# =========================

def main():
    st.title("Cuestionarios FP con Streamlit")

    # 🔹 Inicializar base de datos (crea tablas y, si hace falta, importa el CSV)
    init_db()

    # 🔹 Inicializar estado de sesión la primera vez
    if "step" not in st.session_state:
        st.session_state.step = "select_subject"
        st.session_state.selected_subject_id = None
        st.session_state.selected_topic_id = None
        st.session_state.user_answers = {}
        st.session_state.corrections = None

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
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        init_session_state()
        select_subject_step()


if __name__ == "__main__":
    main()
