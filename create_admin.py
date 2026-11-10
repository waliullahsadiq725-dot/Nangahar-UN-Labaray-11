import argparse
from app.database import Base, engine, SessionLocal
from app import models
from app.models import User
from app.core.security import hash_password

def main():
    parser = argparse.ArgumentParser(description="Create first NUDL super admin")
    parser.add_argument("--name", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        email = args.email.strip().lower()
        if db.query(User).filter(User.email == email).first():
            print("This email already exists."); return
        user = User(full_name=args.name.strip(), email=email,
                    password_hash=hash_password(args.password), role="super_admin",
                    is_active=True, is_approved=True)
        db.add(user); db.commit()
        print(f"Super admin created: {email}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
