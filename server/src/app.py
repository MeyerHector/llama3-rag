from langchain_ollama import OllamaLLM
from flask import Flask, request

app = Flask(__name__)


cached_llm = OllamaLLM(model="llama3")


@app.route("/ai", methods=["POST"])
def aiPost():
    print("Post /ai called")
    json_content = request.json
    query = json_content.get("query")
    return {"response": cached_llm.invoke(query)}

def startup_app(): 
    app.run(host="0.0.0.0", port=4000, debug=True)

if __name__ == "__main__":
    startup_app()
