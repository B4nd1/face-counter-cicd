import os
from fastapi import FastAPI, File, UploadFile, Form, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from models import Base, ImageRecord, Subscriber, get_db, engine
import httpx
# from detect import detect_and_annotate

# Init database tables
Base.metadata.create_all(bind=engine)

detector_url = os.getenv("DETECTOR_URL", "http://detector:8001/detect")

app = FastAPI()

app.mount("/images", StaticFiles(directory="images"), name="images")

templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    images = db.query(ImageRecord).order_by(ImageRecord.created_at.desc()).all()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "images": images}
    )

@app.post("/upload")
async def upload(request: Request, file: UploadFile = File(...),
                 description: str = Form(...), db: Session = Depends(get_db)):
    file_location = f"images/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # Fájlon lefuttatja az arc detektálást
    # Helyi
    # annotated_fname, count = detect_and_annotate(file_location)
    # Külön instance API-jának használata
    async with httpx.AsyncClient() as client:
        resp = await client.post(detector_url, json={"filename": file.filename,
                                                     "image": file.file})
        data = resp.json()

    # Válaszból megkapja az információkat
    annotated_fname = data["annotated"]
    count = data["count"]

    # Kép rögzítése az adatbázisban a modell alapján
    record = ImageRecord(
        filename=file.filename,
        description=description,
        annotated_path=annotated_fname,
        num_people=count
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    # Fix: A "Képernyő újraküldésének megerősítése" bug feltöltés után
    return RedirectResponse(url='/', status_code=303)