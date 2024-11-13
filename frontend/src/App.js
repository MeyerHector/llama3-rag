import { useState } from "react";

function App() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch("http://localhost:4000/ai", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      if (res.ok) {
        const data = await res.json();
        setResponse(data.response);
      } else {
        console.error("Error al hacer la solicitud:", res.statusText);
      }
    } catch (error) {
      console.error("Error al hacer la solicitud:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>Consulta a la IA</h1>
        <form onSubmit={handleSubmit} style={styles.form}>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Escribe tu pregunta aquí..."
            rows="4"
            style={styles.textarea}
          />
          <button type="submit" style={styles.button}>
            Enviar
          </button>
        </form>

        {loading && (
          <div style={styles.loadingContainer}>
            <div style={styles.spinner}></div>
            <p style={styles.loadingText}>Procesando tu pregunta...</p>
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
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    height: "100vh",
    backgroundColor: "#f4f7fc",
    padding: "20px",
    boxSizing: "border-box",
  },
  card: {
    backgroundColor: "#fff",
    padding: "30px",
    borderRadius: "10px",
    boxShadow: "0 4px 10px rgba(0, 0, 0, 0.1)",
    maxWidth: "600px",
    width: "100%",
    boxSizing: "border-box",
    overflow: "hidden",
    wordWrap: "break-word",
  },
  title: {
    fontFamily: "'Roboto', sans-serif",
    fontSize: "2rem",
    color: "#333",
    marginBottom: "20px",
    textAlign: "center",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "10px",
  },
  textarea: {
    padding: "12px",
    borderRadius: "8px",
    border: "1px solid #ddd",
    fontSize: "1rem",
    fontFamily: "'Roboto', sans-serif",
    outline: "none",
    transition: "border 0.3s ease",
    resize: "vertical",
    minHeight: "100px",
    boxSizing: "border-box",
  },
  button: {
    padding: "12px 20px",
    border: "none",
    backgroundColor: "#4e89f1",
    color: "#fff",
    fontSize: "1rem",
    fontWeight: "bold",
    borderRadius: "8px",
    cursor: "pointer",
    transition: "background-color 0.3s ease, transform 0.3s ease",
    boxSizing: "border-box",
  },
  loadingContainer: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    marginTop: "20px",
  },
  spinner: {
    border: "4px solid #f3f3f3",
    borderTop: "4px solid #4e89f1",
    borderRadius: "50%",
    width: "30px",
    height: "30px",
    animation: "spin 2s linear infinite",
  },
  loadingText: {
    marginLeft: "10px",
    fontSize: "1rem",
    color: "#666",
  },
  responseContainer: {
    marginTop: "20px",
    padding: "15px",
    backgroundColor: "#f9f9f9",
    borderRadius: "8px",
    boxShadow: "0 2px 5px rgba(0, 0, 0, 0.1)",
    overflowWrap: "break-word",
    maxHeight: "300px",
    overflowY: "auto",
  },
  responseTitle: {
    fontSize: "1.5rem",
    color: "#333",
    marginBottom: "10px",
  },
  responseText: {
    fontSize: "1rem",
    color: "#555",
    lineHeight: "1.5",
    wordWrap: "break-word",
  },
};

const styleSheet = document.styleSheets[0];
styleSheet.insertRule(
  `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`,
  styleSheet.cssRules.length
);

export default App;
