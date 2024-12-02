import streamlit as st
from openai import OpenAI
from constants import PROMPTS_PATH, COURSES_INFO_PATH
import json
import os
from VoiceRecognition import VoiceRecognition
from chat_email import send_email

st.set_page_config(
    page_title="Womby",
    page_icon="🐨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Show title and description.
st.title("Womby")


# Función para agregar un nuevo mensaje y refrescar
def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})
    st.rerun()


def add_message_without_rerun(role, content):
    st.session_state.messages.append({"role": role, "content": content})


# Create an OpenAI client.
client = OpenAI(api_key=st.secrets["API_KEY"])

# Obtenemos los nombres de los archivos de los prompts
prompt_files = os.listdir(PROMPTS_PATH)

# Cargar el contenido de los prompts y mostrarlo en la barra lateral
with st.sidebar:
    prompt_choice = st.selectbox("Selecciona un prompt inicial", prompt_files, index=0)

    # Abrir el archivo con codificación UTF-8
    with open(
        os.path.join(PROMPTS_PATH, prompt_choice), "r", encoding="utf-8"
    ) as prompt_file:
        instructions_prompt: str = prompt_file.read()

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
    preguntas = cursos_data[nivel][unidad]["questions"]
    pregunta = st.selectbox("Selecciona una pregunta", preguntas)

    # Filtramos el vocabulario según la unidad seleccionada
    vocabulario = cursos_data[nivel][unidad]["vocabulary"]

    # Reemplazamos el vocabulario en el prompt
    instructions_prompt = instructions_prompt.replace("<VOCABULARY>", vocabulario)

    st.write(f"**Pregunta seleccionada:** {pregunta}")

    # Añadir un botón para enviar los mensajes por correo
    if st.button("Enviar historial por correo"):
        # Concatenar los mensajes
        messages_to_send = st.session_state.messages[2:]
        messages_history = "\n".join(
            [f"{m['role']}: {m['content']}" for m in messages_to_send]
        )

        # Configura los detalles del correo
        subject = "Historial de Mensajes Womby"
        body = messages_history
        to_email = st.secrets["EMAIL_RECIPIENT"]
        from_email = st.secrets["SMTP_USER"]
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_user = st.secrets["SMTP_USER"]
        smtp_password = st.secrets["SMTP_PASSWORD"]
        try:
            send_email(
                subject,
                body,
                to_email,
                from_email,
                smtp_server,
                smtp_port,
                smtp_user,
                smtp_password,
            )
            st.success("Correo enviado exitosamente!")
        except Exception as e:
            st.error(f"Error al enviar el correo: {e}")

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
        {
            "role": "assistant",
            "content": "Hi Beauchefian! I'm happy you are here to practice with me. Answer the next question and get ready to improve your English.",
        },
    ]

# Display the existing chat messages via `st.chat_message`.
for message in st.session_state.messages:
    if message["role"] != "system":
        lnk_to_wombat = "https://attic.sh/xi1yhgxjqf1dvx5hxm98su4gzpal"
        lnk_to_student = "https://images.emojiterra.com/google/noto-emoji/unicode-16.0/color/svg/1f9d1-1f393.svg"
        avatar = lnk_to_student if message["role"] == "user" else lnk_to_wombat
        if message["role"] == "user":
            try:
                question = (
                    message["content"].split("Pregunta: ")[1].split("Respuesta: ")[0]
                )
                answer = message["content"].split("Respuesta: ")[1]
                with st.chat_message("assistant", avatar=lnk_to_wombat):
                    st.markdown(f"{question}")
                with st.chat_message("user", avatar=lnk_to_student):
                    st.markdown(f"{answer}")
            except:
                with st.chat_message(message["role"], avatar=avatar):
                    st.markdown(message["content"])
        else:
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

# Variable para almacenar el texto transcrito
if "transcription" not in st.session_state:
    st.session_state.transcription = ""
if "voice_response" not in st.session_state:
    st.session_state.voice_response = ""

if pregunta:
    st.write(f"**Pregunta seleccionada:** {pregunta}")

audio_input, text_input, send_answer = st.columns([0.8, 4, 0.6])

with audio_input:
    # Entrada de audio
    st.session_state.voice_response = st.experimental_audio_input(
        "Voice input", label_visibility="collapsed"
    )

with text_input:
    # Si hay respuesta de voz, se muestra la transcripción
    if st.session_state.voice_response:
        transcriptor = VoiceRecognition()
        st.session_state.transcription = transcriptor.to_text(
            st.session_state.voice_response, client
        )

    user_input = st.text_area(
        label="Text input",
        value=st.session_state.transcription,
        label_visibility="collapsed",
    )

with send_answer:
    # Crear un botón para que el usuario confirme su mensaje antes de enviarlo
    # Que el botón quede centrado verticalmente, o use todo el alto del contenedor
    if st.button("✉️ Enviar", use_container_width=True, disabled=not user_input):
        # Use actual prompt
        add_message_without_rerun("system", prompt_context)

        user_answer = template_user_answer.format(
            pregunta=pregunta, respuesta=user_input
        )

        # Store and display the current prompt.
        add_message_without_rerun("user", user_answer)

        # Generate a response using the OpenAI API.
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=False,
        )
        response = stream.choices[0].message.content
        add_message("assistant", response)
