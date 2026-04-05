# Production Deployment Guide - Travel Companion Backend

## Overview
This guide walks you through preparing and deploying your Django backend to production. The architecture uses:
- **Backend**: Django REST Framework on Render, Railway, or Heroku
- **Database**: PostgreSQL on Neon, Supabase, or AWS RDS
- **Frontend**: React on Vercel or Netlify

---

## Step 1: Prepare Django Backend for Production

### 1.1 Update Environment Variables

Copy `.env.example` to `.env` and fill in production values:

```bash
cp .env.example .env
```

Edit `.env` with your values:
```
SECRET_KEY=your-secure-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_NAME=travel_companion
DB_USER=postgres
DB_PASSWORD=secure-password
DB_HOST=your-db-host.com
DB_PORT=5432
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 1.2 Generate Secure Secret Key

Python needs to generate a new secret key:

```bash
python manage.py shell
>>> from django.core.management.utils import get_random_secret_key
>>> print(get_random_secret_key())
```

Copy this value to your `.env` file as `SECRET_KEY=...`

### 1.3 Collect Static Files

```bash
python manage.py collectstatic --noinput
```

This creates a `staticfiles/` directory with all CSS, JS, and images needed for production.

### 1.4 Run Tests

```bash
python manage.py test
```

Ensure everything works before deploying.

### 1.5 Create Production Database Migrations

Test migrations locally first:

```bash
python manage.py migrate
```

---

## Step 2: Choose Your Hosting Platforms

### Backend Hosting Option A: Render (Recommended for Beginners)

**Why Render?** Free tier available, easiest setup, automatic deploys from Git.

#### Setup Steps:

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click **New +** → **Web Service**
4. Connect your GitHub repo (`Aayushdai/project_backend`)
5. Configuration:
   - **Name**: `travel-companion-api`
   - **Runtime**: Python 3.11
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
     ```
   - **Start Command**: 
     ```bash
     gunicorn travel_companion.wsgi:application
     ```

6. Set Environment Variables:
   - Click **Environment**
   - Add all variables from your `.env` file
   - Especially: `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`

7. Deploy!

**Database with Render:**
- Render supports PostgreSQL backups
- Or use Neon (more common)

---

### Backend Hosting Option B: Railway

1. Go to [railway.app](https://railway.app)
2. Connect GitHub repo
3. Add Django + PostgreSQL plugins
4. Similar setup with environment variables

---

### Backend Hosting Option C: Heroku (Paid, declining popularity)

Similar to Render but requires payment upfront.

---

## Step 3: PostgreSQL Database

### Option A: Neon (Recommended)

1. Go to [neon.tech](https://neon.tech)
2. Sign up → Create project
3. Get connection string:
   ```
   postgresql://user:password@host:5432/dbname
   ```
4. Parse this into your environment variables:
   - `DB_NAME=dbname`
   - `DB_USER=user`
   - `DB_PASSWORD=password`
   - `DB_HOST=host`
   - `DB_PORT=5432`

### Option B: Supabase

1. Go to [supabase.com](https://supabase.com)
2. Create project
3. Get PostgreSQL connection details
4. Same parsing as Neon

### Option C: AWS RDS

More complex but powerful option for larger deployments.

---

## Step 4: Production Checklist

- [ ] Secret key generated and in `.env`
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS set correctly
- [ ] CORS_ALLOWED_ORIGINS includes frontend domain
- [ ] Database configured (PostgreSQL)
- [ ] Static files collected (`staticfiles/` directory exists)
- [ ] Email credentials configured
- [ ] gitignore includes `.env` file
- [ ] All migrations applied to production database
- [ ] `requirements.txt` includes `gunicorn`
- [ ] Security headers enabled (HTTPS, HSTS, etc.)

---

## Step 5: Post-Deployment Tasks

### 5.1 Create Superuser (Admin Account)

After deployment, SSH into your server or use the platform's console:

```bash
python manage.py createsuperuser
```

Access admin at: `https://yourdomain.com/admin`

### 5.2 Test API Endpoints

From your frontend or Postman:

```bash
curl https://yourdomain.com/api/auth/login
```

You should get a proper JWT response.

### 5.3 Monitor Logs

Check deployment logs for errors:
- **Render**: Dashboard → Logs
- **Railway**: Dashboard → Logs
- **Heroku**: Terminal: `heroku logs --tail`

### 5.4 Set Up Backups

Most platforms auto-backup PostgreSQL. Verify this in your database settings.

---

## Security Checklist

✅ **What's Enabled:**
- SSL/TLS (HTTPS enforced)
- HSTS headers
- XSS protection
- CSRF protection
- Secure cookies
- PostgreSQL (encrypted passwords)

✅ **Environment Variables** (Never hardcoded):
- `SECRET_KEY`
- `DB_PASSWORD`
- `EMAIL_HOST_PASSWORD`
- `API_KEYS` (if used)

✅ **Disabled:**
- Debug mode
- Sensitive error messages

---

## Common Issues & Fixes

### Issue: "DisallowedHost" Error
**Fix**: Add your domain to `ALLOWED_HOSTS` in environment variables.

### Issue: "No module named 'psycopg2'"
**Fix**: Run: `pip install psycopg2-binary` and redeploy.

### Issue: Database connection timeout
**Fix**: Check DB_HOST, DB_USER, DB_PASSWORD. Test locally first.

### Issue: Static files not loading (404)
**Fix**: Run: `python manage.py collectstatic --noinput` before deploying.

### Issue: CORS errors in browser console
**Fix**: Add your frontend domain to `CORS_ALLOWED_ORIGINS`.

---

## Next Steps

1. **Deploy Frontend** (React to Vercel/Netlify)
2. **Update CORS Origins** with frontend domain
3. **Test API Integration** with frontend
4. **Set Up Custom Domain** (DNS pointing)
5. **Enable SSL Certificate** (auto with most platforms)
6. **Monitor Performance** (Render/Railway dashboards)

---

## Useful Commands

```bash
# Collect static files
python manage.py collectstatic --noinput

# Create admin user
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Create new migration for model changes
python manage.py makemigrations

# Test locally with production settings
DEBUG=False python manage.py runserver

# Check migrations status
python manage.py showmigrations
```

---

## Support Resources

- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/
- Render Docs: https://render.com/docs
- Railway Docs: https://docs.railway.app
- PostgreSQL: https://www.postgresql.org/docs/

