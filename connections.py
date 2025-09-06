# src/piggy/connection.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///expenses.db"

engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

if __name__ == "__main__":
    from . import models  # ensure models are imported so tables are registered
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized (expenses.db)")
