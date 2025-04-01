# Deployment Guide

This guide provides instructions for deploying DataStream Pro in different environments.

## Prerequisites

- Docker and Docker Compose
- Python 3.8 or higher
- PostgreSQL 13 or higher
- Redis 6 or higher
- Node.js 16 or higher (for frontend)

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/datastream-pro.git
cd datastream-pro
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize database:
```bash
alembic upgrade head
```

6. Run development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker Deployment

### Build Docker Image

```bash
docker build -t datastream-pro .
```

### Run with Docker Compose

1. Create docker-compose.yml:
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/datastream
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=datastream
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

2. Start services:
```bash
docker-compose up -d
```

## Production Deployment

### System Requirements

- 4+ CPU cores
- 8GB+ RAM
- 100GB+ storage
- Ubuntu 20.04 LTS or higher

### Server Setup

1. Update system:
```bash
sudo apt update
sudo apt upgrade -y
```

2. Install dependencies:
```bash
sudo apt install -y python3.8 python3.8-venv postgresql redis-server nginx
```

3. Configure PostgreSQL:
```bash
sudo -u postgres psql
CREATE DATABASE datastream;
CREATE USER datastream WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE datastream TO datastream;
\q
```

4. Configure Redis:
```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### Application Deployment

1. Clone repository:
```bash
git clone https://github.com/yourusername/datastream-pro.git
cd datastream-pro
```

2. Create virtual environment:
```bash
python3.8 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with production configuration
```

5. Initialize database:
```bash
alembic upgrade head
```

6. Create systemd service:
```bash
sudo nano /etc/systemd/system/datastream.service
```

Add:
```ini
[Unit]
Description=DataStream Pro API
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/path/to/datastream-pro
Environment="PATH=/path/to/datastream-pro/venv/bin"
ExecStart=/path/to/datastream-pro/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

7. Start service:
```bash
sudo systemctl enable datastream
sudo systemctl start datastream
```

### Nginx Configuration

1. Create Nginx configuration:
```bash
sudo nano /etc/nginx/sites-available/datastream
```

Add:
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

2. Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/datastream /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL Configuration

1. Install Certbot:
```bash
sudo apt install -y certbot python3-certbot-nginx
```

2. Get SSL certificate:
```bash
sudo certbot --nginx -d your_domain.com
```

## Monitoring

### Prometheus & Grafana Setup

1. Install Prometheus:
```bash
wget https://github.com/prometheus/prometheus/releases/download/v2.30.3/prometheus-2.30.3.linux-amd64.tar.gz
tar xvf prometheus-2.30.3.linux-amd64.tar.gz
sudo mv prometheus-2.30.3.linux-amd64 /etc/prometheus
```

2. Configure Prometheus:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'datastream'
    static_configs:
      - targets: ['localhost:8000']
```

3. Install Grafana:
```bash
wget https://dl.grafana.com/oss/release/grafana-8.1.2.linux-amd64.tar.gz
tar xvf grafana-8.1.2.linux-amd64.tar.gz
sudo mv grafana-8.1.2 /etc/grafana
```

4. Start services:
```bash
sudo systemctl start prometheus
sudo systemctl start grafana-server
```

### Logging

1. Configure logging:
```python
# app/core/logging_config.py
import logging
import logging.handlers
import os

def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    handler = logging.handlers.RotatingFileHandler(
        f"{log_dir}/app.log",
        maxBytes=10000000,
        backupCount=5
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
```

## Backup & Recovery

### Database Backup

1. Create backup script:
```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

pg_dump -U datastream datastream > $BACKUP_DIR/backup_$TIMESTAMP.sql
```

2. Schedule backups:
```bash
0 0 * * * /path/to/backup_script.sh
```

### Recovery

1. Restore database:
```bash
psql -U datastream datastream < backup_20240101_000000.sql
```

## Scaling

### Horizontal Scaling

1. Set up load balancer:
```nginx
upstream datastream {
    server 192.168.1.10:8000;
    server 192.168.1.11:8000;
    server 192.168.1.12:8000;
}

server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://datastream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

2. Configure Redis cluster:
```bash
redis-cli --cluster create \
    192.168.1.10:6379 \
    192.168.1.11:6379 \
    192.168.1.12:6379
```

### Vertical Scaling

1. Update system resources:
```bash
# Increase swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

2. Optimize PostgreSQL:
```ini
# postgresql.conf
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 256MB
```

## Security

### Firewall Configuration

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### SSL/TLS Configuration

1. Update SSL configuration:
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
ssl_prefer_server_ciphers on;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

2. Enable HSTS:
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

## Maintenance

### Updates

1. Update application:
```bash
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
sudo systemctl restart datastream
```

2. Update dependencies:
```bash
pip install --upgrade -r requirements.txt
```

### Monitoring

1. Check logs:
```bash
sudo journalctl -u datastream -f
```

2. Monitor resources:
```bash
htop
```

3. Check database:
```bash
psql -U datastream -d datastream -c "SELECT * FROM pg_stat_activity;"
```

## Troubleshooting

### Common Issues

1. Database connection issues:
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

2. Application issues:
```bash
# Check application logs
tail -f logs/app.log

# Check system logs
sudo journalctl -u datastream -f
```

3. Performance issues:
```bash
# Check system resources
top
htop
iostat

# Check database performance
psql -U datastream -d datastream -c "SELECT * FROM pg_stat_activity;"
``` 