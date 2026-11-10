from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    sub = decode_access_token(token)
    if not sub:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    try:
        user = db.get(User, int(sub))
    except (TypeError, ValueError):
        user = None
    if not user or not user.is_active or not user.is_approved:
        raise HTTPException(status_code=401, detail="Account is not active or approved")
    return user

def require_roles(*roles):
    def checker(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Permission denied")
        return user
    return checker

def require_admin(user: User = Depends(require_roles("admin", "super_admin"))):
    return user
def require_super_admin(user: User = Depends(require_roles("super_admin"))):
    return user
