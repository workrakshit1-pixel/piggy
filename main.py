# src/main.py
from fastapi import FastAPI
from src import models
from src.Db import engine
from src.api import router

# Create DB tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Piggy 🐷 Expense Tracker")

# Include API routes
app.include_router(router)

@app.get("/")
def root():
    return {"message": "Welcome to Piggy 🐷! Ask me about your expenses."}
