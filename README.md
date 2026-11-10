# NUDL Backend v2

FastAPI backend for Nangarhar University Digital Library.

## Included
- Separate student and teacher registration
- JWT login and profile endpoint
- New accounts wait for administrator approval
- Admin: approve/disable users, approve/reject PDFs, create categories, statistics
- Super admin: promote approved users to admin
- PDF upload, validation, search, preview-ready detail endpoint and download
- Favorites and category filters

## Local run (Python 3.12)
    python -m venv .venv
    # Windows: .venv\\Scripts\\activate
    pip install -r requirements.txt
    copy .env.example .env
    uvicorn app.main:app --reload

Open http://127.0.0.1:8000/docs

## First super admin
    python create_admin.py --name "NUDL Super Admin" --email "admin@example.com" --password "Use-A-Strong-Password-123"

## Render
Build: pip install -r requirements.txt
Start: uvicorn app.main:app --host 0.0.0.0 --port $PORT

Set DATABASE_URL to a Render PostgreSQL Internal Database URL, SECRET_KEY to a long random secret, and UPLOAD_DIR to /var/data/uploads. The included render.yaml requests a persistent disk; persistent disks are generally paid. Without persistent storage, uploaded PDFs can be lost on redeploy/restart. Configure CORS_ORIGINS to your frontend domain before public launch.

Never upload .env, database passwords, or secret keys to GitHub. This code is a clean starter backend; test it with your frontend and configure production backups before university-wide use.
