# Backend Production Deployment Checklist

## ✅ Completed: Django Configuration for Production

### Environment-Aware Settings
- [x] `DEBUG` mode controlled by environment variable (defaults to False)
- [x] `ALLOWED_HOSTS` configurable via `ALLOWED_HOSTS` env var
- [x] `SECRET_KEY` loaded from environment (with fallback)
- [x] `.env` file auto-loaded if present using `python-dotenv`

### Database Configuration
- [x] **Development**: SQLite (auto-selected when DEBUG=True)
- [x] **Production**: PostgreSQL (auto-selected when DEBUG=False)
- [x] Database credentials via environment variables:
  - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- [x] Connection pooling enabled (`CONN_MAX_AGE=600`)
- [x] Atomic requests enabled for transactions

### Security Headers (Production)
- [x] SSL/HTTPS redirect enforced
- [x] Secure cookies enabled
- [x] CSRF protection with secure cookies
- [x] XSS filter enabled
- [x] HSTS headers (1 year, include subdomains, preload)
- [x] X-Frame-Options = DENY (clickjacking protection)
- [x] Content Security Policy enabled

### CORS Configuration
- [x] Development: `localhost:3000` and `127.0.0.1:3000`
- [x] Production: Configurable via `CORS_ALLOWED_ORIGINS` env var
- [x] Proper credentials handling enabled

### Static & Media Files
- [x] `STATIC_ROOT = staticfiles/` (for collection)
- [x] `STATICFILES_DIRS` configured for development
- [x] `MEDIA_ROOT = mediafiles/` for uploads
- [x] Ready for `collectstatic` command

---

## 📋 Files Created/Updated

### Configuration Files
| File | Purpose |
|------|---------|
| `travel_companion/settings.py` | Updated for production (DEBUG, ALLOWED_HOSTS, DB, security) |
| `.env.example` | Template for environment variables (comprehensive) |
| `Procfile` | For Heroku/similar platforms (release + web process) |
| `runtime.txt` | Python version specification |
| `render.yaml` | Render.com deployment configuration |

### Documentation
| File | Purpose |
|------|---------|
| `PRODUCTION_DEPLOYMENT_GUIDE.md` | Complete step-by-step deployment instructions |
| `DEPLOYMENT_CHECKLIST.md` | This file - quick reference |

### Security
- [x] `.gitignore` already excludes `.env` (no credentials in Git)
- [x] `psycopg2-binary` in `requirements.txt` (PostgreSQL driver)
- [x] `gunicorn` in `requirements.txt` (production WSGI server)

---

## 🚀 Quick Start: Deploy to Render

### 1. Prepare Repository
```bash
# Ensure .env is in .gitignore (already done)
# Push code to GitHub
git add .
git commit -m "Production setup"
git push
```

### 2. Create `.env` File (Local Only)
```bash
cp .env.example .env
# Edit .env with your actual values
```

### 3. Test Locally
```bash
# Set DEBUG=True for dev testing
python manage.py runserver

# Test with production settings (DEBUG=False) - optional
# DEBUG=False python manage.py runserver
```

### 4. Deploy on Render.com
1. Sign in at [render.com](https://render.com)
2. Click **New +** → **Web Service**
3. Connect GitHub repo: `Aayushdai/project_backend`
4. Configure:
   - **Build Command**: 
     ```
     pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
     ```
   - **Start Command**: 
     ```
     gunicorn travel_companion.wsgi:application
     ```
5. Add Environment Variables (from your `.env` file):
   - `SECRET_KEY=...`
   - `DEBUG=False`
   - `ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com`
   - Database variables (`DB_NAME`, `DB_USER`, etc.)
   - `CORS_ALLOWED_ORIGINS=https://yourdomain.com`
   - Email variables

6. Deploy → Wait for success

### 5. Set Up Database (Neon.tech)
1. Go to [neon.tech](https://neon.tech)
2. Create PostgreSQL database
3. Get connection string from Neon
4. Extract and add to Render environment variables

### 6. Post-Deployment
```bash
# Create admin user (via Render console)
python manage.py createsuperuser

# Access admin: https://yourdomain.com/admin
```

---

## ⚙️ Environment Variables Reference

### Required for Production
```
SECRET_KEY=<generated-randomly>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-ip
DB_NAME=travel_companion
DB_USER=postgres
DB_PASSWORD=<secure-password>
DB_HOST=<neon-host>.neon.tech
DB_PORT=5432
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=<app-password>
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### Optional
```
USE_S3=True  # For AWS S3 file storage
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=...
```

---

## 🔒 Security Checklist

- [x] DEBUG = False in production
- [x] SECRET_KEY is unique and secret
- [x] ALLOWED_HOSTS configured correctly
- [x] CORS origins restricted to your frontend domain
- [x] Email credentials in environment (not hardcoded)
- [x] SSL/HTTPS enforced
- [x] CSRF protection enabled
- [x] XSS protection enabled
- [x] PostgreSQL in production (not SQLite)
- [x] Static files collected before deployment
- [x] Database migrations applied
- [ ] **TODO**: Test login endpoint
- [ ] **TODO**: Test API endpoints with frontend
- [ ] **TODO**: Monitor error logs for weeks 1

---

## 📝 Testing Before Deployment

### Local Testing (Dev Mode)
```bash
python manage.py test
python manage.py runserver
```

### Testing with Production Settings (Advanced)
```bash
# Create a test .env with DEBUG=False
DEBUG=False python manage.py shell
# Test imports and database connection
>>> from django.db import connection
>>> connection.ensure_connection()
```

---

## 🆘 Troubleshooting Quick Links

| Problem | Solution |
|---------|----------|
| "DisallowedHost" | Check ALLOWED_HOSTS env var |
| "No module psycopg2" | Install: `pip install psycopg2-binary` |
| DB connection error | Test DB_HOST, DB_USER, DB_PASSWORD |
| App won't start | Check Render/Railway logs for errors |
| CORS errors | Verify CORS_ALLOWED_ORIGINS includes frontend |
| Static files 404 | Run: `python manage.py collectstatic --noinput` |

---

## 📚 Documentation

- Full Guide: [PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md)
- Django Docs: https://docs.djangoproject.com/en/stable/howto/deployment/
- Render Docs: https://render.com/docs/deploy-django
- Neon Docs: https://neon.tech/docs/

---

## Before Moving to Frontend Deployment

1. ✅ Test backend deployment works
2. ✅ Test `/api/auth/login` endpoint
3. ✅ Verify static files serve correctly
4. ✅ Check admin panel works
5. ✅ Get backend URL (e.g., `https://api.yourdomain.com`)
6. → Then deploy React frontend to Vercel/Netlify
7. → Update `CORS_ALLOWED_ORIGINS` with frontend URL

---

**Last Updated**: April 5, 2026
**Status**: Ready for deployment
