# HRIS System

A comprehensive Human Resource Information System (HRIS) built with Django REST Framework and React, designed for private universities in Zimbabwe.

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [First-Time Setup](#first-time-setup)
- [Email Configuration](#email-configuration)
- [Project Structure](#project-structure)
- [Available Commands](#available-commands)
- [Troubleshooting](#troubleshooting)

## Features

- **Employee Management** - Complete employee lifecycle management
- **Recruitment** - Vacancy posting, applications, and candidate tracking
- **Leave Management** - Leave requests, approvals, and balance tracking
- **Performance Management** - Goals, reviews, and evaluations
- **Training & Development** - Training programs and skill tracking
- **Workforce Analytics** - Reporting and analytics
- **Governance & Compliance** - Policy management and compliance tracking
- **Audit Logging** - Complete activity tracking
- **User Invites** - Email-based user onboarding with invite links
- **Role-based Access Control** - Fine-grained permissions

## Tech Stack

### Backend
- Django 5.2.11
- Django REST Framework 3.16.1
- PostgreSQL 16
- Redis 7
- Celery (async tasks)
- JWT Authentication

### Frontend
- React with Vite
- React Router
- Axios for API calls

### Infrastructure
- Docker & Docker Compose
- Nginx (production)

## Prerequisites

- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Docker Compose** v3.9+
- **Git**

No need to install Python, Node.js, PostgreSQL, or Redis separately - everything runs in containers!

## Quick Start

```bash

# 1. Copy environment file
cp .env.example .env

# 2. run migrations to create necesary relations in databse 
docker compose run --rm backend python manage.py makemigrations accounts employees recruitment leaveapp performance audit notifications contracts benefits imports system training workforce governance reports 

# 2b. confirm migrations and save them 
docker compose run --rm backend python manage.py migrate

# 3. Edit .env with your settings (at minimum, update email settings)
See "Email Configuration" section below

# 4. Start all services
docker-compose up --build -d  

# 4b. Check if all services are up 
docker compose ps 

# 5. Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/schema/swagger-ui/
```

## First-Time Setup

### 1. Environment Configuration

Copy `.env.example` to `.env` and configure the following:

```env
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=1  # Set to 0 in production
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,backend
DJANGO_CORS_ALLOWED_ORIGINS=http://localhost:5173

# Database (PostgreSQL)
POSTGRES_DB=hris
POSTGRES_USER=hris
POSTGRES_PASSWORD=hris

# Default Superuser (created automatically on first run)
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin12345
DJANGO_SUPERUSER_FIRST_NAME=System
DJANGO_SUPERUSER_LAST_NAME=Admin

# Email (SMTP) - Required for user invites
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your_email@gmail.com
EMAIL_SKIP_SSL_VERIFY=False  # Set to True only if encountering SSL issues

# Frontend
FRONTEND_BASE_URL=http://localhost:5173
INVITE_ACCEPT_PATH=/accept-invite
INVITE_EXPIRE_DAYS=7
```

### 2. Build and Start Services

```bash
# Build all images
docker compose build

# Start all services in detached mode
docker compose up -d
```

This will start:
- **PostgreSQL** (port 5432) - Database
- **Redis** (port 6379) - Cache and message broker
- **Backend Django** (port 8000) - REST API
- **Celery Worker** - Async task processing
- **Celery Beat** - Scheduled tasks
- **Frontend Vite** (port 5173) - React UI

### 3. Database Migrations

**Migrations run automatically** when the backend container starts via `entrypoint.sh`:

```bash
python manage.py makemigrations --noinput
python manage.py migrate --noinput
```

The following Django apps will be migrated:
1. `accounts` - User authentication and management
2. `audit` - Activity logging
3. `employees` - Employee records
4. `evaluation` - Performance evaluations
5. `governance` - Policies and compliance
6. `leaveapp` - Leave management
7. `notifications` - User notifications
8. `performance` - Performance reviews
9. `recruitment` - Job vacancies and applications
10. `reports` - Analytics and reporting
11. `training` - Training programs
12. `workforce` - Workforce planning

**Manual Migration (if needed):**
```bash
# Run migrations manually
docker compose exec backend python manage.py migrate

# Create a new migration after model changes
docker compose exec backend python manage.py makemigrations

# Show migration status
docker compose exec backend python manage.py showmigrations
```

### 4. Default Superuser

A superuser is **automatically created** on first run using the credentials from `.env`:

- Email: Value from `DJANGO_SUPERUSER_EMAIL`
- Password: Value from `DJANGO_SUPERUSER_PASSWORD`

If the superuser already exists, it will be skipped.

**Manual Superuser Creation (if needed):**
```bash
docker compose exec backend python manage.py createsuperuser
```

### 5. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api/v1/
- **API Documentation (Swagger)**: http://localhost:8000/api/schema/swagger-ui/
- **API Documentation (ReDoc)**: http://localhost:8000/api/schema/redoc/
- **Django Admin**: http://localhost:8000/admin/

## Email Configuration

### Gmail Setup

1. **Enable 2-Factor Authentication** on your Google account
2. **Generate App Password**:
   - Go to Google Account Settings → Security
   - Under "2-Step Verification", select "App passwords"
   - Generate a new app password for "Mail"
   - Copy the 16-character password

3. **Update .env**:
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_16_char_app_password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your_email@gmail.com
```

### SSL Certificate Issues

If you encounter `SSLCertVerificationError` (common in environments with antivirus or corporate proxies):

```env
EMAIL_SKIP_SSL_VERIFY=True  # Development only! Never use in production
```

> **⚠️ WARNING**: Only use `EMAIL_SKIP_SSL_VERIFY=True` in development environments. This disables SSL certificate verification and should never be enabled in production.

### Other SMTP Providers

- **Outlook/Office365**: `smtp.office365.com` (port 587)
- **SendGrid**: `smtp.sendgrid.net` (port 587)
- **AWS SES**: `email-smtp.[region].amazonaws.com` (port 587)

## Project Structure

```
hris-2/
├── backend/                 # Django backend
│   ├── config/             # Django settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── email_backend.py  # Custom email backend with SSL fix
│   ├── accounts/           # User authentication & invites
│   ├── audit/              # Activity logging
│   ├── employees/          # Employee management
│   ├── evaluation/         # Performance evaluations
│   ├── governance/         # Policies & compliance
│   ├── leaveapp/           # Leave management
│   ├── notifications/      # User notifications
│   ├── performance/        # Performance reviews
│   ├── recruitment/        # Vacancies & applications
│   ├── reports/            # Analytics & reporting
│   ├── training/           # Training programs
│   ├── workforce/          # Workforce planning
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── entrypoint.sh       # Auto-runs migrations on startup
├── frontend/               # React frontend
│   ├── src/
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── docker-compose.yml      # Container orchestration
├── .env                    # Environment variables (create from .env.example)
├── .env.example            # Environment template
└── README.md               # This file
```

## Available Commands

### Docker Compose

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f
docker compose logs backend -f
docker compose logs frontend -f

# Rebuild services
docker compose build
docker compose up -d --build

# Restart a specific service
docker compose restart backend

# Execute command in container
docker compose exec backend python manage.py [command]
```

### Django Management Commands

```bash
# Database migrations
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py showmigrations

# Create superuser
docker compose exec backend python manage.py createsuperuser

# Django shell
docker compose exec backend python manage.py shell

# Collect static files (production)
docker compose exec backend python manage.py collectstatic --noinput

# Run tests
docker compose exec backend python manage.py test
```

### Database Operations

```bash
# Access PostgreSQL shell
docker compose exec db psql -U hris -d hris

# Create database backup
docker compose exec db pg_dump -U hris hris > backup.sql

# Restore database
docker compose exec -T db psql -U hris hris < backup.sql

# Reset database (WARNING: deletes all data)
docker compose down -v
docker compose up -d
```

## Deployment

### Production Considerations

1. **Environment Variables**:
   ```env
   DJANGO_DEBUG=0
   DJANGO_SECRET_KEY=generate-a-new-secret-key
   EMAIL_SKIP_SSL_VERIFY=False
   ```

2. **Use Production WSGI Server**:
   Update `entrypoint.sh` to use Gunicorn:
   ```bash
   gunicorn config.wsgi:application --bind 0.0.0.0:8000
   ```

3. **Set up HTTPS** with nginx reverse proxy

4. **Configure allowed hosts**:
   ```env
   DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
   DJANGO_CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
   ```

5. **Use environment-specific settings** for database, Redis, etc.

## Troubleshooting

### Backend won't start

**Check logs:**
```bash
docker compose logs backend
```

**Common issues:**
- Database not ready: Wait a few seconds and restart
- Port 8000 already in use: Stop conflicting service or change port in docker-compose.yml
- Migration errors: Reset database or fix migrations

### Migrations failing

```bash
# Force recreate migrations (WARNING: for development only)
docker compose exec backend python manage.py migrate --fake
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```

### Email not sending

1. Check email credentials in `.env`
2. Verify SMTP settings are correct
3. For Gmail: Ensure App Password is generated (not regular password)
4. Check backend logs: `docker compose logs backend`
5. If SSL errors: Set `EMAIL_SKIP_SSL_VERIFY=True` (development only)

### Frontend not loading

**Check if Vite is running:**
```bash
docker compose logs frontend
```

**Common issues:**
- Port 5173 in use: Change in docker-compose.yml
- API connection issues: Verify `VITE_API_BASE_URL` in .env
- Node modules missing: Rebuild frontend: `docker compose build frontend`

### Database connection issues

```bash
# Verify database is running
docker compose ps db

# Check database logs
docker compose logs db

# Test connection
docker compose exec backend python manage.py dbshell
```

### Reset Everything (Fresh Start)

```bash
# Stop and remove all containers, networks, and volumes
docker compose down -v

# Remove backend image to rebuild
docker rmi hris2-backend

# Start fresh
docker compose up -d --build
```

## Support

For issues, questions, or contributions, please refer to the project documentation or contact the development team.

## License

[Specify your license here]
