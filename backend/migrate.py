from app.database import Base, engine
from app import models  # WAJIB: agar semua model terbaca oleh metadata

print("🔄 Migrating database...")
Base.metadata.create_all(bind=engine)
print("✅ Migration completed.")
