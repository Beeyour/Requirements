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
