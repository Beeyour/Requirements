import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from api import auth, projects, chat, requirements, models_api
import models

app = FastAPI(title="SRS Analyst API", version="1.2.0")
FRONTEND_URL = os.getenv("FRONTEND_URL", "*")
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth,        prefix="/auth",     tags=["Authentication"])
app.include_router(projects,    prefix="/projects", tags=["Projects"])
app.include_router(chat,                            tags=["Chat"])
app.include_router(requirements,                    tags=["Requirements"])
app.include_router(models_api,                      tags=["Models"])

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}