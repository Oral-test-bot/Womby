from pyexpat import model
import streamlit as st
from openai import OpenAI
from constants import PROMPTS_PATH, COURSES_INFO_PATH
import json
import os
from VoiceRecognition import VoiceRecognition

st.set_page_config(
    page_title="Womby",
    page_icon="🐨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Show title and description.
st.title("🐨 Womby")

load_dotenv()
openai_api_key = os.getenv("API_KEY")


# Función para agregar un nuevo mensaje y refrescar
def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})
    st.rerun()


def add_message_without_rerun(role, content):
    st.session_state.messages.append({"role": role, "content": content})


if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

# Create an OpenAI client.
client = OpenAI(api_key=st.secrets["API_KEY"])

# Obtenemos los nombres de los archivos de los prompts
prompt_files = os.listdir(PROMPTS_PATH)

# Cargar el contenido de los prompts y mostrarlo en la barra lateral
with st.sidebar:
    prompt_choice = st.selectbox(
        "Selecciona un prompt inicial", prompt_files, index=0
    )

    # Abrir el archivo con codificación UTF-8
    with open(
        os.path.join(PROMPTS_PATH, prompt_choice), "r", encoding="utf-8"
    ) as prompt_file:
        instructions_prompt = prompt_file.read()

    # Cargar JSON de los niveles, unidades y preguntas
    with open(COURSES_INFO_PATH, "r", encoding="utf-8") as courses_info_file:
        cursos_data = json.load(courses_info_file)

    # Selector de nivel
    niveles = list(cursos_data.keys())
    nivel = st.selectbox("Selecciona tu nivel de inglés", niveles)

    # Filtrar las unidades según el nivel seleccionado
    unidades = list(cursos_data[nivel].keys())
    unidad = st.selectbox("Selecciona tu unidad", unidades)

    # Filtrar las preguntas según la unidad seleccionada
    preguntas = cursos_data[nivel][unidad]
    pregunta = st.selectbox("Selecciona una pregunta", preguntas)

    # Concatenar el prompt inicial con la pregunta seleccionada
    prompt_context = f"{instructions_prompt.strip()}\n\n"
    template_user_answer = """
    Pregunta: {pregunta}
    Respuesta: {respuesta}
    """

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "user", "content": prompt_context},
            {
                "role": "assistant",
                "content": f"Hola! Estaré esperando tu respuesta a tu pregunta.",
            },
        ]

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages[1:]:
        lnk_to_wombat = "https://attic.sh/xi1yhgxjqf1dvx5hxm98su4gzpal"
        lnk_to_student = "https://images.emojiterra.com/google/noto-emoji/unicode-16.0/color/svg/1f9d1-1f393.svg"
        avatar = lnk_to_student if message["role"] == "user" else lnk_to_wombat
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Variable para almacenar el texto transcrito
    if "transcription" not in st.session_state:
        st.session_state.transcription = ""

    audio_input, text_input, send_answer = st.columns([0.8, 4, 0.6])

    with audio_input:
        # Entrada de audio
        voice_response = st.experimental_audio_input(
            "Voice input", label_visibility="collapsed"
        )
        transcriptor = VoiceRecognition()

    with text_input:
        # Si hay respuesta de voz, se muestra la transcripción
        if voice_response:
            text = transcriptor.to_text(voice_response, client)
            st.session_state.transcription = text
            user_input = st.text_area(
                "Ingrese su respuesta",
                st.session_state.transcription,
                label_visibility="collapsed",
            )
        else:
            user_input = st.text_area(
                "Ingrese su respuesta", label_visibility="collapsed"
            )

    with send_answer:
        # Crear un botón para que el usuario confirme su mensaje antes de enviarlo
        # Que el botón quede centrado verticalmente, o use todo el alto del contenedor
        if st.button(
            "✉️ Enviar respuesta", use_container_width=True, disabled=not user_input
        ):
            user_answer = template_user_answer.format(
                pregunta=pregunta, respuesta=user_input
            )

            # Store and display the current prompt.
            add_message_without_rerun("user", user_answer)

            # Generate a response using the OpenAI API.
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=False,
            )
            response = stream.choices[0].message.content
            add_message("assistant", response)
