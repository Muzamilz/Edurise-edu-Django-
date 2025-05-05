# Edurise Production Deployment Guide

## Table of Contents
1. [Pre-deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [Security Measures](#security-measures)
4. [Database Configuration](#database-configuration)
5. [Static and Media Files](#static-and-media-files)
6. [Email Configuration](#email-configuration)
7. [Zoom Integration](#zoom-integration)
8. [Performance Optimization](#performance-optimization)
9. [Hostinger Deployment Steps](#hostinger-deployment-steps)
10. [Post-deployment Tasks](#post-deployment-tasks)

## Pre-deployment Checklist

### Code Review
- [ ] Remove all debug print statements
- [ ] Remove any test/development code
- [ ] Ensure all sensitive data is moved to environment variables
- [ ] Review and clean up unused imports
- [ ] Check for any hardcoded URLs and replace with settings variables

### Dependencies
- [ ] Create requirements.txt with exact versions
- [ ] Remove development-only packages
- [ ] Update all packages to their latest stable versions
- [ ] Document all third-party integrations

## Environment Setup

1. Create a production settings file:
```python
# settings_prod.py
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

2. Set up environment variables:
```bash
# .env.production
SECRET_KEY=your-secure-secret-key
DATABASE_URL=your-production-database-url
EMAIL_HOST=your-smtp-server
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-email-password
ZOOM_API_KEY=your-zoom-api-key
ZOOM_API_SECRET=your-zoom-api-secret
```

## Security Measures

1. Update Django settings:
```python
# settings_prod.py
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

2. Implement security headers:
```python
# settings_prod.py
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

3. Configure CORS if needed:
```python
CORS_ALLOWED_ORIGINS = [
    "https://your-domain.com",
]
```

## Database Configuration

1. Configure PostgreSQL for production:
```python
# settings_prod.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

2. Database optimization:
- [ ] Create necessary indexes
- [ ] Set up database backups
- [ ] Configure connection pooling

## Static and Media Files

1. Configure static files:
```python
# settings_prod.py
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
```

2. Set up a CDN for static files (recommended):
- [ ] Configure AWS S3 or similar service
- [ ] Update settings to use CDN URLs
- [ ] Set up proper caching headers

## Email Configuration

1. Configure production email settings:
```python
# settings_prod.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.hostinger.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@your-domain.com'
EMAIL_HOST_PASSWORD = 'your-email-password'
DEFAULT_FROM_EMAIL = 'your-email@your-domain.com'
```

## Zoom Integration

1. Update Zoom credentials:
- [ ] Set up production Zoom API credentials
- [ ] Test all Zoom-related functionality
- [ ] Implement proper error handling
- [ ] Set up webhook endpoints for Zoom events

## Performance Optimization

1. Implement caching:
```python
# settings_prod.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

2. Configure Gunicorn:
```bash
# gunicorn_config.py
workers = 3
bind = "127.0.0.1:8000"
timeout = 120
```

3. Set up Nginx configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /static/ {
        alias /path/to/your/staticfiles/;
    }

    location /media/ {
        alias /path/to/your/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Hostinger Deployment Steps

1. Server Setup:
- [ ] Purchase hosting plan on Hostinger
- [ ] Set up domain and DNS records
- [ ] Configure SSL certificate

2. Database Setup:
- [ ] Create PostgreSQL database
- [ ] Import database schema
- [ ] Configure database user permissions

3. Application Deployment:
```bash
# On your local machine
python manage.py collectstatic
python manage.py check --deploy

# Create deployment package
tar -czf edurise.tar.gz *

# On Hostinger server
cd /home/username/your-domain.com
tar -xzf edurise.tar.gz
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
```

4. Configure Hostinger:
- [ ] Set up Python application
- [ ] Configure application port
- [ ] Set up process manager (Supervisor)
- [ ] Configure Nginx as reverse proxy

## Post-deployment Tasks

1. Monitoring Setup:
- [ ] Configure error logging
- [ ] Set up monitoring tools
- [ ] Implement backup strategy

2. Testing:
- [ ] Test all user flows
- [ ] Verify email functionality
- [ ] Test Zoom integration
- [ ] Check payment processing
- [ ] Verify file uploads

3. Documentation:
- [ ] Update API documentation
- [ ] Create maintenance procedures
- [ ] Document deployment process
- [ ] Create backup and restore procedures

4. Performance Monitoring:
- [ ] Set up Google Analytics
- [ ] Configure server monitoring
- [ ] Set up error tracking (e.g., Sentry)

## Regular Maintenance

1. Weekly Tasks:
- [ ] Check server logs
- [ ] Monitor disk space
- [ ] Review error reports
- [ ] Backup verification

2. Monthly Tasks:
- [ ] Security updates
- [ ] Package updates
- [ ] Performance review
- [ ] Database optimization

3. Quarterly Tasks:
- [ ] SSL certificate renewal
- [ ] Security audit
- [ ] Performance optimization
- [ ] Backup strategy review

## Emergency Procedures

1. Server Issues:
- [ ] Contact Hostinger support
- [ ] Check server logs
- [ ] Verify application logs
- [ ] Test database connectivity

2. Application Issues:
- [ ] Check error logs
- [ ] Verify environment variables
- [ ] Test database connections
- [ ] Review recent changes

3. Data Issues:
- [ ] Verify backup integrity
- [ ] Check database logs
- [ ] Review recent transactions
- [ ] Contact database administrator

Remember to keep this guide updated as you make changes to the deployment process or infrastructure. 