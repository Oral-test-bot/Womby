# Womby

## Deploy URL
[Página de deploy](englishbot.streamlit.app)

## How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Add the api key on the root project directory in a .env file, in the same way as .env.example

3. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```

## Agregar un nuevo Prompt
Para configurar un segundo Prompt es necesario crear un archivo de texto (.txt)  con el texto del Prompt que se quiere configurar en la carpeta prompts (/static/prompts es la ruta). El nombre del archivo de texto es el nombre que aparecerá en la interfaz de Womby. Es posible que sea necesario hacer reboot de la aplicación desde Streamlit para que se apliquen los cambios.

## Agregar preguntas, unidades y/o niveles
Para agregar preguntas, unidades y/o niveles de inglés se debe editar el archivo courses_info.json. En este se deben agregar los elementos deseados siguiendo el formato ya establecido en el mismo archivo. Es posible que sea necesario hacer reboot de la aplicación desde Streamlit para que se apliquen los cambios.
