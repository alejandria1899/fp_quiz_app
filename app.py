import random
import streamlit as st

from services.quiz_service import (
    get_subjects,
    get_topics_by_subject,
    get_questions_by_topic,
    get_subject_name,
    get_topic_name,
)

# ---------------------- ACCESO POR CORREOS PERMITIDOS ---------------------- #


def load_allowed_emails():
    """
    Carga los correos permitidos desde st.secrets["allowed_emails"].

    En Streamlit Cloud debes configurar en los secrets algo como:
    allowed_emails = "correo1@alu.medac.es,correo2@alu.medac.es"

    En local, si no hay nada configurado en secrets, se usará
    un correo de prueba por defecto (cámbialo por el tuyo).
    """
    try:
        raw = st.secrets.get("allowed_emails", "")
    except Exception:
        # Si no hay secrets (por ejemplo, primera vez en local),
        # usa tu correo para pruebas locales.
        return {"tuemail@alu.medac.es"}

    if not raw:
        return {"tuemail@alu.medac.es"}

    return {email.strip().lower() for email in raw.split(",") if email.strip()}


ALLOWED_EMAILS = load_allowed_emails()

# ---------------------- ESTADO INICIAL ---------------------- #


def init_state():
    if "step" not in st.session_state:
        st.session_state.step = "select_subject"

    if "selected_subject_id" not in st.session_state:
        st.session_state.selected_subject_id = None

    if "selected_topic_id" not in st.session_state:
        st.session_state.selected_topic_id = None

    if "questions" not in st.session_state:
        st.session_state.questions = []

    if "user_answers" not in st.session_state:
        # dict: question_id -> option_id
        st.session_state.user_answers = {}

    if "score" not in st.session_state:
        st.session_state.score = 0

    if "total_questions" not in st.session_state:
        st.session_state.total_questions = 0

    if "review" not in st.session_state:
        # lista de dicts con info por pregunta para el resumen final
        st.session_state.review = []

    # 🔐 Estado de autenticación
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "user_email" not in st.session_state:
        st.session_state.user_email = ""


# ---------------------- LOGIN ---------------------- #


def login_screen():
    st.title("🔐 Acceso restringido a FP Quiz")

    email = st.text_input("Introduce tu correo autorizado")

    if st.button("Entrar"):
        email_clean = email.strip().lower()

        if email_clean in ALLOWED_EMAILS:
            st.session_state.logged_in = True
            st.session_state.user_email = email_clean
            st.success("Acceso permitido. ¡Bienvenido!")
            st.rerun()
        else:
            st.error("❌ Este correo no está autorizado para usar la aplicación.")


# ---------------------- HELPERS DE TEMAS / QUIZ ---------------------- #


def start_quiz_for_topic(topic_id: int):
    """
    Carga las preguntas de un tema, baraja las opciones y prepara el estado
    de sesión para empezar el cuestionario.
    """
    questions = get_questions_by_topic(topic_id)

    # Barajar opciones de cada pregunta
    for q in questions:
        random.shuffle(q["options"])

    st.session_state.selected_topic_id = topic_id
    st.session_state.questions = questions
    st.session_state.user_answers = {}
    st.session_state.score = 0
    st.session_state.total_questions = len(questions)
    st.session_state.review = []
    st.session_state.step = "quiz"


def build_topic_label(subject_id: int, topic_id: int) -> str:
    """
    Devuelve un texto tipo: 'Tema 3: Título del tema'
    usando la info de la DB.
    """
    topic_name = get_topic_name(topic_id) or "Tema"
    label = topic_name

    if subject_id is not None and topic_id is not None:
        topics = get_topics_by_subject(subject_id)
        for t in topics:
            if t["id"] == topic_id:
                label = f"Tema {t['number']}: {topic_name}"
                break

    return label


# ---------------------- PANTALLA 1: SELECCIONAR ASIGNATURA ---------------------- #


def select_subject_step():
    st.header("📚 Selecciona la asignatura")

    subjects = get_subjects()

    if not subjects:
        st.warning("No hay asignaturas disponibles en la base de datos.")
        return

    subject_names = [s["name"] for s in subjects]
    id_by_name = {s["name"]: s["id"] for s in subjects}

    # Preselección si ya tenía algo guardado
    if st.session_state.selected_subject_id is not None:
        try:
            default_index = subject_names.index(
                next(
                    s["name"]
                    for s in subjects
                    if s["id"] == st.session_state.selected_subject_id
                )
            )
        except StopIteration:
            default_index = 0
    else:
        default_index = 0

    selected_subject_name = st.selectbox(
        "Elige una asignatura:",
        subject_names,
        index=default_index,
    )

    selected_subject_id = id_by_name[selected_subject_name]

    if st.button("Continuar ➡️"):
        # Guardamos asignatura y reseteamos todo lo relacionado con el quiz
        st.session_state.selected_subject_id = selected_subject_id
        st.session_state.selected_topic_id = None
        st.session_state.questions = []
        st.session_state.user_answers = {}
        st.session_state.score = 0
        st.session_state.total_questions = 0
        st.session_state.review = []
        st.session_state.step = "select_topic"
        st.rerun()


# ---------------------- PANTALLA 2: SELECCIONAR TEMA ---------------------- #


def select_topic_step():
    st.header("📝 Selecciona el tema")

    subject_id = st.session_state.selected_subject_id
    if subject_id is None:
        st.error("No se ha seleccionado ninguna asignatura.")
        st.session_state.step = "select_subject"
        st.rerun()
        return

    subject_name = get_subject_name(subject_id) or "Asignatura"
    st.subheader(f"Asignatura: **{subject_name}**")

    topics = get_topics_by_subject(subject_id)

    if not topics:
        st.warning("No hay temas para esta asignatura.")
        if st.button("⬅️ Volver a asignaturas"):
            st.session_state.step = "select_subject"
            st.rerun()
        return

    topic_labels = [f"Tema {t['number']}: {t['name']}" for t in topics]
    id_by_label = {topic_labels[i]: topics[i]["id"] for i in range(len(topics))}

    # Preselección si ya había tema
    if st.session_state.selected_topic_id is not None:
        try:
            default_index = topic_labels.index(
                next(
                    f"Tema {t['number']}: {t['name']}"
                    for t in topics
                    if t["id"] == st.session_state.selected_topic_id
                )
            )
        except StopIteration:
            default_index = 0
    else:
        default_index = 0

    selected_label = st.selectbox(
        "Elige un tema:",
        topic_labels,
        index=default_index,
    )
    selected_topic_id = id_by_label[selected_label]

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Cambiar asignatura"):
            st.session_state.step = "select_subject"
            st.rerun()

    with col2:
        if st.button("Empezar cuestionario ✅"):
            start_quiz_for_topic(selected_topic_id)
            st.rerun()


# ---------------------- PANTALLA 3: CUESTIONARIO (TODAS LAS PREGUNTAS) ---------------------- #


def quiz_step():
    st.header("📖 Cuestionario")

    questions = st.session_state.questions
    if not questions:
        st.error("No hay preguntas cargadas para este tema.")
        if st.button("⬅️ Volver a temas"):
            st.session_state.step = "select_topic"
            st.rerun()
        return

    subject_id = st.session_state.selected_subject_id
    topic_id = st.session_state.selected_topic_id
    subject_name = get_subject_name(subject_id) or "Asignatura"
    topic_label = build_topic_label(subject_id, topic_id)

    st.caption(f"**{subject_name}** · {topic_label}")
    st.write(f"Total de preguntas: **{len(questions)}**")

    # Mostramos TODAS las preguntas a la vez
    for idx, question in enumerate(questions, start=1):
        st.markdown(f"### {idx}. {question['text']}")

        options = question["options"]
        option_ids = [opt["id"] for opt in options]

        # Mapa id -> "A. Texto"
        def format_option(opt_id):
            opt = next(o for o in options if o["id"] == opt_id)
            label = opt.get("label")
            if label:
                return f"{label}. {opt['text']}"
            return opt["text"]

        saved = st.session_state.user_answers.get(question["id"], None)

        # Radio SIN opción preseleccionada al inicio (index=None)
        selected_option_id = st.radio(
            "Selecciona una opción:",
            option_ids,
            index=option_ids.index(saved) if saved in option_ids else None,
            format_func=format_option,
            key=f"q_{question['id']}",
        )

        # Guardamos en el dict de respuestas
        st.session_state.user_answers[question["id"]] = selected_option_id

        st.markdown("---")

    # Botones debajo de todo
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("⬅️ Volver a elegir tema"):
            # Volver a pantalla de temas y limpiar solo cosas del cuestionario
            st.session_state.step = "select_topic"
            st.session_state.questions = []
            st.session_state.user_answers = {}
            st.session_state.score = 0
            st.session_state.total_questions = 0
            st.session_state.review = []
            st.rerun()

    with col2:
        if st.button("✅ Corregir cuestionario"):
            finish_quiz()  # calcula nota y review
            st.session_state.step = "results"
            st.rerun()


# ---------------------- CORRECCIÓN Y RESULTADOS ---------------------- #


def finish_quiz():
    questions = st.session_state.questions
    answers = st.session_state.user_answers

    correct_count = 0
    review = []

    for q in questions:
        q_id = q["id"]
        options = q["options"]
        selected_option_id = answers.get(q_id)

        # Buscar opción correcta
        correct_option = next((o for o in options if o["is_correct"]), None)

        selected_option = None
        if selected_option_id is not None:
            selected_option = next(
                (o for o in options if o["id"] == selected_option_id),
                None,
            )

        is_correct = (
            selected_option is not None
            and correct_option is not None
            and selected_option["id"] == correct_option["id"]
        )

        if is_correct:
            correct_count += 1

        review.append(
            {
                "question_text": q["text"],
                "is_correct": is_correct,
                "correct_label": correct_option.get("label") if correct_option else None,
                "correct_text": correct_option.get("text") if correct_option else None,
                "selected_label": selected_option.get("label")
                if selected_option
                else None,
                "selected_text": selected_option.get("text")
                if selected_option
                else None,
            }
        )

    total = len(questions)
    st.session_state.score = correct_count
    st.session_state.total_questions = total
    st.session_state.review = review


def results_step():
    st.header("📊 Resultado del cuestionario")

    score = st.session_state.score
    total = st.session_state.total_questions
    review = st.session_state.review
    subject_id = st.session_state.selected_subject_id
    topic_id = st.session_state.selected_topic_id

    # Cabecera con asignatura y "Tema X: ..."
    subject_name = get_subject_name(subject_id) or "Asignatura"
    topic_label = build_topic_label(subject_id, topic_id)
    st.caption(f"**{subject_name}** · {topic_label}")

    if total == 0 or not review:
        st.warning("No hay resultados para mostrar.")
        if st.button("Volver a temas", key="btn_results_back_if_empty"):
            st.session_state.step = "select_topic"
            st.rerun()
        return

    pct = (score / total) * 100
    st.write(f"Has acertado **{score} de {total}** preguntas. (**{pct:.1f}%**)")

    if pct == 100:
        st.success("¡Perfecto! 🎉")
    elif pct >= 70:
        st.success("Muy bien, buen nivel 💪")
    elif pct >= 50:
        st.info("No está mal, pero hay margen de mejora 📚")
    else:
        st.warning("Toca repasar un poco más. Puedes volver a intentarlo 😉")

    # Separar acertadas y falladas
    correct_questions = [r for r in review if r["is_correct"]]
    wrong_questions = [r for r in review if not r["is_correct"]]

    st.markdown("---")
    st.subheader("✅ Preguntas acertadas")
    if not correct_questions:
        st.write("No has acertado ninguna en este intento.")
    else:
        for idx, r in enumerate(correct_questions, start=1):
            st.markdown(f"**{idx}. {r['question_text']}**")
            st.write(
                f"✅ Respuesta correcta: **{r['correct_label']}. {r['correct_text']}**"
            )

    st.markdown("---")
    st.subheader("❌ Preguntas falladas")
    if not wrong_questions:
        st.write("No has fallado ninguna, ¡enhorabuena! 🎉")
    else:
        for idx, r in enumerate(wrong_questions, start=1):
            st.markdown(f"**{idx}. {r['question_text']}**")

            if r["selected_label"] is None:
                st.write("❌ No respondiste esta pregunta.")
            else:
                st.write(
                    f"❌ Tu respuesta: **{r['selected_label']}. {r['selected_text']}**"
                )

            st.write(
                f"✅ Respuesta correcta: **{r['correct_label']}. {r['correct_text']}**"
            )

    st.markdown("---")

    # ---------- PRIMERO: BOTONES TEMA ANTERIOR / SIGUIENTE (JUNTOS) ---------- #
    topics = get_topics_by_subject(subject_id) if subject_id is not None else []
    topic_ids_ordered = [t["id"] for t in topics]

    prev_topic_id = None
    next_topic_id = None

    if topic_id in topic_ids_ordered:
        idx = topic_ids_ordered.index(topic_id)
        if idx > 0:
            prev_topic_id = topic_ids_ordered[idx - 1]
        if idx < len(topic_ids_ordered) - 1:
            next_topic_id = topic_ids_ordered[idx + 1]

    nav_prev_col, nav_next_col = st.columns(2)

    with nav_prev_col:
        if prev_topic_id is not None:
            if st.button("⬅️ Tema anterior", key="btn_prev_topic"):
                start_quiz_for_topic(prev_topic_id)
                st.rerun()

    with nav_next_col:
        if next_topic_id is not None:
            if st.button("Siguiente tema ➡️", key="btn_next_topic"):
                start_quiz_for_topic(next_topic_id)
                st.rerun()

    st.markdown("")

    # ---------- DESPUÉS: BOTONES PRINCIPALES (REPETIR / VOLVER A ELEGIR TEMA) ---------- #
    top_col1, top_col2 = st.columns(2)

    with top_col1:
        if st.button("🔁 Repetir este tema", key="btn_repeat_topic"):
            if topic_id is not None:
                start_quiz_for_topic(topic_id)
                st.rerun()

    with top_col2:
        if st.button("🔙 Volver a elegir tema", key="btn_back_to_topics"):
            st.session_state.step = "select_topic"
            st.session_state.questions = []
            st.session_state.user_answers = {}
            st.session_state.score = 0
            st.session_state.total_questions = 0
            st.session_state.review = []
            st.rerun()


# ---------------------- MAIN ---------------------- #


def main():
    st.set_page_config(
        page_title="Prevención de riesgos profesionales",
        page_icon="✅",
        layout="centered",
    )

    init_state()

    # 🔐 Comprobar login antes de mostrar la app
    if not st.session_state.logged_in:
        login_screen()
        return

    st.title("FP Quiz – Prevención de riesgos profesionales")

    step = st.session_state.step

    if step == "select_subject":
        select_subject_step()
    elif step == "select_topic":
        select_topic_step()
    elif step == "quiz":
        quiz_step()
    elif step == "results":
        results_step()
    else:
        # Por si el estado se corrompe
        st.session_state.step = "select_subject"
        st.rerun()


if __name__ == "__main__":
    main()
