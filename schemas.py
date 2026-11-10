from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field

class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(pattern="^(student|teacher)$")
    department: str | None = None
    student_id: str | None = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    department: str | None
    student_id: str | None
    is_active: bool
    is_approved: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DocumentResponse(BaseModel):
    id: int
    title: str
    description: str | None
    original_filename: str
    file_size: int
    department: str | None
    course_name: str | None
    academic_year: str | None
    status: str
    download_count: int
    view_count: int
    uploader_id: int
    category_id: int | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None
    model_config = ConfigDict(from_attributes=True)
