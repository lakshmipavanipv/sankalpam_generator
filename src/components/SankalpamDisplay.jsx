import { useState, useEffect, useRef } from "react";
import { fetchSankalpamAudio } from "../services/api";

const LANGUAGES = [
  { key: "sanskrit", label: "संस्कृत",  sublabel: "Sanskrit" },
  { key: "english",  label: "English",  sublabel: "English" },
  { key: "telugu",   label: "తెలుగు",   sublabel: "Telugu" },
  { key: "tamil",    label: "தமிழ்",    sublabel: "Tamil" },
  { key: "kannada",  label: "ಕನ್ನಡ",    sublabel: "Kannada" },
  { key: "marathi",  label: "मराठी",    sublabel: "Marathi" },
  { key: "hindi",    label: "हिन्दी",    sublabel: "Hindi" },
];

// Split at the separator line to show verses + meaning separately
function splitText(text) {
  if (!text) return { verses: "", meaning: "" };
  const m = text.match(/━{5,}/);
  if (!m) return { verses: text, meaning: "" };
  return {
    verses:  text.slice(0, m.index).trim(),
    meaning: text.slice(m.index + m[0].length).trim(),
  };
}

export default function SankalpamDisplay({
  data, formData, language, onLanguageChange, onDownloadPDF, downloading,
}) {
  const [copied, setCopied] = useState(false);
  const { panchang, sankalpam, location } = data;
  const currentText = sankalpam[language] || "";
  const { verses, meaning } = splitText(currentText);

  // ── Priest voice recitation ──
  const [audio, setAudio] = useState({ status: "idle", url: null, error: "" });
  const urlRef = useRef(null);
  useEffect(() => {          // new language/result → drop the old recording
    if (urlRef.current) URL.revokeObjectURL(urlRef.current);
    urlRef.current = null;
    setAudio({ status: "idle", url: null, error: "" });
  }, [language, data]);
  useEffect(() => () => urlRef.current && URL.revokeObjectURL(urlRef.current), []);

  const handleListen = async () => {
    setAudio({ status: "loading", url: null, error: "" });
    try {
      const blob = await fetchSankalpamAudio({ ...formData, language });
      const url = URL.createObjectURL(blob);
      urlRef.current = url;
      setAudio({ status: "ready", url, error: "" });
    } catch (e) {
      setAudio({ status: "error", url: null, error: e.message || "Voice unavailable" });
    }
  };

  const handleCopy = async () => {
    try { await navigator.clipboard.writeText(currentText); }
    catch {
      const ta = document.createElement("textarea");
      ta.value = currentText;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const PItem = ({ icon, label, value }) => (
    <div className="panchang-item">
      <span className="panchang-icon">{icon}</span>
      <div>
        <div className="panchang-label">{label}</div>
        <div className="panchang-value">{value}</div>
      </div>
    </div>
  );

  return (
    <div className="result-card">

      {/* Header */}
      <div className="result-header">
        <h2 className="result-title">🎉 Sankalpam Generated!</h2>
        <p className="result-subtitle">
          {formData?.pooja_name} • {formData?.name} •{" "}
          {[formData?.city, formData?.state, formData?.country].filter(Boolean).join(", ")}
        </p>
      </div>

      {/* Panchang */}
      <div className="panchang-section">
        <h3 className="section-title">📅 Panchang Details</h3>
        <div className="panchang-grid">
          <PItem icon="🌙" label="Tithi"         value={`${panchang.tithi} (${panchang.paksha})`} />
          <PItem icon="☀️" label="Vara"          value={`${panchang.vara} / ${panchang.vara_english}`} />
          <PItem icon="⭐" label="Nakshatra"      value={panchang.nakshatra} />
          <PItem icon="🔮" label="Yoga"          value={panchang.yoga} />
          <PItem icon="🌀" label="Karana"        value={panchang.karana} />
          <PItem icon="📆" label="Masa"          value={panchang.masa} />
          <PItem icon="🍃" label="Ritu"          value={`${panchang.ritu} (${panchang.ritu_english})`} />
          <PItem icon="🌅" label="Ayana"         value={panchang.ayana} />
          <PItem icon="🗓️" label="Samvatsara"    value={panchang.samvatsara} />
          <PItem icon="📍" label="Location"      value={[formData?.city, formData?.state, formData?.country].filter(Boolean).join(", ")} />
        </div>
      </div>

      {/* Language Tabs */}
      <div className="language-section">
        <h3 className="section-title">🌐 Select Language</h3>
        <div className="language-tabs">
          {LANGUAGES.map(lang => (
            <button
              key={lang.key}
              className={`lang-tab${language === lang.key ? " active" : ""}`}
              onClick={() => onLanguageChange(lang.key)}
            >
              <span className="lang-native">{lang.label}</span>
              <span className="lang-sub">{lang.sublabel}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Sankalpam — TWO PARTS */}
      <div className="sankalpam-section">

        {/* Part 1: Sanskrit Devanagari Verses */}
        <div className="verse-label">📜 Sankalpam (सङ्कल्पः)</div>

        <div className="listen-bar">
          {audio.status === "ready" ? (
            <audio className="listen-audio" src={audio.url} controls autoPlay />
          ) : (
            <button className="action-btn listen-btn" onClick={handleListen} disabled={audio.status === "loading"}>
              {audio.status === "loading"
                ? <><span className="btn-spinner dark" /> Preparing recitation…</>
                : "🔊 Listen — Purohit voice"}
            </button>
          )}
          {audio.status === "error" && <p className="field-error">⚠ {audio.error}</p>}
        </div>
        <div className="sankalpam-box verses-box">
          <div className="sankalpam-decoration" aria-hidden="true">✿ ❈ ✿</div>
          <p className="sankalpam-text lang-sanskrit">
            {verses}
          </p>
          <div className="sankalpam-decoration" aria-hidden="true">✿ ❈ ✿</div>
        </div>

        {/* Part 2: Meaning in selected language */}
        {meaning && (
          <>
            <div className="verse-label meaning-label">
              💡 Meaning ({LANGUAGES.find(l => l.key === language)?.sublabel})
            </div>
            <div className="sankalpam-box meaning-box">
              <p className={`sankalpam-text lang-${language}`}>
                {meaning}
              </p>
            </div>
          </>
        )}

        {/* Actions */}
        <div className="action-buttons">
          <button
            className={`action-btn copy-btn${copied ? " copied" : ""}`}
            onClick={handleCopy}
          >
            {copied ? "✅ Copied!" : "📋 Copy to Clipboard"}
          </button>
          <button
            className="action-btn pdf-btn"
            onClick={onDownloadPDF}
            disabled={downloading}
          >
            {downloading
              ? <><span className="btn-spinner dark" /> Generating PDF…</>
              : "📄 Download PDF"
            }
          </button>
        </div>
      </div>

    </div>
  );
}
