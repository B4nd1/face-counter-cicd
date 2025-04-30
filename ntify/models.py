import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func

DATABASE_URL = os.getenv("NTFY_DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Feliratkozók tárolása
class Subscriber(Base):
    __tablename__ = "subscribers"
    id = Column(Integer, primary_key=True, index=True)
    # Email cím
    contact = Column(String, unique=True, index=True, nullable=False)
    method = Column(String, nullable=False)
    # subscribed_to = Column(String,)
    # Feliratkozás dátuma
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Adatbázis kapcsolat létrehozása
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()