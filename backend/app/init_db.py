# backend/app/init_db.py
from app.database import engine
from app.models import Base

def init():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully.")

if __name__ == "__main__":
    init()
