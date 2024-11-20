import { useState } from "react";
import { FaFileAlt, FaArrowUp } from "react-icons/fa";

function App() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [uploadResponse, setUploadResponse] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      alert("Por favor selecciona un archivo PDF.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      const res = await fetch("http://localhost:5000/pdf", {
        method: "POST",
        body: formData,
      });
      if (res.ok) {
        const data = await res.json();
        setUploadResponse(`Archivo subido: ${data.filename}, chunks procesados: ${data.chunk_len}`);
      } else {
        const errorData = await res.json();
        setUploadResponse(`Error: ${errorData.error}`);
      }
    } catch (error) {
      console.error("Error al subir el archivo:", error);
      setUploadResponse("Error al subir el archivo.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      alert("Por favor sube un archivo PDF antes de hacer una consulta.");
      return;
    }
    setLoading(true);
  
    try {
      const res = await fetch("http://localhost:5000/ask-pdf", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });
  
      if (!res.ok) {
        const errorData = await res.json();
        console.error("Error al hacer la solicitud:", errorData);
        setResponse(`Error: ${errorData.message || "Error desconocido"}`);
        return;
      }
  
      const data = await res.json();
      if (data.result) {
        setResponse(data.result);
      } else {
        setResponse("No se recibió una respuesta válida.");
      }
    } catch (error) {
      console.error("Error al hacer la solicitud:", error);
      setResponse("Hubo un error al procesar tu consulta.");
    } finally {
      setLoading(false);
    }
  };
  

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>Carga y Consulta IA</h1>

        <form onSubmit={handleFileUpload} style={styles.form}>
          <div style={styles.fileInputWrapper}>
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              style={styles.fileInput}
              id="fileInput"
            />
            <label htmlFor="fileInput" style={styles.fileInputLabel}>
              <FaFileAlt style={{ marginRight: 7 }} />
              Seleccionar PDF
            </label>
          </div>
          <button type="submit" style={styles.button}>
            <FaArrowUp style={{ marginRight: 7 }} />
            Subir PDF
          </button>
        </form>

        {uploadResponse && <p style={styles.responseText}>{uploadResponse}</p>}

        <form onSubmit={handleSubmit} style={styles.form}>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Escribe tu pregunta aquí..."
            rows="4"
            style={styles.textarea}
          />
          <button type="submit" style={styles.button}>
            Enviar Consulta
          </button>
        </form>

        {loading && (
          <div style={styles.loadingContainer}>
            <div style={styles.spinner}></div>
            <p style={styles.loadingText}>Procesando...</p>
          </div>
        )}

        {response && !loading && (
          <div style={styles.responseContainer}>
            <h2 style={styles.responseTitle}>Respuesta:</h2>
            <p style={styles.responseText}>{response}</p>
          </div>
        )}
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    backgroundColor: '#f0f2f5',
    padding: '20px',
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: '12px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    padding: '40px',
    width: '100%',
    maxWidth: '600px',
  },
  title: {
    fontSize: '28px',
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: '30px',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
    marginBottom: '30px',
  },
  fileInputWrapper: {
    position: 'relative',
    overflow: 'hidden',
    display: 'inline-block',
    maxWidth: '200px',
  },
  fileInput: {
    fontSize: '100px',
    position: 'absolute',
    left: '0',
    top: '0',
    opacity: '0',
  },
  fileInputLabel: {
    display: 'inline-block',
    padding: '10px 20px',
    backgroundColor: '#4CAF50',
    color: 'white',
    borderRadius: '5px',
    cursor: 'pointer',
    transition: 'background-color 0.3s',
  },
  button: {
    padding: '12px 24px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    fontSize: '16px',
    cursor: 'pointer',
    transition: 'background-color 0.3s',
    width: '100%', 
  },
  textarea: {
    width: '96%', 
    padding: '12px',
    borderRadius: '5px',
    border: '1px solid #ddd',
    fontSize: '16px',
    resize: 'vertical',
  },
  loadingContainer: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: '20px',
  },
  spinner: {
    border: '3px solid #f3f3f3',
    borderTop: '3px solid #3498db',
    borderRadius: '50%',
    width: '30px',
    height: '30px',
    animation: 'spin 1s linear infinite',
  },
  loadingText: {
    marginLeft: '15px',
    fontSize: '18px',
    color: '#666',
  },
  responseContainer: {
    marginTop: '30px',
    padding: '20px',
    backgroundColor: '#f8f9fa',
    borderRadius: '8px',
  },
  responseTitle: {
    fontSize: '22px',
    fontWeight: 'bold',
    color: '#333',
    marginBottom: '15px',
  },
  responseText: {
    fontSize: '16px',
    color: '#333',
    lineHeight: '1.6',
  },
};

export default App;