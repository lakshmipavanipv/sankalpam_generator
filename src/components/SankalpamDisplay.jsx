import { useState } from "react";

const LANGUAGES = [
  { key: "sanskrit", label: "संस्कृत",  sublabel: "Sanskrit" },
  { key: "english",  label: "English",  sublabel: "Meaning" },
  { key: "telugu",   label: "తెలుగు",   sublabel: "Telugu" },
  { key: "tamil",    label: "தமிழ்",    sublabel: "Tamil" },
  { key: "kannada",  label: "ಕನ್ನಡ",    sublabel: "Kannada" },
  { key: "marathi",  label: "मराठी",    sublabel: "Marathi" },
  { key: "hindi",    label: "हिन्दी",    sublabel: "Hindi" },
];

// Split at the separator line to show verses + meaning separately
function splitText(text) {
  if (!text) return { verses: "", meaning: "" };
  const SEP = "─────────────────────────────────────";
  const idx = text.indexOf(SEP);
  if (idx === -1) return { verses: text, meaning: "" };
  return {
    verses:  text.slice(0, idx).trim(),
    meaning: text.slice(idx + SEP.length).trim(),
  };
}

export default function SankalpamDisplay({
  data, formData, language, onLanguageChange, onDownloadPDF, downloading,
}) {
  const [copied, setCopied] = useState(false);
  const { panchang, sankalpam, location } = data;
  const currentText = sankalpam[language] || "";
  const { verses, meaning } = splitText(currentText);

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
        <div className="verse-label">📜 Sanskrit Verses (संस्कृत श्लोकाः)</div>
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
              💡 {LANGUAGES.find(l => l.key === language)?.sublabel} Meaning / అర్థం / பொருள்
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
