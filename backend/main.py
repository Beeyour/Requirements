import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Use absolute imports for reliability
from backend.database import engine, Base
from backend import api
from backend import models
from backend.models.user import User
from backend.models.project import Project
from backend.models.conversation import ConversationHistory
from backend.models.requirement import Requirement
from backend.models.requirement_log import RequirementLog

app = FastAPI(
    title="SRS Analyst API",
    description="AI-powered software requirements engineering platform",
    version="1.3.0"
)

# Setup CORS - In production, replace "*" with your actual frontend domain

FRONTEND_URL = os.getenv("FRONTEND_URL", "*")

# Create database tables on startup (Automatic migration)
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Registering Routers ---

app.include_router(api.auth, prefix="/auth", tags=["Authentication"])
app.include_router(api.projects, prefix="/projects", tags=["Projects"])
app.include_router(api.chat, tags=["Chat"]) 
app.include_router(api.requirements, prefix="/requirements", tags=["Requirements"])
app.include_router(api.models_api, tags=["Models Info"])
app.include_router(api.uml, tags=["UML"])




@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Welcome to SRS Analyst API",
        "docs": "/docs",
        "status": "active"
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Service health check for monitoring and deployment."""
    return {"status": "healthy"}