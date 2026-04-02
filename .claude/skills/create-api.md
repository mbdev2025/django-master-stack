---
name: create-api
description: Génère instantanément une API REST complète avec ViewSets, Serializers, Permissions, Tests, Documentation
---

# Skill: Create API

Crée instantanément une API REST Django complète et production-ready pour vos modèles existants.

## Utilisation

```
/create-api <ModelName> [options]
```

## Exemples

```bash
# API complète pour un modèle
/create-api Product

# API avec options spécifiques
/create-api Order --permissions --filters --docs

# API pour plusieurs modèles
/create-api Product,Category,Review --full

# API avec custom endpoints
/create-api Subscription --custom-actions:activate,cancel,upgrade
```

## Options

- `--full`: API complète avec toutes les fonctionnalités
- `--permissions`: Ajoute permissions RBAC détaillées
- `--filters`: Filtres de recherche avancés
- `--docs`: Documentation OpenAPI complète
- `--tests`: Tests d'API automatisés
- `--actions`: Actions custom (bulk, export, etc.)
- `--nested`: Nested routes pour les relations
- `--bulk`: Bulk operations (create, update, delete)
- `--export`: Export functionality (CSV, Excel, PDF)

## Ce qui est généré

### 1. ViewSets Complets

```python
class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint pour les produits
    - List avec pagination et filtres
    - Create avec validation
    - Retrieve par ID ou slug
    - Update partiel ou complet
    - Delete avec soft-delete
    """
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_class = ProductFilter
    lookup_field = 'pk'

    def get_queryset(self):
        return Product.objects.filter(
            organization__members__user=self.request.user
        ).select_related('category')

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            organization=self.request.user.organization
        )
```

### 2. Serializers Multiples

```python
# List serializer (optimisé)
class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name')
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category_name']

# Detail serializer (complet)
class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    created_by = UserSerializer()
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

# Create/Update serializer
class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'category']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le prix doit être positif")
        return value
```

### 3. Permissions SaaS

```python
# Organization-based permissions
class IsOrganizationMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.organization.members.filter(
            user=request.user
        ).exists()

# Role-based permissions
class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user or \
               request.user.role in ['admin', 'manager']
```

### 4. Filtres Avancés

```python
class ProductFilter(django_filters.FilterSet):
    # Recherche textuelle
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')

    # Filtres numériques
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    # Filtres par relation
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all())
    category_name = django_filters.CharFilter(field_name='category__name')

    # Filtres par date
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    # Filtres boolean
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Product
        fields = ['name', 'price', 'category', 'is_active']
```

### 5. Custom Actions

```python
@action(detail=True, methods=['post'])
def duplicate(self, request, pk=None):
    """Dupliquer un produit"""
    product = self.get_object()
    new_product = product
    new_product.pk = None
    new_product.name = f"{product.name} (copie)"
    new_product.save()
    serializer = self.get_serializer(new_product)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@action(detail=False, methods=['get'])
def featured(self, request):
    """Produits en vedette"""
    featured = Product.objects.filter(is_featured=True)[:10]
    serializer = self.get_serializer(featured, many=True)
    return Response(serializer.data)

@action(detail=True, methods=['post'])
def archive(self, request, pk=None):
    """Archiver un produit"""
    product = self.get_object()
    product.is_active = False
    product.save()
    return Response({'status': 'archivé'})

@action(detail=False, methods=['post'])
def bulk_delete(self, request):
    """Suppression en masse"""
    ids = request.data.get('ids', [])
    Product.objects.filter(id__in=ids).delete()
    return Response({'status': f'{len(ids)} produits supprimés'})
```

### 6. Tests Automatisés

```python
class ProductAPITest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

    def test_list_products(self):
        ProductFactory.create_batch(10)
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 10)

    def test_create_product(self):
        response = self.client.post('/api/products/', {
            'name': 'Test Product',
            'price': '99.99'
        })
        self.assertEqual(response.status_code, 201)

    def test_update_product(self):
        product = ProductFactory()
        response = self.client.patch(f'/api/products/{product.id}/', {
            'name': 'Updated Name'
        })
        self.assertEqual(response.status_code, 200)

    def test_delete_product(self):
        product = ProductFactory()
        response = self.client.delete(f'/api/products/{product.id}/')
        self.assertEqual(response.status_code, 204)

    def test_filters(self):
        ProductFactory(name='Cheap', price=10)
        ProductFactory(name='Expensive', price=1000)
        response = self.client.get('/api/products/?price_min=50')
        self.assertEqual(len(response.data['results']), 1)

    def test_permissions(self):
        other_user = UserFactory()
        product = ProductFactory(created_by=other_user)
        response = self.client.patch(f'/api/products/{product.id}/', {
            'name': 'Hacked'
        })
        self.assertEqual(response.status_code, 403)
```

### 7. Documentation OpenAPI

```python
# Tags et descriptions automatiques
@extend_schema(
    tags=['Products'],
    summary='Lister tous les produits',
    description='Retourne la liste des produits de l\'organization avec pagination et filtres',
    responses={200: ProductListSerializer(many=True)}
)
def list(self, request, *args, **kwargs):
    return super().list(request, *args, **kwargs)

@extend_schema(
    tags=['Products'],
    summary='Créer un nouveau produit',
    request=ProductCreateSerializer,
    responses={201: ProductDetailSerializer}
)
def create(self, request, *args, **kwargs):
    return super().create(request, *args, **kwargs)
```

### 8. URLs & Routes

```python
# Router principal
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

# Routes générées
GET    /api/products/                    # Liste des produits
POST   /api/products/                    # Créer un produit
GET    /api/products/{id}/               # Détails produit
PUT    /api/products/{id}/               # Update complet
PATCH  /api/products/{id}/               # Update partiel
DELETE /api/products/{id}/               # Supprimer produit

# Custom actions
POST   /api/products/{id}/duplicate/     # Dupliquer
POST   /api/products/{id}/archive/       # Archiver
GET    /api/products/featured/           # Vedette
POST   /api/products/bulk_delete/        # Suppression masse
```

## Types d'API Générés

### CRUD Standard
```bash
/create-api Product
```

### Nested Routes
```bash
/create-api Comment --nested
# GET /api/posts/{post_id}/comments/
# POST /api/posts/{post_id}/comments/
```

### Bulk Operations
```bash
/create-api Product --bulk
# POST /api/products/bulk_create/
# PUT /api/products/bulk_update/
# DELETE /api/products/bulk_delete/
```

### Export Functionality
```bash
/create-api Product --export
# GET /api/products/export/csv/
# GET /api/products/export/excel/
# GET /api/products/export/pdf/
```

## API Patterns Prédéfinis

### E-commerce API
```bash
/create-api Product,Category,Review,Order --full --export
```

### CRM API
```bash
/create-api Lead,Deal,Activity --permissions --filters
```

### Project Management API
```bash
/create-api Project,Task,Comment --actions --nested
```

### Help Desk API
```bash
/create-api Ticket,Message,Category --full --bulk
```

## Performance Optimizations

Les ViewSets générés incluent:
- **select_related** pour optimiser les ForeignKeys
- **prefetch_related** pour optimiser les ManyToMany
- **only()** et **defer()** pour charger seulement les champs nécessaires
- **QuerySet caching** pour les listes fréquemment accédées

## Intégration Frontend

Documentation JSON automatique pour les teams frontend:
```bash
# GET /api/schema/
{
  "openapi": "3.0.0",
  "info": {...},
  "paths": {
    "/api/products/": {...}
  }
}
```

Créez des API REST production-ready en quelques secondes ! 🚀
