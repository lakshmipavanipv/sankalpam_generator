"""
Sankalpam Generator - FastAPI Backend (v2)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import logging

from panchang_service import PanchangService
from geolocation_service import GeolocationService
from sankalpam_generator import SankalpamGenerator
from pdf_generator import PDFGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sankalpam Generator API",
    description="Dynamically generate Hindu Pooja Sankalpam",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

panchang_service = PanchangService()
geo_service      = GeolocationService()
sankalpam_gen    = SankalpamGenerator()
pdf_gen          = PDFGenerator()


class SankalpamRequest(BaseModel):
    date: str
    time: str
    pooja_name: str
    sankalpam_type: Optional[str] = ""
    gothram: str
    name: str
    dharma_patni_name: Optional[str] = ""
    family_name: Optional[str] = ""
    other_members: Optional[str] = ""   # comma-separated, e.g. "Ravi, Priya, Arjun"
    country: str
    state: Optional[str] = ""          # NEW: state/province for location string
    city: str
    calendar_type: str = "Telugu"
    desires: Optional[str] = ""        # NEW: free-text personal wishes


class PDFRequest(SankalpamRequest):
    language: str = "english"


@app.get("/")
def root():
    return {"message": "Sankalpam Generator API v2 running 🙏"}


@app.post("/generate-sankalpam")
async def generate_sankalpam(req: SankalpamRequest):
    try:
        logger.info(f"Generating Sankalpam for {req.name} in {req.city}, {req.country}")

        location = geo_service.get_location(req.city, req.country)
        if not location:
            raise HTTPException(
                status_code=400,
                detail=f"Could not find location for '{req.city}, {req.country}'. Please check the spelling."
            )

        panchang = panchang_service.calculate(
            date_str=req.date,
            time_str=req.time,
            latitude=location["latitude"],
            longitude=location["longitude"],
            timezone=location["timezone"],
            calendar_type=req.calendar_type
        )

        # Inject state into form_data for location string building
        form_data = req.dict()
        form_data["state"] = req.state or ""

        sankalpam_texts = sankalpam_gen.generate_all_languages(
            panchang=panchang,
            form_data=form_data,
            location=location
        )

        return {
            "success": True,
            "panchang": panchang,
            "location": location,
            "sankalpam": sankalpam_texts
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/download-pdf")
async def download_pdf(req: PDFRequest):
    try:
        location = geo_service.get_location(req.city, req.country)
        if not location:
            raise HTTPException(status_code=400, detail="Location not found")

        panchang = panchang_service.calculate(
            date_str=req.date,
            time_str=req.time,
            latitude=location["latitude"],
            longitude=location["longitude"],
            timezone=location["timezone"],
            calendar_type=req.calendar_type
        )

        form_data = req.dict()
        form_data["state"] = req.state or ""

        sankalpam_texts = sankalpam_gen.generate_all_languages(
            panchang=panchang,
            form_data=form_data,
            location=location
        )

        pdf_path = pdf_gen.create_pdf(
            sankalpam_text=sankalpam_texts.get(req.language, sankalpam_texts["english"]),
            form_data=form_data,
            panchang=panchang,
            language=req.language
        )

        safe_name = req.name.replace(" ", "_")
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=f"sankalpam_{safe_name}_{req.date}.pdf",
            headers={"Content-Disposition": f"attachment; filename=sankalpam_{safe_name}_{req.date}.pdf"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
