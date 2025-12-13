# Production Deployment Guide

## 🚀 Quick Start - Production Deployment

### 1. Install Dependencies

```bash
cd backend
pip install -r requirement.txt
```

### 2. Set Up PostgreSQL Database

#### Option A: Local PostgreSQL Installation

**Windows:**
```powershell
# Install PostgreSQL (if not installed)
# Download from: https://www.postgresql.org/download/windows/

# Create database
psql -U postgres
CREATE DATABASE vidyarthi_db;
CREATE USER vidyarthi_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE vidyarthi_db TO vidyarthi_user;
\q
```

**Linux/Mac:**
```bash
# Install PostgreSQL
sudo apt-get install postgresql  # Ubuntu/Debian
brew install postgresql          # macOS

# Create database
sudo -u postgres psql
CREATE DATABASE vidyarthi_db;
CREATE USER vidyarthi_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE vidyarthi_db TO vidyarthi_user;
\q
```

#### Option B: Cloud Database (Recommended for Production)

- **Supabase** (Free tier): https://supabase.com/
- **Neon** (Free tier): https://neon.tech/
- **ElephantSQL** (Free tier): https://www.elephantsql.com/
- **AWS RDS**: https://aws.amazon.com/rds/postgresql/
- **Google Cloud SQL**: https://cloud.google.com/sql/postgresql

### 3. Configure Environment Variables

```bash
cd backend
cp .env.example .env
nano .env  # or use your preferred editor
```

**Required Configuration:**

```env
# Database
DATABASE_URL=postgresql://vidyarthi_user:your_secure_password@localhost:5432/vidyarthi_db

# API Keys
GEMINI_API_KEY=your_actual_gemini_api_key

# Security
SECRET_KEY=generate_with_openssl_rand_hex_32

# CORS (update with your production domain)
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Environment
ENVIRONMENT=production
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Generate SSL Certificates

#### Option A: Self-Signed (Development/Testing Only)

```bash
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365 \
  -subj "/CN=localhost"
```

#### Option B: Let's Encrypt (Production - Recommended)

```bash
# Install certbot
sudo apt-get install certbot  # Ubuntu/Debian
brew install certbot          # macOS

# Generate certificate (replace yourdomain.com)
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Certificates will be at:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

Update `.env`:
```env
SSL_ENABLED=true
SSL_CERTFILE=/etc/letsencrypt/live/yourdomain.com/fullchain.pem
SSL_KEYFILE=/etc/letsencrypt/live/yourdomain.com/privkey.pem
```

### 5. Set Up Sentry Logging (Optional but Recommended)

1. Create account: https://sentry.io/
2. Create new project: Select "FastAPI"
3. Copy DSN and add to `.env`:

```env
SENTRY_DSN=https://your-sentry-dsn@o123456.ingest.sentry.io/123456
```

### 6. Initialize Database

```bash
cd backend
python -c "from database import init_db; init_db()"
```

### 7. Test Configuration

```bash
# Test database connection
python -c "from database import engine; print('✓ Database connected!' if engine.connect() else '✗ Failed')"

# Test Gemini API
python -c "import google.generativeai as genai; import os; from dotenv import load_dotenv; load_dotenv(); genai.configure(api_key=os.getenv('GEMINI_API_KEY')); print('✓ Gemini API configured!')"
```

### 8. Run Production Server

```bash
cd backend
python server.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

With SSL:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 \
  --ssl-certfile=/path/to/cert.pem \
  --ssl-keyfile=/path/to/key.pem
```

---

## 🐳 Docker Deployment (Recommended)

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run server
CMD ["python", "server.py"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: vidyarthi_db
      POSTGRES_USER: vidyarthi_user
      POSTGRES_PASSWORD: your_secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://vidyarthi_user:your_secure_password@db:5432/vidyarthi_db
      GEMINI_API_KEY: ${GEMINI_API_KEY}
      SECRET_KEY: ${SECRET_KEY}
      ENVIRONMENT: production
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs

volumes:
  postgres_data:
```

### Run with Docker

```bash
docker-compose up -d
```

---

## 🔒 Security Checklist

- [x] ✅ Bcrypt password hashing implemented
- [x] ✅ PostgreSQL database configured
- [x] ✅ Rate limiting enabled
- [x] ✅ API keys in environment variables
- [x] ✅ Sentry logging configured
- [x] ✅ SSL/HTTPS support added
- [ ] ⚠️ Update ALLOWED_ORIGINS for production domain
- [ ] ⚠️ Generate strong SECRET_KEY
- [ ] ⚠️ Set up SSL certificates (Let's Encrypt)
- [ ] ⚠️ Configure Sentry DSN
- [ ] ⚠️ Set up database backups
- [ ] ⚠️ Configure firewall rules
- [ ] ⚠️ Set up monitoring and alerts

---

## 📊 Monitoring & Maintenance

### View Logs

```bash
# Application logs
tail -f backend/logs/app.log

# Error logs
tail -f backend/logs/error.log

# Security logs
tail -f backend/logs/security.log
```

### Database Backup

```bash
# Backup
pg_dump -U vidyarthi_user vidyarthi_db > backup_$(date +%Y%m%d).sql

# Restore
psql -U vidyarthi_user vidyarthi_db < backup_20241208.sql
```

### Update SSL Certificates (Let's Encrypt)

```bash
# Auto-renewal (set up cron job)
sudo certbot renew --quiet

# Test renewal
sudo certbot renew --dry-run
```

---

## 🌐 Cloud Deployment Options

### AWS EC2

1. Launch Ubuntu EC2 instance
2. Install dependencies
3. Configure security groups (open port 8000/443)
4. Set up Elastic IP
5. Configure Route53 for domain
6. Deploy application

### Google Cloud Platform

```bash
gcloud app deploy
```

### Heroku

```bash
heroku create vidyarthi-backend
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

### Vercel/Railway (Serverless)

- Both support FastAPI with auto-scaling
- Database: Use Supabase or Neon
- Configure environment variables in dashboard

---

## 🧪 Testing Production Setup

```bash
# Test health endpoint
curl https://yourdomain.com/health

# Test with SSL
curl -k https://localhost:8000/health

# Test rate limiting (should block after 30 requests)
for i in {1..35}; do curl https://yourdomain.com/ping; done
```

---

## 📞 Support

For issues or questions:
- GitHub Issues: [Repository URL]
- Email: support@vidyarthi-app.com
- Documentation: [Docs URL]

---

**Version**: 2.0.0  
**Last Updated**: December 8, 2025
