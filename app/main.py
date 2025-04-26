import os
from fastapi import FastAPI, File, UploadFile, Form, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from models import Base, ImageRecord, Subscriber, get_db, engine
from detect import detect_and_annotate

# Init database tables
Base.metadata.create_all(bind=engine)

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

    # Run detection and annotation
    annotated_fname, count = detect_and_annotate(file_location)

    # Store record in db
    record = ImageRecord(
        filename=file.filename,
        description=description,
        annotated_path=annotated_fname,
        num_people=count
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return RedirectResponse(url='/', status_code=303)