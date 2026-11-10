from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database import Base, engine
from app import models
from app.routers import auth, admin, documents, public

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.auto_create_tables:
        Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title=settings.app_name, version="2.0.0",
              description="Nangarhar University Digital Library API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list,
                   allow_credentials=settings.cors_origin_list != ["*"],
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(documents.router)
app.include_router(public.router)

@app.get("/")
def root():
    return {"message": "NUDL API is running", "docs": "/docs", "health": "/health"}

@app.get("/health")
def health():
    return {"status": "ok", "environment": settings.environment}
