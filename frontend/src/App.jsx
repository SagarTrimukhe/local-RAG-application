import { useState, useRef, useEffect } from "react";
import { uploadPdf, askQuestion } from "./api";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setMessages((prev) => [
      ...prev,
      { role: "system", content: `Uploading ${file.name}...` },
    ]);

    try {
      const result = await uploadPdf(file);
      setUploadedFiles((prev) => [...prev, result.filename]);
      setMessages((prev) => [
        ...prev,
        { role: "system", content: result.message },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "system", content: `Upload failed: ${err.message}` },
      ]);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleAsk = async (e) => {
    e.preventDefault();
    const question = input.trim();
    if (!question || asking) return;

    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setInput("");
    setAsking(true);

    try {
      const result = await askQuestion(question);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: result.answer,
          sources: result.sources,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${err.message}` },
      ]);
    } finally {
      setAsking(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>📄 RAG Chat</h1>
        <p className="subtitle">Upload a PDF and ask questions about it</p>
      </header>

      <div className="upload-bar">
        <label className={`upload-btn ${uploading ? "disabled" : ""}`}>
          {uploading ? "Uploading..." : "📎 Upload PDF"}
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={handleUpload}
            disabled={uploading}
            hidden
          />
        </label>
        {uploadedFiles.length > 0 && (
          <span className="file-count">
            {uploadedFiles.length} file{uploadedFiles.length > 1 ? "s" : ""}{" "}
            loaded
          </span>
        )}
      </div>

      <div className="chat-container">
        <div className="messages">
          {messages.length === 0 && (
            <div className="empty-state">
              <p>Upload a PDF to get started, then ask any question about it.</p>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              <div className="message-content">
                <span className="message-label">
                  {msg.role === "user"
                    ? "You"
                    : msg.role === "assistant"
                    ? "AI"
                    : "System"}
                </span>
                <p>{msg.content}</p>
                {msg.sources && msg.sources.length > 0 && (
                  <p className="sources">
                    Sources: {msg.sources.join(", ")}
                  </p>
                )}
              </div>
            </div>
          ))}
          {asking && (
            <div className="message assistant">
              <div className="message-content">
                <span className="message-label">AI</span>
                <p className="thinking">Thinking...</p>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <form className="input-bar" onSubmit={handleAsk}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about your PDF..."
          disabled={asking}
        />
        <button type="submit" disabled={asking || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}

export default App;
