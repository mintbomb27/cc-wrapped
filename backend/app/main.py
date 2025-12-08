from fastapi import FastAPI
from .core.database import engine
from .models import models
from .api import cards

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Credit Card Wrapped API")

app.include_router(cards.router, prefix="/api/v1", tags=["cards"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Credit Card Wrapped API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
