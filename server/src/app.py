import os
import gc
from flask import Flask, request, Response, stream_with_context
from langchain_ollama import ChatOllama
from langchain_community.document_loaders import PDFPlumberLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import shutil
import json

os.environ["ALLOW_RESET"] = "TRUE"

app = Flask(__name__)
folder_path = "chroma_db_dir"
pdf_folder = "./pdf"

# Crear directorios si no existen
os.makedirs(pdf_folder, exist_ok=True)
os.makedirs(folder_path, exist_ok=True)

# Definir el modelo LLM
llm = ChatOllama(model="llama3.2:1b")

# Definir el modelo de embeddings
embed_model = FastEmbedEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Definir el prompt personalizado
custom_prompt_template = """ Responde siempre en español. Usa la informacion proporcionada para encontrar la respuesta mas adecuada. Si no encuentras lo solicitado di que no tienes esa informacion

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

def stream_response(response):
    for chunk in response:
        # Asegurarse de que el chunk es una cadena o dict antes de codificarlo
        if isinstance(chunk, dict):
            yield json.dumps(chunk).encode('utf-8')
        else:
            yield str(chunk).encode('utf-8')

# Ruta para subir y procesar el PDF
@app.route("/pdf", methods=["POST"])
def pdfPost():
    global qa, vector_store
    
    # Verificar si se ha subido un archivo
    if 'file' not in request.files:
        return {"error": "No se ha subido ningún archivo"}, 400
    
    file = request.files['file']
    if file.filename == '':
        return {"error": "El nombre del archivo está vacío"}, 400
    
    if file and file.filename.endswith(".pdf"):
        try:
            # Eliminar todos los archivos en ./pdf
            for filename in os.listdir(pdf_folder):
                file_path = os.path.join(pdf_folder, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            
            # Eliminar el directorio de persistencia de Chroma si existe
            if os.path.exists(folder_path):
                try:
                    # Cerrar y eliminar referencias a Chroma
                    qa = None
                    vector_store = None
                    gc.collect()
                    
                    # Intentar eliminar el directorio
                    shutil.rmtree(folder_path)
                except Exception as e:
                    print(f"Error al eliminar el directorio de Chroma: {e}")
                    return {"error": "No se pudo procesar el PDF debido a un error interno al eliminar Chroma."}, 500
        except Exception as e:
            print(f"Error al eliminar archivos/directorio: {e}")
            return {"error": "No se pudo procesar el PDF debido a un error interno."}, 500

        try:
            # Guardar nuevo PDF
            save_file = os.path.join(pdf_folder, file.filename)
            file.save(save_file)
            print("Archivo subido:", file.filename)

            # Cargar y procesar el PDF
            loader = PDFPlumberLoader(save_file)
            data_pdf = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=80)
            chunks = text_splitter.split_documents(data_pdf)
            print(f"Cantidad de chunks: {len(chunks)}")

            # Crear y persistir el vector store
            vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=embed_model,
                persist_directory=folder_path,
                collection_name="chroma_collection"
            )

            # Crear el retriever y el chain de QA
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
            print(f"Error al procesar el PDF: {e}")
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