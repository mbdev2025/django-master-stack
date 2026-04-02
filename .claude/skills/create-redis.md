---
name: create-redis
description: Configure Redis pour le cache, sessions, Celery avec optimisations SaaS
---

# Skill: Create Redis

Configure Redis instantanément pour le cache, sessions, et tâches async.

## Utilisation

```
/create-redis [options]
```

## Exemples

```bash
# Configuration Redis complète
/create-redis

# Avec options spécifiques
/create-redis --cache:redis --sessions:redis --celery:full

# Redis Cluster pour HA
/create-redis --cluster --sentinel
```

## Options

- `--cache:redis` | `--cache:memcached` | `--cache:database`
- `--sessions:redis` | `--sessions:signed_cookies`
- `--celery:full` | `--celery:basic`
- `--cluster` | `--sentinel` pour haute disponibilité
- `--monitoring` avec Redis Exporter

## Ce qui est généré

### 1. Configuration Django Complete

```python
# settings.py
REDIS_HOST = env('REDIS_HOST', default='localhost')
REDIS_PORT = env('REDIS_PORT', default=6379)
REDIS_DB = env('REDIS_DB', default=0)
REDIS_PASSWORD = env('REDIS_PASSWORD', default=None)
REDIS_URL = f'redis://{":".join(filter(None, [REDIS_PASSWORD, f"{REDIS_HOST}:{REDIS_PORT}"]))}/{REDIS_DB}'

# CACHES
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,
        },
        'KEY_PREFIX': 'django',
        'TIMEOUT': 300,  # 5 minutes par défaut
        'VERSION': 1,
    }
}

# Cache custom timeouts
CACHE_TIMEOUTS = {
    'default': 300,
    'static_files': 86400,  # 24 heures
    'api_responses': 60,     # 1 minute
    'user_sessions': 1800,   # 30 minutes
    'permissions': 3600,     # 1 heure
}

# Session backend
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 1209600  # 2 semaines
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = 'Lax'

# Celery Configuration
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

# Celery Worker Settings
CELERY_WORKER_PREFETCH_MULTIPLIER = 4
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000

# Celery Task Settings
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True

# Celery Beat Settings
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_BEAT_MAX_LOOP_INTERVAL = 60  # seconds

# Celery Routing
CELERY_TASK_ROUTES = {
    'apps.users.tasks.*': {'queue': 'users'},
    'apps.notifications.tasks.*': {'queue': 'notifications'},
    'apps.payments.tasks.*': {'queue': 'payments'},
    'apps.analytics.tasks.*': {'queue': 'analytics'},
}

# Celery Priority
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('users', Exchange('users'), routing_key='users'),
    Queue('notifications', Exchange('notifications'), routing_key='notifications'),
    Queue('payments', Exchange('payments'), routing_key='payments'),
    Queue('analytics', Exchange('analytics'), routing_key='analytics'),
)
```

### 2. Docker Compose avec Redis

```yaml
# docker-compose.yml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    environment:
      - REDIS_PASSWORD=${REDIS_PASSWORD}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  redis-exporter:
    image: oliver006/redis_exporter:latest
    environment:
      - REDIS_ADDR=redis:6379
      - REDIS_PASSWORD=${REDIS_PASSWORD}
    ports:
      - "9121:9121"
    depends_on:
      - redis

  celery-worker:
    build: .
    command: celery -A config worker -l info -Q default,users,notifications,payments,analytics
    volumes:
      - .:/app
    depends_on:
      - redis
      - db
    environment:
      - CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD}@redis:6379/0
    restart: unless-stopped

  celery-beat:
    build: .
    command: celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    volumes:
      - .:/app
    depends_on:
      - redis
      - db
      - celery-worker
    environment:
      - CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
    restart: unless-stopped

  flower:
    build: .
    command: celery -A config flower --port=5555
    ports:
      - "5555:5555"
    environment:
      - CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD}@redis:6379/0
    depends_on:
      - redis
      - celery-worker
    restart: unless-stopped

volumes:
  redis_data:
```

### 3. Cache Helpers

```python
# utils/cache.py
from django.core.cache import cache
from django.utils.encoding import force_str
import hashlib
import json

def cache_key(*args, **kwargs):
    """Générer une clé de cache unique"""
    key = ':'.join([
        force_str(arg) for arg in args
    ] + [
        f'{k}={v}' for k, v in sorted(kwargs.items())
    ])
    return hashlib.md5(key.encode()).hexdigest()

def cache_result(timeout=300, key_prefix=''):
    """Décorateur pour mettre en cache les résultats de fonction"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Générer clé de cache
            key = f'{key_prefix}:{cache_key(func.__name__, *args, **kwargs)}'

            # Essayer de récupérer du cache
            result = cache.get(key)
            if result is not None:
                return result

            # Exécuter fonction
            result = func(*args, **kwargs)

            # Mettre en cache
            cache.set(key, result, timeout)
            return result
        return wrapper
    return decorator

def invalidate_cache_pattern(pattern):
    """Invalider tous les keys matching un pattern"""
    import re
    from django.core.cache import cache

    # Pour Redis, on peut utiliser SCAN avec MATCH
    if cache.__class__.__name__ == 'RedisCache':
        with cache.client.get_client() as client:
            for key in client.scan_iter(match=f'*{pattern}*'):
                cache.delete(key)
    else:
        # Fallback pour autres backends
        keys = cache.keys(f'*{pattern}*')
        cache.delete_many(keys)

# Cache decorators pour use cases communs
def cache_user_permissions(timeout=3600):
    """Cache des permissions utilisateur"""
    def decorator(func):
        def wrapper(user, *args, **kwargs):
            key = f'user_permissions:{user.id}'
            result = cache.get(key)
            if result is None:
                result = func(user, *args, **kwargs)
                cache.set(key, result, timeout)
            return result
        return wrapper
    return decorator

def cache_organization_data(timeout=1800):
    """Cache des données organization"""
    def decorator(func):
        def wrapper(org_id, *args, **kwargs):
            key = f'org_data:{org_id}'
            result = cache.get(key)
            if result is None:
                result = func(org_id, *args, **kwargs)
                cache.set(key, result, timeout)
            return result
        return wrapper
    return decorator
```

### 4. Session Management

```python
# middleware.py
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin

class SessionCacheMiddleware(MiddlewareMixin):
    """Middleware pour optimiser les sessions avec cache"""

    def process_request(self, request):
        if request.user.is_authenticated:
            # Cache des données utilisateur fréquemment accédées
            cache_key = f'user_data:{request.user.id}'

            user_data = cache.get(cache_key)
            if user_data is None:
                user_data = {
                    'organization_id': request.user.organization.id,
                    'role': request.user.role,
                    'permissions': list(
                        request.user.user_permissions.values_list(
                            'codename', flat=True
                        )
                    ),
                }
                cache.set(cache_key, user_data, timeout=1800)

            # Attacher à la request
            request.user_cache = user_data

        return None

class CachePermissionMiddleware(MiddlewareMixin):
    """Middleware pour mettre en cache les vérifications de permissions"""

    def process_request(self, request):
        if request.user.is_authenticated:
            cache_key = f'user_perms:{request.user.id}'

            permissions = cache.get(cache_key)
            if permissions is None:
                from django.contrib.auth.models import Permission
                permissions = {
                    f'{p.content_type.app_label}.{p.codename}'
                    for p in Permission.objects.filter(
                        user=request.user
                    ) | Permission.objects.filter(
                        group__user=request.user
                    )
                }
                cache.set(cache_key, permissions, timeout=3600)

            request.cached_permissions = permissions

        return None
```

### 5. Celery Tasks

```python
# tasks.py
from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings

logger = get_task_logger(__name__)

@shared_task(bind=True, max_retries=3)
def send_email_task(self, subject, message, recipient_list):
    """Envoyer email de manière asynchrone"""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list
        )
        logger.info(f'Email sent to {recipient_list}')
        return {'status': 'sent'}
    except Exception as exc:
        logger.error(f'Email failed: {exc}')
        raise self.retry(exc=exc, countdown=60)

@shared_task
def update_user_cache(user_id):
    """Mettre à jour le cache utilisateur"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)
        cache_key = f'user_data:{user_id}'

        # Invalidate ancien cache
        cache.delete(cache_key)

        # Précharger nouvelles données
        user_data = {
            'organization_id': user.organization.id if hasattr(user, 'organization') else None,
            'role': user.role,
            'permissions': list(user.user_permissions.values_list('codename', flat=True)),
        }

        cache.set(cache_key, user_data, timeout=1800)
        logger.info(f'Cache updated for user {user_id}')

    except User.DoesNotExist:
        logger.error(f'User {user_id} does not exist')

@shared_task
def cleanup_expired_cache():
    """Nettoyer les entrées de cache expirées"""
    from django.core.cache import cache

    if cache.__class__.__name__ == 'RedisCache':
        with cache.client.get_client() as client:
            # Redis gère automatiquement l'expiration
            # Mais on peut forcer un cleanup si nécessaire
            info = client.info('stats')
            logger.info(f'Redis stats: {info}')

@shared_task
def generate_daily_report(organization_id):
    """Générer rapport journalier"""
    from apps.tenants.models import Organization
    from apps.analytics.utils import generate_report

    try:
        org = Organization.objects.get(id=organization_id)
        report = generate_report(org, date=timezone.now().date())

        # Mettre en cache le rapport
        cache_key = f'daily_report:{organization_id}:{timezone.now().date()}'
        cache.set(cache_key, report, timeout=86400)

        logger.info(f'Daily report generated for org {organization_id}')
        return report

    except Organization.DoesNotExist:
        logger.error(f'Organization {organization_id} does not exist')

@shared_task
def process_webhook(event_type, payload):
    """Traiter webhook de manière asynchrone"""
    logger.info(f'Processing webhook: {event_type}')

    if event_type == 'subscription.created':
        # Logique pour nouveau subscription
        pass
    elif event_type == 'payment.succeeded':
        # Logique pour paiement réussi
        pass

    logger.info(f'Webhook {event_type} processed')
```

### 6. Cache Invalidation System

```python
# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .utils import invalidate_cache_pattern

@receiver(post_save)
def invalidate_on_save(sender, instance, **kwargs):
    """Invalider cache quand un objet est sauvegardé"""
    model_name = instance.__class__.__name__.lower()

    # Invalidate cache pour cet objet
    cache.delete(f'{model_name}:{instance.id}')

    # Invalidate listes
    invalidate_cache_pattern(f'{model_name}_list')

@receiver(post_delete)
def invalidate_on_delete(sender, instance, **kwargs):
    """Invalider cache quand un objet est supprimé"""
    model_name = instance.__class__.__name__.lower()

    # Invalidate cache pour cet objet
    cache.delete(f'{model_name}:{instance.id}')

    # Invalidate listes
    invalidate_cache_pattern(f'{model_name}_list')
```

### 7. Monitoring & Metrics

```python
# monitoring/redis_metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Métriques Redis
redis_operations = Counter(
    'redis_operations_total',
    'Total Redis operations',
    ['operation', 'status']
)

redis_latency = Histogram(
    'redis_operation_duration_seconds',
    'Redis operation latency',
    ['operation']
)

redis_memory_usage = Gauge(
    'redis_memory_usage_bytes',
    'Redis memory usage'
)

class RedisMetrics:
    @staticmethod
    def track_operation(operation):
        """Decorator pour tracker les opérations Redis"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start = time.time()
                try:
                    result = func(*args, **kwargs)
                    redis_operations.labels(
                        operation=operation,
                        status='success'
                    ).inc()
                    return result
                except Exception as e:
                    redis_operations.labels(
                        operation=operation,
                        status='error'
                    ).inc()
                    raise e
                finally:
                    latency = time.time() - start
                    redis_latency.labels(operation=operation).observe(latency)
            return wrapper
        return decorator

# Usage
@RedisMetrics.track_operation('cache_get')
def get_from_cache(key):
    return cache.get(key)
```

### 8. Tests

```python
# tests/test_cache.py
from django.test import TestCase, override_settings
from django.core.cache import cache
from apps.core.utils import cache_result

class CacheTest(TestCase):
    def test_cache_decorator(self):
        @cache_result(timeout=60)
        def expensive_function(x):
            return x * 2

        # Premier appel - pas en cache
        result1 = expensive_function(5)
        self.assertEqual(result1, 10)

        # Deuxième appel - depuis cache
        result2 = expensive_function(5)
        self.assertEqual(result2, 10)

    def test_cache_invalidation(self):
        cache.set('test_key', 'test_value')
        self.assertEqual(cache.get('test_key'), 'test_value')

        cache.delete('test_key')
        self.assertIsNone(cache.get('test_key'))

    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
        }
    })
    def test_cache_operations(self):
        cache.set('key', 'value', timeout=10)
        self.assertTrue(cache.has_key('key'))
        self.assertEqual(cache.get('key'), 'value')
```

### 9. Management Commands

```python
# management/commands/flush_cache.py
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Flush all cache'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pattern',
            type=str,
            help='Flush keys matching pattern'
        )

    def handle(self, *args, **options):
        from django.core.cache import cache

        if options['pattern']:
            # Flush pattern
            from apps.core.utils import invalidate_cache_pattern
            invalidate_cache_pattern(options['pattern'])
            self.stdout.write(
                self.style.SUCCESS(f'Flushed cache for pattern: {options["pattern"]}')
            )
        else:
            # Flush all
            cache.clear()
            self.stdout.write(
                self.style.SUCCESS('All cache flushed')
            )
```

## Performance Optimizations

### Cache Strategy
- **Nested caching** pour hiérarchie de données
- **Cache warming** au démarrage
- **Cache backpressure** pour éviter overflow
- **Lazy loading** avec mise en cache différée

### Redis Optimization
- **Pipeline** pour operations multiples
- **Transactions** pour atomicité
- **Pub/Sub** pour realtime updates
- **Lua scripts** pour operations complexes

Configurez Redis pour un SaaS scalable en quelques minutes ! ⚡
