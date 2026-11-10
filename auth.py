from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import RegisterRequest, TokenResponse, UserResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    email = str(data.email).lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(full_name=data.full_name.strip(), email=email,
                password_hash=hash_password(data.password), role=data.role,
                department=data.department, student_id=data.student_id,
                is_active=False, is_approved=False)
    db.add(user); db.commit(); db.refresh(user)
    return user

@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username.lower()).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user.is_active or not user.is_approved:
        raise HTTPException(status_code=403, detail="Account is waiting for admin approval")
    return {"access_token": create_access_token(str(user.id)), "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return user
