# Proyecto de IA con Flask Ollama y React

Este proyecto es una aplicación web que permite cargar archivos PDF y realizar consultas a través de un modelo de lenguaje (LLM). La aplicación está dividida en dos partes: un servidor backend desarrollado con Flask y un frontend desarrollado con React.

## Instalación

### Backend

1. Clona el repositorio.
2. Navega al directorio `server`.
3. Crea y activa un entorno virtual:
   ```sh
   python -m venv venv
   source venv/bin/activate  # En macOS/Linux
   .\venv\Scripts\activate   # En Windows
   ```
4. Instala las dependencias:
   ```sh
   pip install -r requirements.txt
   ```
5. Ejecuta el servidor:
   ```sh
   python src/app.py
   ```

### Frontend

1. Navega al directorio `frontend`.
2. Instala las dependencias:
   ```sh
   npm install
   ```
3. Ejecuta la aplicación:
   ```sh
   npm start
   ```

## Uso

### Subir un PDF

1. Abre la aplicación en tu navegador en `http://localhost:3000`.
2. Selecciona un archivo PDF y súbelo.
3. El servidor procesará el PDF y lo dividirá en chunks.

### Realizar Consultas

1. Una vez que el PDF esté procesado, puedes realizar consultas escribiendo una pregunta en el campo de texto y enviándola.
2. La respuesta se mostrará en la pantalla.

## Rutas del Backend

- `POST /pdf`: Sube y procesa un archivo PDF.
- `POST /ask-pdf`: Realiza una consulta al PDF procesado.
