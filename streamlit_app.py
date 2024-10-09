import streamlit as st
from openai import OpenAI
from constants import PROMPTS_PATH, COURSES_INFO_PATH
import json
import os

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses OpenAI's GPT-3.5 model to generate responses. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
    "You can also learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Obtenemos los nombres de los archivos de los prompts
    prompt_files = os.listdir(PROMPTS_PATH)

    # Cargar el contenido de los prompts y mostrarlo en la barra lateral
    with st.sidebar:
        prompt_choice = st.selectbox(
            "Selecciona un prompt inicial", prompt_files, index=0
        )

        with open(os.path.join(PROMPTS_PATH, prompt_choice), "r") as prompt_file:
            instructions_prompt = prompt_file.read()

        # Cargar JSON de los niveles, unidades y preguntas
        with open(COURSES_INFO_PATH, "r") as courses_info_file:
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
    instructions_prompt += f"\n\nPregunta a responder: {pregunta}\nRespuesta:"

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "user", "content": instructions_prompt}]

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages[1:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("What is up?"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response using the OpenAI API.
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # Stream the response to the chat using `st.write_stream`, then store it in 
        # session state.
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
