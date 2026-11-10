from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Category, Document
from app.schemas import CategoryResponse

router = APIRouter(prefix="/api", tags=["Public"])

@router.get("/categories", response_model=list[CategoryResponse])
def categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.name).all()

@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    return {"approved_documents": db.query(Document).filter(Document.status == "approved").count(),
            "categories": db.query(Category).count()}
