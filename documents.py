import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.core.config import settings
from app.models import User, Document, Category, Favorite
from app.schemas import DocumentResponse
from app.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/api/documents", tags=["Digital Library"])
UPLOAD_ROOT = Path(settings.upload_dir).resolve()
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

@router.get("", response_model=list[DocumentResponse])
def list_documents(search: str | None = Query(None, max_length=120), department: str | None = None,
                   category_id: int | None = None, skip: int = 0,
                   limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    q = db.query(Document).filter(Document.status == "approved")
    if search:
        term = f"%{search.strip()}%"
        q = q.filter(or_(Document.title.ilike(term), Document.description.ilike(term),
                         Document.course_name.ilike(term)))
    if department: q = q.filter(Document.department == department)
    if category_id: q = q.filter(Document.category_id == category_id)
    return q.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()

@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(title: str = Form(...), description: str | None = Form(None),
                          department: str | None = Form(None), course_name: str | None = Form(None),
                          academic_year: str | None = Form(None), category_id: int | None = Form(None),
                          file: UploadFile = File(...), db: Session = Depends(get_db),
                          user: User = Depends(require_roles("student", "teacher", "admin", "super_admin"))):
    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(400, "Only PDF files are allowed")
    data = await file.read(settings.max_upload_size_mb * 1024 * 1024 + 1)
    if not data: raise HTTPException(400, "File is empty")
    if len(data) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(413, f"Maximum file size is {settings.max_upload_size_mb} MB")
    if not data.startswith(b"%PDF-"): raise HTTPException(400, "Invalid PDF file")
    if category_id is not None and not db.get(Category, category_id):
        raise HTTPException(404, "Category not found")
    stored = f"{uuid.uuid4().hex}.pdf"
    target = UPLOAD_ROOT / stored
    target.write_bytes(data)
    doc = Document(title=title.strip(), description=description,
                   original_filename=Path(file.filename).name[:255], stored_filename=stored,
                   file_path=str(target), file_size=len(data), department=department,
                   course_name=course_name, academic_year=academic_year,
                   status="pending", uploader_id=user.id, category_id=category_id)
    db.add(doc); db.commit(); db.refresh(doc)
    return doc

@router.get("/{document_id}", response_model=DocumentResponse)
def document_detail(document_id: int, db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if not doc or doc.status != "approved": raise HTTPException(404, "Document not found")
    doc.view_count += 1; db.commit(); db.refresh(doc)
    return doc

@router.get("/{document_id}/download")
def download_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if not doc or doc.status != "approved": raise HTTPException(404, "Document not found")
    path = Path(doc.file_path).resolve()
    if not path.is_file() or UPLOAD_ROOT not in path.parents:
        raise HTTPException(404, "PDF file is not available")
    doc.download_count += 1; db.commit()
    return FileResponse(path, media_type="application/pdf", filename=doc.original_filename)

@router.get("/mine/uploads", response_model=list[DocumentResponse])
def my_uploads(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Document).filter(Document.uploader_id == user.id).order_by(Document.created_at.desc()).all()

@router.post("/{document_id}/favorite")
def add_favorite(document_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    doc = db.get(Document, document_id)
    if not doc or doc.status != "approved": raise HTTPException(404, "Document not found")
    fav = db.query(Favorite).filter_by(user_id=user.id, document_id=document_id).first()
    if not fav: db.add(Favorite(user_id=user.id, document_id=document_id)); db.commit()
    return {"message": "Added to favorites"}

@router.delete("/{document_id}/favorite")
def remove_favorite(document_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    fav = db.query(Favorite).filter_by(user_id=user.id, document_id=document_id).first()
    if fav: db.delete(fav); db.commit()
    return {"message": "Removed from favorites"}

@router.get("/favorites/list", response_model=list[DocumentResponse])
def favorites(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Document).join(Favorite, Favorite.document_id == Document.id).filter(
        Favorite.user_id == user.id, Document.status == "approved").all()
