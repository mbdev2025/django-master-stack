---
name: deploy
description: Déploiement automatisé de l'application Django avec Docker, CI/CD et monitoring
---

# Skill: Deploy

Ce skill gère le déploiement complet de l'application Django SaaS en production.

## Utilisation

```
/deploy [environment]
```

## Environnements

- `staging` (défaut): Environnement de pré-production
- `production`: Environnement de production
- `local`: Environnement de développement local

## Ce que le skill fait

### 1. Containerisation Docker
- Crée `Dockerfile` optimisé multi-stage
- Crée `docker-compose.yml` avec tous les services
- Configuration des volumes et networks
- Health checks et restart policies

### 2. CI/CD Pipeline
- Configuration GitHub Actions ou GitLab CI
- Tests automatisés à chaque commit
- Build et push des images Docker
- Déploiement automatique en staging/production

### 3. Configuration Production
- Variables d'environnement sécurisées
- PostgreSQL avec backup automatique
- Redis pour cache et Celery
- Nginx reverse proxy
- SSL/TLS avec Let's Encrypt

### 4. Monitoring & Logging
- Prometheus + Grafana pour metrics
- Sentry pour error tracking
- Log centralization
- Performance monitoring

### 5. Security Hardening
- Secrets management (Docker Swarm Secrets ou AWS Secrets Manager)
- Firewall configuration
- Rate limiting
- CORS configuration
- Security headers

## Fichiers générés

```
/
├── Dockerfile                    # Image application optimisée
├── docker-compose.yml            # Services complets
├── docker-compose.prod.yml       # Configuration production
├── .github/workflows/
│   └── deploy.yml               # GitHub Actions
├── nginx/
│   ├── nginx.conf              # Configuration reverse proxy
│   └── ssl/                    # Certificats SSL
├── scripts/
│   ├── deploy.sh               # Script déploiement
│   ├── backup.sh               # Script backup
│   └── monitor.sh              # Health checks
└── prometheus/
    └── prometheus.yml          # Configuration monitoring
```

## Services Docker Compose

```yaml
services:
  db:          # PostgreSQL
  redis:       # Cache & Celery broker
  web:         # Django application
  worker:      # Celery worker
  beat:        # Celery beat scheduler
  nginx:       # Reverse proxy
  prometheus:  # Monitoring
  grafana:     # Dashboard
```

## Commandes de déploiement

```bash
# Déploiement staging
/deploy staging

# Déploiement production
/deploy production

# Déploiement local avec Docker
/deploy local

# Mise à jour d'un environnement existant
/deploy staging --update

# Rollback en cas de problème
/deploy staging --rollback
```

## Configuration requise

### Variables d'environnement production
```bash
DJANGO_SECRET_KEY=<secret_key_à_générer>
DATABASE_URL=postgres://user:pass@db:5432/dbname
REDIS_URL=redis://redis:6379/0
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DEBUG=False
```

### Infrastructure minimale
- 2 CPU cores
- 4 GB RAM
- 20 GB SSD
- Ports: 80, 443, 8000

## Pipeline CI/CD

1. **Test Phase**
   - Linting (black, flake8, mypy)
   - Tests unitaires (pytest)
   - Tests d'intégration
   - Coverage report

2. **Build Phase**
   - Build Docker image
   - Tag avec version/git SHA
   - Push vers registry

3. **Deploy Phase**
   - Database migrations
   - Static files collection
   - Container restart
   - Health checks

## Monitoring

### Métriques collectées
- Requests per second
- Response times
- Error rates
- Database query performance
- Cache hit rates
- Celery task stats

### Alertes
- CPU > 80%
- Memory > 85%
- Disk space < 10%
- Error rate > 5%
- Response time > 2s

## Backup Strategy

- **Database**: Backup quotidien vers S3
- **Media files**: Sync vers S3
- **Configuration**: Version control
- **Rétention**: 30 jours

## Rollback automatique

En cas d'échec des health checks:
1. Arrêt du nouveau déploiement
2. Restauration de la version précédente
3. Notification équipe
4. Logs analysés

## Documentation déployée

- `/api/docs/` - Swagger UI
- `/api/redoc/` - ReDoc
- `/metrics/` - Prometheus metrics
- `/health/` - Health check endpoint

## Sécurité production

- Password secrets générés aléatoirement
- SSL/TLS obligatoire
- Firewall restrictif
- Rate limiting: 100 req/min par IP
- JWT tokens: 60 min access, 7 jours refresh
- CORS: domaines autorisés seulement

## Performance optimisation

- PostgreSQL connection pooling
- Redis caching strategy
- Static files sur CDN (Cloudflare/AWS CloudFront)
- Gzip compression
- HTTP/2 enabled
- Database indexes optimisés

## Coûts estimés (AWS/GCP)

- **Staging**: ~50€/mois (t2.medium, RDS t2.micro)
- **Production**: ~200€/mois (m5.large, RDS db.t3.medium, ElastiCache)
