# test_connection.py
from app.database import SessionLocal

try:
    db = SessionLocal()
    db.execute("SELECT 1")
    print("✅ Koneksi ke RDS berhasil.")
except Exception as e:
    print("❌ Gagal koneksi ke RDS:", str(e))
finally:
    db.close()
