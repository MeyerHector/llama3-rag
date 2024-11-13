from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from langchain_ollama import OllamaLLM

app = Flask(__name__)

# Configuración global de CORS para todas las rutas
CORS(app, origins="http://localhost:3000")  # Permite solicitudes desde localhost:3000 a todas las rutas

cached_llm = OllamaLLM(model="llama3")

@app.route("/ai", methods=["POST"])
@cross_origin(origins="http://localhost:3000")  # Esto sobrescribe o añade configuraciones específicas para esta ruta
def aiPost():
    print("Post /ai called")
    json_content = request.json
    query = json_content.get("query")
    response_data = {"response": cached_llm.invoke(query)}

    return jsonify(response_data)

@app.route("/ai", methods=["OPTIONS"])
@cross_origin(origins="http://localhost:3000")  # Habilita CORS para las solicitudes OPTIONS también
def ai_options():
    return "", 200  # Responde vacío, solo con los encabezados CORS

def startup_app():
    app.run(host="0.0.0.0", port=4000, debug=True)

if __name__ == "__main__":
    startup_app()
