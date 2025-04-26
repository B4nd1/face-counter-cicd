import os
import cv2
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(cascade_path)

class DetectRequest(BaseModel):
    filename: str

class DetectResponse(BaseModel):
    annotated: str
    count: int

@app.get("/health")
def health_check():
    return {"status": "healthy"}
@app.post("/detect", response_model=DetectResponse)
def detect(req: DetectRequest):
    image_path = os.path.join("images", req.filename)
    img = cv2.imread(image_path)
    if img is None:
        raise HTTPException(status_code=404, detail="Image not found")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30,30))
    for (x,y,w,h) in faces:
        cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
    annotated = f"annotated_{req.filename}"
    save_path = os.path.join("images", annotated)
    cv2.imwrite(save_path, img)
    return {"annotated": annotated, "count": len(faces)}