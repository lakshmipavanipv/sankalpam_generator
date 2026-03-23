# 🕉️ Sankalpam Generator

A full-stack web application that dynamically generates Hindu Pooja Sankalpam using real Panchang (almanac) calculations. Supports Sanskrit, Telugu, Tamil, and English.

---

## 📁 Project Structure

```
sankalpam/
├── backend/                    # Python FastAPI backend
│   ├── main.py                 # API server (routes)
│   ├── panchang_service.py     # Panchang calculations
│   ├── geolocation_service.py  # City → lat/lng/timezone
│   ├── sankalpam_generator.py  # Multi-language text generation
│   ├── pdf_generator.py        # PDF creation
│   ├── requirements.txt        # Python dependencies
│   └── render.yaml             # Render.com deploy config
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── App.jsx             # Main app component
│   │   ├── App.css             # Temple-style UI styles
│   │   ├── main.jsx            # Entry point
│   │   ├── components/
│   │   │   ├── SankalpamForm.jsx     # Input form
│   │   │   ├── SankalpamDisplay.jsx  # Result display
│   │   │   └── LoadingSpinner.jsx    # Loading animation
│   │   └── services/
│   │       └── api.js          # Backend API calls
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── vercel.json             # Vercel deploy config
│
└── generate_qr.py              # QR code generator script
```

---

## 🚀 Running Locally

### Prerequisites
- Python 3.10+ installed
- Node.js 18+ installed
- Git (optional)

---

### Step 1: Set Up the Backend

```bash
# Go to the backend folder
cd sankalpam/backend

# Create a virtual environment (recommended)
python -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
python main.py
```

The backend will start at: **http://localhost:8000**

You can verify it works by opening: http://localhost:8000 in your browser.
You should see: `{"message": "Sankalpam Generator API is running 🙏"}`

---

### Step 2: Set Up the Frontend

Open a **new terminal window** (keep the backend running):

```bash
# Go to the frontend folder
cd sankalpam/frontend

# Install Node dependencies
npm install

# Copy the environment file
cp .env.example .env
# The default .env points to http://localhost:8000 — no changes needed locally

# Start the frontend
npm run dev
```

The frontend will start at: **http://localhost:3000**

Open http://localhost:3000 in your browser and you're ready! 🎉

---

## 📱 Generating a QR Code

After deploying (or for local testing):

```bash
# Install QR code library
pip install qrcode[pil]

# Generate QR for your deployed app
python generate_qr.py --url https://your-app.vercel.app

# For local testing
python generate_qr.py --url http://localhost:3000

# Custom output filename
python generate_qr.py --url https://your-app.vercel.app --output temple_qr.png
```

This creates a `sankalpam_qr.png` file you can print and place at your pooja venue!

---

## ☁️ Deploying to Production

### Backend → Deploy on Render.com (Free)

1. Create a free account at [render.com](https://render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo (push the `backend/` folder)
4. Configure:
   - **Name**: `sankalpam-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Click **"Create Web Service"**
6. Wait ~3 minutes for deployment
7. Copy your URL: `https://sankalpam-backend.onrender.com`

> ⚠️ Free Render instances sleep after 15 min of inactivity. First request may take ~30 seconds to wake up.

---

### Frontend → Deploy on Vercel (Free)

1. Create a free account at [vercel.com](https://vercel.com)
2. Click **"New Project"** → Import your GitHub repo
3. Set **Root Directory** to `frontend`
4. Add **Environment Variable**:
   - Key: `VITE_API_URL`
   - Value: `https://sankalpam-backend.onrender.com` (your Render URL)
5. Click **"Deploy"**
6. Your app will be live at: `https://sankalpam-yourname.vercel.app`

---

### Updating CORS for Production

In `backend/main.py`, update the CORS origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",   # Your Vercel URL
        "http://localhost:3000",          # Keep for local dev
    ],
    ...
)
```

---

## 🛠️ API Reference

### `POST /generate-sankalpam`

Generate Sankalpam from form data.

**Request body (JSON):**
```json
{
  "date": "2024-01-15",
  "time": "10:30",
  "pooja_name": "Satyanarayana Puja",
  "sankalpam_type": "Kamya Pooja",
  "gothram": "Kashyapa",
  "name": "Rama Rao",
  "dharma_patni_name": "Sita",
  "family_name": "Sharma",
  "country": "India",
  "city": "Hyderabad",
  "calendar_type": "Telugu"
}
```

**Response:**
```json
{
  "success": true,
  "panchang": {
    "tithi": "Panchami",
    "vara": "Guruvara",
    "nakshatra": "Rohini",
    "yoga": "Siddhi",
    "karana": "Bava",
    "masa": "Pushya",
    "paksha": "Shukla Paksha",
    "ritu": "Shishira",
    "ayana": "Uttarayana",
    "samvatsara": "Vilambi"
  },
  "location": {
    "latitude": 17.385,
    "longitude": 78.4867,
    "timezone": "Asia/Kolkata",
    "city": "Hyderabad",
    "country": "India"
  },
  "sankalpam": {
    "sanskrit": "ॐ विष्णुर्विष्णुर्विष्णुः...",
    "telugu": "ఓం శ్రీ మహా గణపతయే నమః...",
    "tamil": "ஓம் ஸ்ரீ மஹா கணபதயே நமஹ...",
    "english": "Om. By the command of Lord Vishnu..."
  }
}
```

### `POST /download-pdf`

Same body as above, plus:
```json
{ "language": "telugu" }
```

Returns a PDF file download.

---

## 🔧 Troubleshooting

| Problem | Solution |
|---|---|
| `City not found` error | Check spelling; try nearby major city |
| Backend won't start | Run `pip install -r requirements.txt` again |
| Frontend won't connect | Make sure backend is running on port 8000 |
| PDF fonts look wrong | Install `fonts-noto` on Linux: `sudo apt install fonts-noto` |
| Render backend is slow | Free tier sleeps — first request takes ~30s |

---

## 🙏 Credits

- Panchang calculations based on Jean Meeus' *Astronomical Algorithms*
- Geocoding by [OpenStreetMap Nominatim](https://nominatim.org/) (free, no API key)
- Fonts: [Google Noto Fonts](https://fonts.google.com/noto) (supports all Indian scripts)

---

*|| Shubham Bhavatu || May all be auspicious ||*
