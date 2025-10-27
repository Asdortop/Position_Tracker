# Docker Setup Guide

This guide shows you how to run the Position Tracker API using Docker with PostgreSQL.

## 🐳 Quick Start

### **Development Environment**

```bash
# 1. Clone and navigate to the project
cd position-tracker-main

# 2. Start all services
docker-compose up -d

# 3. Check if everything is running
docker-compose ps

# 4. View logs
docker-compose logs -f api
```

### **Production Environment**

```bash
# 1. Set production environment variables
export POSTGRES_PASSWORD=your_secure_password_here

# 2. Start production services
docker-compose -f docker-compose.prod.yml up -d

# 3. Check services
docker-compose -f docker-compose.prod.yml ps
```

## 📋 Services Overview

| Service | Container Name | Port | Description |
|---------|----------------|------|-------------|
| **API** | `position-tracker-api` | 8000 | FastAPI application |
| **PostgreSQL** | `position-tracker-postgres` | 5432 | Database |
| **Redis** | `position-tracker-redis` | 6379 | Caching (optional) |
| **Nginx** | `position-tracker-nginx` | 80/443 | Reverse proxy (prod only) |

## 🔧 Configuration

### **Environment Variables**

Create a `.env` file for custom configuration:

```env
# Database
POSTGRES_PASSWORD=your_secure_password_here

# API Settings
DEBUG=true
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000

# Production Settings
WORKERS=4
MAX_WORKERS=8
TIMEOUT=30
```

### **Database Configuration**

The PostgreSQL database is automatically initialized with:
- ✅ **Database**: `position_tracker`
- ✅ **User**: `tracker_user`
- ✅ **Password**: `secure_pass_123` (or from `POSTGRES_PASSWORD`)
- ✅ **Schema**: All tables, indexes, and constraints
- ✅ **Sample Data**: Initial security prices

## 🚀 Usage Commands

### **Development**

```bash
# Start all services
docker-compose up -d

# Start with logs
docker-compose up

# Stop services
docker-compose down

# Rebuild and start
docker-compose up --build -d

# View logs
docker-compose logs -f api
docker-compose logs -f postgres

# Execute commands in containers
docker-compose exec api bash
docker-compose exec postgres psql -U tracker_user -d position_tracker
```

### **Production**

```bash
# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Scale API instances
docker-compose -f docker-compose.prod.yml up -d --scale api=3

# Update services
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Stop production services
docker-compose -f docker-compose.prod.yml down
```

## 🧪 Testing

### **API Health Check**

```bash
# Check if API is running
curl http://localhost:8000/

# Check API health
curl http://localhost:8000/health

# Check database connection
curl http://localhost:8000/api/v1/portfolios/123/snapshot
```

### **Database Connection**

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U tracker_user -d position_tracker

# Run SQL queries
docker-compose exec postgres psql -U tracker_user -d position_tracker -c "SELECT * FROM tax_lots;"

# Backup database
docker-compose exec postgres pg_dump -U tracker_user position_tracker > backup.sql

# Restore database
docker-compose exec -T postgres psql -U tracker_user -d position_tracker < backup.sql
```

## 📊 Monitoring

### **Container Status**

```bash
# Check running containers
docker-compose ps

# Check resource usage
docker stats

# Check container logs
docker-compose logs api
docker-compose logs postgres
```

### **Database Monitoring**

```bash
# Check database size
docker-compose exec postgres psql -U tracker_user -d position_tracker -c "
SELECT pg_size_pretty(pg_database_size('position_tracker'));"

# Check table sizes
docker-compose exec postgres psql -U tracker_user -d position_tracker -c "
SELECT schemaname,tablename,pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"

# Check active connections
docker-compose exec postgres psql -U tracker_user -d position_tracker -c "
SELECT count(*) as active_connections FROM pg_stat_activity WHERE state = 'active';"
```

## 🔧 Troubleshooting

### **Common Issues**

#### **1. Port Already in Use**
```bash
# Check what's using the port
netstat -tulpn | grep :8000

# Kill the process
sudo kill -9 <PID>

# Or change the port in docker-compose.yml
```

#### **2. Database Connection Failed**
```bash
# Check if PostgreSQL is running
docker-compose logs postgres

# Check database health
docker-compose exec postgres pg_isready -U tracker_user -d position_tracker

# Restart PostgreSQL
docker-compose restart postgres
```

#### **3. API Won't Start**
```bash
# Check API logs
docker-compose logs api

# Check if dependencies are installed
docker-compose exec api pip list

# Rebuild the API container
docker-compose build --no-cache api
```

#### **4. Permission Issues**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Rebuild containers
docker-compose down
docker-compose up --build -d
```

### **Debug Mode**

```bash
# Run in debug mode
DEBUG=true docker-compose up

# Enable SQL logging
docker-compose exec api python -c "
import os
os.environ['SQLALCHEMY_ECHO'] = 'true'
"
```

## 📈 Performance Tuning

### **Database Optimization**

```bash
# Connect to PostgreSQL and run optimization
docker-compose exec postgres psql -U tracker_user -d position_tracker -c "
-- Analyze tables for better query planning
ANALYZE;

-- Check index usage
SELECT schemaname, tablename, attname, n_distinct, correlation 
FROM pg_stats WHERE schemaname = 'public';
"
```

### **Container Resource Limits**

Edit `docker-compose.yml` to set resource limits:

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

## 🔄 Backup and Restore

### **Database Backup**

```bash
# Create backup
docker-compose exec postgres pg_dump -U tracker_user position_tracker > backup_$(date +%Y%m%d_%H%M%S).sql

# Compress backup
gzip backup_*.sql
```

### **Full System Backup**

```bash
# Backup volumes
docker run --rm -v position-tracker-main_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .

# Restore volumes
docker run --rm -v position-tracker-main_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /data
```

## 🚀 Deployment

### **Production Deployment**

1. **Set up environment**:
   ```bash
   export POSTGRES_PASSWORD=your_secure_password
   export DOMAIN=your-domain.com
   ```

2. **Start services**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Configure SSL** (optional):
   ```bash
   # Place SSL certificates in ./ssl/
   mkdir ssl
   # Copy your cert.pem and key.pem files
   ```

4. **Set up monitoring**:
   ```bash
   # Install monitoring tools
   docker-compose -f docker-compose.prod.yml exec api pip install prometheus-client
   ```

### **Scaling**

```bash
# Scale API instances
docker-compose -f docker-compose.prod.yml up -d --scale api=3

# Use load balancer
docker-compose -f docker-compose.prod.yml up -d nginx
```

## 📞 Support

For issues with Docker setup:

1. **Check logs**: `docker-compose logs`
2. **Verify configuration**: Check `.env` and `docker-compose.yml`
3. **Test connectivity**: Use the health check endpoints
4. **Review resources**: Ensure sufficient memory and CPU

---

**Docker setup completed!** 🐳

Your Position Tracker API is now running in Docker with PostgreSQL, Redis, and Nginx!
