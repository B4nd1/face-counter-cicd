import base64
import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI()

cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(cascade_path)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image")

    # Arc számlálás
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30,30))
    for (x,y,w,h) in faces:
        cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)

    _, encoded_img = cv2.imencode('.jpg', img)
    base64_image = base64.b64encode(encoded_img).decode('utf-8')

    return {
        "faces_detected": len(faces),
        "annotated_image_base64": base64_image
    }