import { useState, useRef } from "react";
import SankalpamForm from "./components/SankalpamForm";
import SankalpamDisplay from "./components/SankalpamDisplay";
import LoadingSpinner from "./components/LoadingSpinner";
import { generateSankalpam, downloadPDF } from "./services/api";
import "./App.css";

export default function App() {
  const [sankalpamData, setSankalpamData] = useState(null);
  const [formData,      setFormData]      = useState(null);
  const [language,      setLanguage]      = useState("english");
  const [loading,       setLoading]       = useState(false);
  const [error,         setError]         = useState(null);
  const [downloading,   setDownloading]   = useState(false);
  const resultRef = useRef(null);

  const handleSubmit = async (data) => {
    setLoading(true);
    setError(null);
    setSankalpamData(null);
    setFormData(data);
    try {
      const result = await generateSankalpam(data);
      setSankalpamData(result);
      setTimeout(() => resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 300);
    } catch (err) {
      setError(err.message || "Failed to generate Sankalpam. Please check your inputs.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!formData || !sankalpamData) return;
    setDownloading(true);
    try {
      await downloadPDF({ ...formData, language });
    } catch (err) {
      setError("PDF download failed: " + err.message);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="app">
      <div className="bg-pattern" aria-hidden="true" />

      <header className="app-header">
        <div className="header-inner">
          <div className="om-symbol">ॐ</div>
          <div className="header-text">
            <h1 className="app-title">Sankalpam Generator</h1>
            <p className="app-brand">by <a href="https://velvue.in" target="_blank" rel="noopener noreferrer">Velvue</a></p>
            <p className="app-subtitle">Sri Vedic Pooja Sankalpam • Generate Your Sacred Vow</p>
          </div>
          <div className="om-symbol om-right">🪔</div>
        </div>
        <div className="header-divider" />
      </header>

      <main className="app-main">
        <section className="form-section">
          <SankalpamForm onSubmit={handleSubmit} loading={loading} />
        </section>

        {loading && (
          <div className="loading-section">
            <LoadingSpinner />
            <p className="loading-text">Calculating Panchang and generating your Sankalpam…</p>
          </div>
        )}

        {error && (
          <div className="error-box">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
            <button className="error-dismiss" onClick={() => setError(null)}>✕</button>
          </div>
        )}

        {sankalpamData && !loading && (
          <section className="result-section" ref={resultRef}>
            <SankalpamDisplay
              data={sankalpamData}
              formData={formData}
              language={language}
              onLanguageChange={setLanguage}
              onDownloadPDF={handleDownloadPDF}
              downloading={downloading}
            />
          </section>
        )}
      </main>

      <footer className="app-footer">
        <p>🙏 <em>Shubham Bhavatu</em> — May all be auspicious</p>
        <p className="footer-small">Sankalpam Generator by Velvue • Panchang-based • Multi-language</p>
      </footer>
    </div>
  );
}
