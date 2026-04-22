<<<<<<< HEAD
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
# Note: In production, using Alembic is recommended over this line.
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Registering Routers ---

# Auth: Endpoints like /auth/login, /auth/register
app.include_router(api.auth, prefix="/auth", tags=["Authentication"])

# Projects: Endpoints like /projects/, /projects/{id}
app.include_router(api.projects, prefix="/projects", tags=["Projects"])

# Chat: Fixed prefixing to avoid "/chat/chat" redundancy.
# The router already defines paths starting with /chat
app.include_router(api.chat, tags=["Chat"]) 

# Requirements: Endpoints like /req/generate-srs
app.include_router(api.requirements, prefix="/req", tags=["Requirements"])

# Info: Endpoints like /info/models
app.include_router(api.models_api, tags=["Models Info"])

# UML: Uncomment when your uml_router is ready
# app.include_router(api.uml, prefix="/uml", tags=["UML Generation"])

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
=======
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from api import auth, projects, chat, requirements, models_api
import models  # noqa: F401 – registers all ORM classes before create_all

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SRS Analyst API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # هذا التغيير الجوهري: يسمح بالدخول من أي IP
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
>>>>>>> 5b97499 (chore: apply .gitignore and remove cached files)
