import base64
import os
from fastapi import FastAPI, File, UploadFile, Form, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from models import Base, Subscriber, get_db, engine
from email_component import send_email
from sqlalchemy.orm import Session

app = FastAPI()
Base.metadata.create_all(bind=engine)

subscribed_to_options = ["all", "only-posts-from-now-on"]

@app.post("/subscribe")
async def subscribe(
    contact: str = Form(...),
    method: str = Form(...),
    body: str = Form(None),
    db: Session = Depends(get_db),
):
    subscriber = db.query(Subscriber).filter_by(contact=contact).first()
    if not subscriber:
        subscriber = Subscriber(contact=contact, method=method)
        db.add(subscriber)
        db.commit()
        db.refresh(subscriber)
    else:
        return {"status": "Already subscribed"}

    # Send welcome message if provided
    if body:
        subject = "Welcome to our notifications"
        if method == 'email':
            send_email(to_email=contact, subject=subject, body=body)
    return {"status": "Subscribe success"}

@app.post("/notify")
async def notify(
    notify: str = Form(...),
    db: Session = Depends(get_db),
):
    subscribers = db.query(Subscriber).all()

    subject = "New notification"
    for sub in subscribers:
        try:
            if sub.method == 'email':
                send_email(to_email=sub.contact, subject=subject, body=notify)
        except Exception as e:
            print(f"Failed to send to {sub.contact} via {sub.method}: {e}")
    return {"status": f"Sent notifications to {len(subscribers)} subscribers"}

# Debug
@app.get("/allsubs")
async def getall(secret: str = Form(...), db: Session = Depends(get_db)):
    if secret == 'alma':
        return db.query(Subscriber).all()
    else:
        return "Invalid secret"

