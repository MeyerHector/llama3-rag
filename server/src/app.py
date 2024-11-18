import os
import gc
import threading
from flask_cors import CORS, cross_origin
from flask import Flask, request, Response, stream_with_context
from langchain_ollama import ChatOllama
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
import shutil
import json
import traceback

os.environ["ALLOW_RESET"] = "TRUE"

app = Flask(__name__)
folder_path = "chroma_db_dir"
pdf_folder = "./pdf"


# Configuración global de CORS para todas las rutas
CORS(app, origins="http://localhost:3000")  # Permite solicitudes desde localhost:3000 a todas las rutas
# Crear directorios si no existen
os.makedirs(pdf_folder, exist_ok=True)
os.makedirs(folder_path, exist_ok=True)

# Definir el modelo LLM
llm = ChatOllama(model="llama3.2:1b")


@app.route("/ai", methods=["POST"])
@cross_origin(origins="http://localhost:3000")  # Esto sobrescribe o añade configuraciones específicas para esta ruta
def aiPost():
    print("Post /ai called")
    json_content = request.json
    query = json_content.get("query")

    # Llama al modelo LLM
    ai_response = llm.invoke(query)

    # Extrae el contenido de la respuesta
    if hasattr(ai_response, 'content'):
        response_data = {"response": ai_response.content}
    else:
        response_data = {"response": "Error: El modelo no devolvió contenido válido."}

    print(response_data)
    return response_data


@app.route("/ai", methods=["OPTIONS"])
@cross_origin(origins="http://localhost:3000")  # Habilita CORS para las solicitudes OPTIONS también
def ai_options():
    return "", 200  # Responde vacío, solo con los encabezados CORS

def startup_app():
    app.run(host="0.0.0.0", port=4000, debug=True)

# Definir el modelo de embeddings
embed_model = FastEmbedEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Definir el prompt personalizado
custom_prompt_template = """ Responde siempre en español. Usa la informacion proporcionada para encontrar la respuesta mas adecuada. Si no encuentras lo solicitado di que no tienes esa informacion y no respondas.

Contexto: {context}
Pregunta: {question}

Respuesta:
"""
prompt = PromptTemplate(
    template=custom_prompt_template,
    input_variables=['context', 'question']
)

# Variables globales para el chain de QA y el vector_store
qa = None
vector_store = None
delete_lock = threading.Lock()

def stream_response(response):
    for chunk in response:
        # Asegurarse de que el chunk es una cadena o dict antes de codificarlo
        if isinstance(chunk, dict):
            yield json.dumps(chunk).encode('utf-8')
        else:
            yield str(chunk).encode('utf-8')

def remove_folder_safely(folder_path):
    try:
        shutil.rmtree(folder_path)
        print(f"Directorio {folder_path} eliminado correctamente.")
    except Exception as e:
        print(f"Error al eliminar el directorio {folder_path}: {traceback.format_exc()}")

# Ruta para subir y procesar el PDF
@app.route("/pdf", methods=["POST"])
def pdfPost():
    global qa, vector_store

    if 'file' not in request.files:
        return {"error": "No se ha subido ningún archivo"}, 400

    file = request.files['file']
    if file.filename == '':
        return {"error": "El nombre del archivo está vacío"}, 400

    if file and file.filename.endswith(".pdf"):
        try:
            # Eliminar archivos en ./pdf
            for filename in os.listdir(pdf_folder):
                file_path = os.path.join(pdf_folder, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

            # Eliminar directorio de persistencia de Chroma
            with delete_lock:
                if os.path.exists(folder_path):
                    try:
                        # Liberar recursos
                        qa = None
                        vector_store = None
                        gc.collect()

                        # Intentar eliminar el directorio
                        remove_folder_safely(folder_path)
                    except Exception as e:
                        print(f"Error al eliminar {folder_path}: {traceback.format_exc()}")
                        return {"error": "Error al eliminar archivos abiertos en Chroma."}, 500
                else:
                    print(f"El directorio {folder_path} no existe, no es necesario eliminarlo.")

            # Guardar nuevo PDF
            save_file = os.path.join(pdf_folder, file.filename)
            file.save(save_file)
            print("Archivo subido:", file.filename)

            # Procesar el PDF
            loader = PDFPlumberLoader(save_file)
            data_pdf = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=80)
            chunks = text_splitter.split_documents(data_pdf)
            print(f"Cantidad de chunks: {len(chunks)}")

            # Crear vector_store
            vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=embed_model,
                persist_directory=folder_path,
                collection_name="chroma_collection"
            )

            # Configurar QA chain
            retriever = vector_store.as_retriever(search_kwargs={'k': 5})
            qa = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=False,
                chain_type_kwargs={'prompt': prompt}
            )

            return {"status": "success", "filename": file.filename, "chunk_len": len(chunks)}
        except Exception as e:
            print(f"Error al procesar el PDF: {traceback.format_exc()}")
            return {"error": "No se pudo procesar el PDF debido a un error interno."}, 500
    else:
        return {"error": "El archivo debe ser un PDF"}, 400

# Ruta para realizar consultas al PDF procesado con streaming
@app.route("/ask-pdf", methods=["POST"])
def askPdfPost():
    global qa
    if qa is None:
        return {"error": "No se ha cargado ningún PDF. Por favor, sube un PDF primero."}, 400

    data = request.get_json()
    if not data or "query" not in data:
        return {"error": "No se proporcionó ninguna pregunta"}, 400

    query = data["query"]

    def generate():
        try:
            response = qa.stream({"query": query})
            for chunk in response:
                if isinstance(chunk, dict):
                    yield json.dumps(chunk).encode('utf-8')
                else:
                    yield str(chunk).encode('utf-8')
        except Exception as e:
            error_message = json.dumps({"error": "Error al procesar la consulta."}).encode('utf-8')
            yield error_message

    return Response(stream_with_context(generate()), mimetype='application/json')

if __name__ == "__main__":
    app.run(debug=True)