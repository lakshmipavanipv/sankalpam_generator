/**
 * api.js
 * ──────
 * All API calls to the FastAPI backend.
 * BASE_URL reads from environment variable (set in .env file).
 */

// In development: http://localhost:8000
// In production: set VITE_API_URL in your .env file
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Generate Sankalpam from form data.
 * Returns: { panchang, location, sankalpam }
 */
export async function generateSankalpam(formData) {
  const response = await fetch(`${BASE_URL}/generate-sankalpam`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formData),
  });

  if (!response.ok) {
    let errorMsg = `Server error (${response.status})`;
    try {
      const err = await response.json();
      errorMsg = err.detail || errorMsg;
    } catch {}
    throw new Error(errorMsg);
  }

  return response.json();
}

/**
 * Download Sankalpam as PDF.
 * Triggers browser file download.
 */
export async function downloadPDF(formData) {
  const response = await fetch(`${BASE_URL}/download-pdf`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formData),
  });

  if (!response.ok) {
    let errorMsg = `PDF generation failed (${response.status})`;
    try {
      const err = await response.json();
      errorMsg = err.detail || errorMsg;
    } catch {}
    throw new Error(errorMsg);
  }

  // Trigger file download
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `sankalpam_${formData.name}_${formData.date}.pdf`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}

/** GPS coordinates -> { city, state, country, timezone, source } */
export async function reverseGeocode(lat, lon) {
  const r = await fetch(`${BASE_URL}/reverse-geocode?lat=${lat}&lon=${lon}`);
  if (!r.ok) throw new Error(`Location lookup failed (${r.status})`);
  return r.json();
}

/** Panchang only, for the live strip (computed offline on the backend). */
export async function fetchPanchang({ date, time, latitude, longitude, calendar_type }) {
  const q = new URLSearchParams({ date, time, lat: latitude, lon: longitude, calendar_type });
  const r = await fetch(`${BASE_URL}/panchang?${q}`);
  if (!r.ok) throw new Error(`Panchang failed (${r.status})`);
  return r.json();
}
