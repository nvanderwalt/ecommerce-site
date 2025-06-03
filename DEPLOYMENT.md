# FitFusion Deployment Guide

## Prerequisites
- Python 3.8+
- PostgreSQL
- Redis (for rate limiting)
- Nginx
- Gunicorn
- SSL certificate

## Environment Variables
Create a `.env` file with the following variables:
```
DEBUG=False
DJANGO_SECRET_KEY=your-secure-secret-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgres://user:password@localhost:5432/fitfusion
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@fitfusion.com
```

## Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fitfusion.git
cd fitfusion
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Collect static files:
```bash
python manage.py collectstatic
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

## Nginx Configuration
Create a new Nginx configuration file at `/etc/nginx/sites-available/fitfusion`:
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
        alias /path/to/fitfusion/staticfiles/;
    }

    location /media/ {
        alias /path/to/fitfusion/media/;
    }

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Gunicorn Service
Create a systemd service file at `/etc/systemd/system/fitfusion.service`:
```ini
[Unit]
Description=FitFusion Gunicorn Service
After=network.target

[Service]
User=your-user
Group=your-group
WorkingDirectory=/path/to/fitfusion
Environment="PATH=/path/to/fitfusion/venv/bin"
ExecStart=/path/to/fitfusion/venv/bin/gunicorn --workers 3 --bind unix:fitfusion.sock ecommerce_site.wsgi:application

[Install]
WantedBy=multi-user.target
```

## Start Services
```bash
sudo systemctl start fitfusion
sudo systemctl enable fitfusion
sudo systemctl restart nginx
```

## Monitoring
- Check application logs: `journalctl -u fitfusion`
- Check Nginx logs: `/var/log/nginx/error.log`
- Monitor application: `tail -f /path/to/fitfusion/logs/debug.log`

## Backup
Set up regular database backups:
```bash
pg_dump -U your-user fitfusion > backup.sql
```

## Security Checklist
- [ ] SSL certificate installed and configured
- [ ] All environment variables set
- [ ] DEBUG mode disabled
- [ ] Static files collected
- [ ] Database migrations applied
- [ ] Firewall configured
- [ ] Regular backups scheduled
- [ ] Monitoring set up 