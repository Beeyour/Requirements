import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from api import auth, projects, chat, requirements, models_api, uml # Import uml here
import models # Crucial for table creation

app = FastAPI(title="SRS Analyst API", version="1.3.0")

# Setup CORS
FRONTEND_URL = os.getenv("FRONTEND_URL", "*")

# Create database tables on startup
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registering Routers
app.include_router(auth,        prefix="/auth",     tags=["Authentication"])
app.include_router(projects,    prefix="/projects", tags=["Projects"])
app.include_router(chat,        prefix="/chat",     tags=["Chat"]) # Added prefix for clarity
app.include_router(requirements,prefix="/req",      tags=["Requirements"]) # Optional prefix
# app.include_router(uml,         prefix="/uml",      tags=["UML Generation"]) # Register UML
app.include_router(models_api,  prefix="/info",     tags=["Models Info"])

@app.get("/health", tags=["Health"])
def health_check():
    """Service health check endpoint."""
    return {"status": "healthy"}