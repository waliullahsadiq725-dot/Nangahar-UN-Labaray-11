from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Document, Category
from app.schemas import UserResponse, DocumentResponse, CategoryCreate, CategoryResponse
from app.dependencies import require_admin, require_super_admin

router = APIRouter(prefix="/api/admin", tags=["Administration"])

@router.get("/users/pending", response_model=list[UserResponse])
def pending_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(User).filter(User.is_approved.is_(False)).order_by(User.created_at.desc()).all()

@router.patch("/users/{user_id}/approve", response_model=UserResponse)
def approve_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    user = db.get(User, user_id)
    if not user: raise HTTPException(404, "User not found")
    user.is_approved = True; user.is_active = True
    db.commit(); db.refresh(user)
    return user

@router.patch("/users/{user_id}/disable", response_model=UserResponse)
def disable_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    user = db.get(User, user_id)
    if not user: raise HTTPException(404, "User not found")
    if user.role == "super_admin": raise HTTPException(400, "Cannot disable super admin")
    user.is_active = False; db.commit(); db.refresh(user)
    return user

@router.get("/documents/pending", response_model=list[DocumentResponse])
def pending_documents(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(Document).filter(Document.status == "pending").order_by(Document.created_at.desc()).all()

@router.patch("/documents/{document_id}/approve", response_model=DocumentResponse)
def approve_document(document_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    doc = db.get(Document, document_id)
    if not doc: raise HTTPException(404, "Document not found")
    doc.status = "approved"; db.commit(); db.refresh(doc)
    return doc

@router.patch("/documents/{document_id}/reject", response_model=DocumentResponse)
def reject_document(document_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    doc = db.get(Document, document_id)
    if not doc: raise HTTPException(404, "Document not found")
    doc.status = "rejected"; db.commit(); db.refresh(doc)
    return doc

@router.post("/categories", response_model=CategoryResponse, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    name = data.name.strip()
    if db.query(Category).filter(Category.name == name).first():
        raise HTTPException(409, "Category already exists")
    item = Category(name=name, description=data.description)
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(User).order_by(User.created_at.desc()).limit(500).all()

@router.post("/admins/{user_id}", response_model=UserResponse)
def promote_admin(user_id: int, db: Session = Depends(get_db), _: User = Depends(require_super_admin)):
    user = db.get(User, user_id)
    if not user: raise HTTPException(404, "User not found")
    user.role = "admin"; user.is_active = True; user.is_approved = True
    db.commit(); db.refresh(user)
    return user

@router.get("/stats")
def stats(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return {"users_total": db.query(User).count(),
            "students": db.query(User).filter(User.role == "student").count(),
            "teachers": db.query(User).filter(User.role == "teacher").count(),
            "documents_total": db.query(Document).count(),
            "documents_approved": db.query(Document).filter(Document.status == "approved").count(),
            "documents_pending": db.query(Document).filter(Document.status == "pending").count()}
