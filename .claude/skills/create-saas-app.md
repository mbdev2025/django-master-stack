---
name: create-saas-app
description: Créer une nouvelle application Django SaaS complète avec models, views, serializers, URLs, admin et tests
---

# Skill: Create SaaS App

Ce skill crée une nouvelle application Django SaaS complète avec toute la structure nécessaire.

## Utilisation

```
/create-saas-app <app_name> [options]
```

## Options

- `--models`: Créer les modèles spécifiés (ex: `--models Product,Order,Invoice`)
- `--api-only`: Créer seulement l'API REST (sans templates)
- `--tests`: Générer les tests automatiquement
- `--permissions`: Ajouter les systèmes de permissions (RBAC)

## Ce que le skill génère

### 1. Structure Django complète
- `apps/<app_name>/models.py` avec modèles optimisés
- `apps/<app_name>/views.py` avec ViewSets REST Framework
- `apps/<app_name>/serializers.py` avec sérialiseurs complets
- `apps/<app_name>/urls.py` avec routes API
- `apps/<app_name>/admin.py` avec interface admin
- `apps/<app_name>/filters.py` avec filtres Django-filter

### 2. Fonctionnalités SaaS incluses
- Multi-tenancy support (Organization, Team)
- Permissions RBAC (Role-Based Access Control)
- Timestamps automatiques (created_at, updated_at)
- Soft delete (is_active)
- Audit trail (created_by, updated_by)

### 3. Tests automatisés
- Tests unitaires pour modèles
- Tests d'intégration pour API
- Tests de permissions
- Fixtures Factory Boy

### 4. Documentation
- OpenAPI/Swagger via drf-spectacular
- Docstrings Google style
- Examples dans les sérialiseurs

## Exemple d'utilisation

```bash
# Créer une app de gestion de produits
/create-saas-app products --models Product,Category,Review --tests

# Créer une app API only
/create-saas-app notifications --api-only --permissions
```

## Intégration avec la stack existante

Le skill intègre automatiquement la nouvelle app avec:
- Système d'authentification JWT existant
- Modèle Organization pour multi-tenancy
- Système de notifications
- Logging structuré

## Fichiers générés

```
apps/<app_name>/
├── __init__.py
├── apps.py
├── models.py          # Modèles avec champs SaaS
├── views.py           # ViewSets avec permissions
├── serializers.py     # Sérialiseurs REST
├── urls.py            # Routes API
├── filters.py         # Filtres de recherche
├── admin.py           # Interface admin
├── permissions.py     # Permissions personnalisées
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_views.py
    └── factories.py   # Factory Boy fixtures
```

## Patterns utilisés

### Modèle avec multi-tenancy
```python
class Product(models.Model):
    organization = models.ForeignKey('tenants.Organization', ...)
    created_by = models.ForeignKey('users.User', ...)
    # ... autres champs
```

### ViewSet avec permissions
```python
class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    def get_queryset(self):
        return Product.objects.filter(
            organization__members__user=self.request.user
        )
```

### Sérialiseur avec validation
```python
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['organization', 'created_by']
```

## Commandes Django générées

```bash
# Lancer les migrations
python manage.py makemigrations <app_name>
python manage.py migrate

# Lancer les tests
pytest apps/<app_name>/tests/

# Voir la documentation API
# Ouvrir http://localhost:8000/api/schema/
```
