import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Képek metaadatainak a tárolása
class ImageRecord(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    # Leírás
    description = Column(Text, nullable=False)
    # Útvonal
    annotated_path = Column(String, nullable=False)
    # Észlelt arcok száma
    num_people = Column(Integer, nullable=False)
    # Feltöltés dátuma
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Feliratkozók tárolása
class Subscriber(Base):
    __tablename__ = "subscribers"
    id = Column(Integer, primary_key=True, index=True)
    # Email cím
    email = Column(String, unique=True, index=True, nullable=False)
    # Feliratkozás dátuma
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Adatbázis kapcsolat létrehozása
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()