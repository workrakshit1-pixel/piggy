# init_db.py
from src.Db import Base, engine
from src import models  # imports all models so they are registered

print("📦 Creating tables...")
Base.metadata.create_all(bind=engine)
print("✅ Done! Database ready.")
