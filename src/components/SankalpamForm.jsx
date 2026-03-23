import { useState } from "react";

const today       = new Date().toISOString().split("T")[0];
const currentTime = new Date().toTimeString().slice(0, 5);

const POOJA_NAMES = [
  "Ganesh Puja", "Lakshmi Puja", "Satyanarayana Puja", "Navagraha Puja",
  "Rudrabhishekam", "Ayushya Homa", "Grihapravesham", "Vivah (Wedding)",
  "Upanayanam", "Namakaranam", "Annaprasana", "Seemantham",
  "Vastu Puja", "Durga Puja", "Karthika Deepam", "Other"
];

const SANKALPAM_TYPES = [
  "", "Nithya Pooja (Daily worship)", "Kamya Pooja (Special occasion)",
  "Vrata (Vow/Fasting)", "Homa/Yajna (Fire ritual)",
  "Shraddha (Ancestral rites)", "Thiruvanandal (Temple ritual)"
];

const CALENDAR_TYPES = ["Telugu", "Tamil", "Kannada", "Marathi"];

const INIT = {
  date: today, time: currentTime,
  pooja_name: "Satyanarayana Puja", pooja_name_custom: "",
  sankalpam_type: "", gothram: "", name: "",
  dharma_patni_name: "", family_name: "", other_members: "",
  country: "Canada", state: "", city: "",
  calendar_type: "Telugu", desires: "",
};

export default function SankalpamForm({ onSubmit, loading }) {
  const [form, setForm]     = useState(INIT);
  const [errors, setErrors] = useState({});

  const set = (e) => {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
    setErrors(e2 => ({ ...e2, [name]: undefined }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const errs = {};
    if (!form.name.trim())    errs.name    = "Name is required";
    if (!form.gothram.trim()) errs.gothram = "Gothram is required";
    if (!form.city.trim())    errs.city    = "City is required";
    if (!form.country.trim()) errs.country = "Country is required";
    const poojaFinal = form.pooja_name === "Other" ? form.pooja_name_custom.trim() : form.pooja_name;
    if (!poojaFinal)          errs.pooja_name = "Pooja name is required";
    if (Object.keys(errs).length) { setErrors(errs); return; }
    onSubmit({ ...form, pooja_name: poojaFinal });
  };

  const inp = (name, placeholder, type = "text") => (
    <input
      id={name} name={name} type={type}
      value={form[name]} onChange={set}
      placeholder={placeholder}
      className={`form-input${errors[name] ? " input-error" : ""}`}
      disabled={loading} autoComplete="off"
    />
  );

  const err = (name) => errors[name]
    ? <p className="field-error">⚠ {errors[name]}</p> : null;

  const lbl = (name, text, required) => (
    <label htmlFor={name} className="form-label">
      {text}{required && <span className="required"> *</span>}
    </label>
  );

  return (
    <div className="form-card">
      <div className="form-card-header">
        <h2 className="form-card-title">🙏 Enter Pooja Details</h2>
        <p className="form-card-subtitle">Fill in your details to generate a personalized Sankalpam</p>
      </div>

      <form onSubmit={handleSubmit} className="sankalpam-form" noValidate>

        {/* ── Date & Time ── */}
        <div className="form-row">
          <div className="form-field">
            {lbl("date","Date",true)}
            {inp("date","","date")}
          </div>
          <div className="form-field">
            {lbl("time","Time",true)}
            {inp("time","","time")}
          </div>
        </div>

        {/* ── Pooja Name ── */}
        <div className="form-field">
          {lbl("pooja_name","Pooja Name",true)}
          <select id="pooja_name" name="pooja_name" value={form.pooja_name}
            onChange={set} className="form-input form-select" disabled={loading}>
            {POOJA_NAMES.map(p => <option key={p} value={p}>{p}</option>)}
          </select>
        </div>

        {/* Custom pooja when "Other" selected */}
        {form.pooja_name === "Other" && (
          <div className="form-field">
            {lbl("pooja_name_custom","Specify Pooja Name",true)}
            <input
              id="pooja_name_custom" name="pooja_name_custom" type="text"
              value={form.pooja_name_custom} onChange={set}
              placeholder="e.g. Sudarshana Homa, Chandi Homa…"
              className={`form-input${errors.pooja_name ? " input-error" : ""}`}
              disabled={loading} autoComplete="off"
            />
            {err("pooja_name")}
          </div>
        )}

        {/* ── Sankalpam Type ── */}
        <div className="form-field">
          {lbl("sankalpam_type","Sankalpam Type")}
          <select id="sankalpam_type" name="sankalpam_type" value={form.sankalpam_type}
            onChange={set} className="form-input form-select" disabled={loading}>
            {SANKALPAM_TYPES.map(s => (
              <option key={s} value={s}>{s || "— Select type (optional) —"}</option>
            ))}
          </select>
          <p className="field-hint">Optional</p>
        </div>

        <div className="section-divider"><span>Devotee Information</span></div>

        {/* ── Name & Gothram ── */}
        <div className="form-row">
          <div className="form-field">
            {lbl("name","Your Name",true)}
            {inp("name","e.g. Rama Rao")}
            {err("name")}
          </div>
          <div className="form-field">
            {lbl("gothram","Gothram",true)}
            {inp("gothram","e.g. Kashyapa, Bharadwaja")}
            {err("gothram")}
          </div>
        </div>

        {/* ── Wife & Family ── */}
        <div className="form-row">
          <div className="form-field">
            {lbl("dharma_patni_name","Dharma Patni (Wife) Name")}
            {inp("dharma_patni_name","e.g. Sita Devi")}
            <p className="field-hint">Optional</p>
          </div>
          <div className="form-field">
            {lbl("family_name","Family / Kulam Name")}
            {inp("family_name","e.g. Sharma")}
            <p className="field-hint">Optional</p>
          </div>
        </div>

        {/* ── Other Family Members ── */}
        <div className="form-field">
          {lbl("other_members","Other Family Members")}
          <input
            id="other_members" name="other_members" type="text"
            value={form.other_members} onChange={set}
            placeholder="e.g. Ravi, Priya, Arjun, Meena (separate names with commas)"
            className="form-input" disabled={loading} autoComplete="off"
          />
          <p className="field-hint">Optional — names of children, parents, siblings to include in Sankalpam</p>
        </div>

        <div className="section-divider"><span>Location &amp; Calendar</span></div>

        {/* ── Country & State ── */}
        <div className="form-row">
          <div className="form-field">
            {lbl("country","Country",true)}
            {inp("country","e.g. Canada, India, USA")}
            {err("country")}
          </div>
          <div className="form-field">
            {lbl("state","State / Province")}
            {inp("state","e.g. British Columbia")}
            <p className="field-hint">Optional</p>
          </div>
        </div>

        {/* ── City ── */}
        <div className="form-field">
          {lbl("city","City",true)}
          {inp("city","e.g. White Rock, Hyderabad, Toronto")}
          {err("city")}
        </div>

        {/* ── Calendar Type ── */}
        <div className="form-field">
          <label className="form-label">Calendar Type</label>
          <div className="calendar-options">
            {CALENDAR_TYPES.map(cal => (
              <label key={cal} className={`calendar-option${form.calendar_type === cal ? " selected" : ""}`}>
                <input type="radio" name="calendar_type" value={cal}
                  checked={form.calendar_type === cal} onChange={set} disabled={loading} />
                {cal}
              </label>
            ))}
          </div>
        </div>

        <div className="section-divider"><span>Personal Desires (Sankalpa)</span></div>

        {/* ── Desires ── */}
        <div className="form-field">
          {lbl("desires","Your Personal Wishes / Sankalpa")}
          <textarea
            id="desires" name="desires" value={form.desires} onChange={set}
            placeholder={"Write your personal wishes here…\ne.g. Puthra Santhanam, good health, career success, family happiness, spiritual progress…"}
            className="form-input form-textarea" disabled={loading} rows={4}
          />
          <p className="field-hint">
            💡 Personal desires are contemplated silently in tradition (manasi dhyatavyah). They will appear as a private note in your Sankalpam.
          </p>
        </div>

        <button type="submit" className="submit-btn" disabled={loading}>
          {loading
            ? <><span className="btn-spinner" /> Generating Sankalpam…</>
            : <>🕉️ Generate Sankalpam</>}
        </button>

      </form>
    </div>
  );
}
