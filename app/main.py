import os
from fastapi import FastAPI, File, UploadFile, Form, Depends, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from models import Base, ImageRecord, get_db, engine
import httpx
import base64

# Init database tables
Base.metadata.create_all(bind=engine)

detector_url = os.getenv("DETECTOR_URL", "http://detector:8001/detect")
NTIFY_URL = os.getenv("NTIFY_URL")

IMAGES_LOC = "images"

app = FastAPI()

app.mount(f"/{IMAGES_LOC}", StaticFiles(directory=IMAGES_LOC), name=IMAGES_LOC)

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
    file_location = f"{IMAGES_LOC}/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # Fájlon lefuttatja az arc detektálást
    # Helyi
    # annotated_fname, count = detect_and_annotate(file_location)
    # Külön instance API-jának használata
    async with httpx.AsyncClient() as client:
        resp = await client.post(detector_url, files={"file": (file.filename, file.file, file.content_type)})
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Detection failed")
        data = resp.json()

    # Válaszból megkapja az arcok számát és a módosított képet
    annotated_path = f"annotated_{file.filename}"
    annotated_base64 = data["annotated_image_base64"]
    annotated_bytes = base64.b64decode(annotated_base64)
    with open(f"{IMAGES_LOC}/{annotated_path}", "wb") as f:
        f.write(annotated_bytes)

    count = data["faces_detected"]
    # Kép rögzítése az adatbázisban a modell alapján
    record = ImageRecord(
        filename=file.filename,
        description=description,
        annotated_path=annotated_path,
        num_people=count
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    await notify(record)

    # Fix: A "Képernyő újraküldésének megerősítése" bug feltöltés után
    return RedirectResponse(url='/', status_code=303)

@app.post("/subscribe")
async def subscribe(request: Request, contact: str = Form(...), method: str = Form(...), db: Session = Depends(get_db)):
    # Összes eddigi poszt
    all_posts = db.query(ImageRecord).order_by(ImageRecord.created_at).all()
    body = "Welcome! Here are all the posts so far:\n\n"
    if all_posts:
        for post in all_posts:
            body += f"Fájlnév: {post.filename}\n Leírás: {post.description}\n Észlelt arcok száma: {post.num_people}\n Feltöltés Dátuma: {post.created_at}\n###########\n"
    else:
        body = "Welcome! There are no posts yet."

    async with httpx.AsyncClient() as client:
        resp = await client.post(f'{NTIFY_URL}/subscribe', data={"method": method, "contact": contact, "body": body})
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Subscription failed")

    return RedirectResponse(url="/", status_code=303)


async def notify(post):
    poststr = f"New post\n\n Fájlnév: {post.filename}\n Leírás: {post.description}\n Észlelt arcok száma: {post.num_people}\n Feltöltés Dátuma: {post.created_at}"
    async with httpx.AsyncClient() as client:
        resp = await client.post(f'{NTIFY_URL}/notify', data={"notify": poststr})
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Notify failed")
