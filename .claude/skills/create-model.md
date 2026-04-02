---
name: create-model
description: Génère automatiquement des modèles Django optimisés SaaS avec migrations, admin, serializers, factories
---

# Skill: Create Model

Génère instantanément un modèle Django SaaS-ready avec toute la structure nécessaire.

## Utilisation

```
/create-model <ModelName> [fields]
```

## Exemples

```bash
# Modèle simple
/create-model Product name:string price:decimal description:text category:fk:Category

# Modèle SaaS complet
/create-model Subscription organization:fk:Organization user:fk:User plan:choices:STARTER,PRO,ENTERPRISE status:choices:ACTIVE,CANCELLED,EXPIRED start_date:date end_date:date is_active:boolean

# Modèle avec relations
/create-model Order customer:fk:User items:mk:OrderItem total:decimal status:choices:PENDING,PAID,SHIPPED,REFUNDED created_at:datetime updated_at:datetime
```

## Syntaxe des Champs

```
field_name:type:options

Types:
- string      -> CharField
- text        -> TextField
- integer     -> IntegerField
- decimal     -> DecimalField(max_digits=10, decimal_places=2)
- boolean     -> BooleanField(default=True)
- date        -> DateField
- datetime    -> DateTimeField(auto_now_add=True)
- email       -> EmailField
- url         -> URLField
- image       -> ImageField(upload_to=...)
- file        -> FileField(upload_to=...)
- fk:Model    -> ForeignKey(Model, on_delete=CASCADE)
- m2m:Model   -> ManyToManyField(Model)
- mk:Model    -> Model inverse relation
- json        -> JSONField()
- slug        -> SlugField(unique=True)
- choices:VAL1,VAL2,VAL3 -> CharField with choices
```

## Ce qui est généré automatiquement

### 1. Model Django complet
```python
class Product(models.Model):
    # Vos champs personnalisés
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # Champs SaaS automatiques
    organization = models.ForeignKey('tenants.Organization', ...)
    created_by = models.ForeignKey('users.User', ...)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [...]  # Indexes optimisés
        ordering = ['-created_at']
```

### 2. Admin Interface
```python
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [...]
    list_filter = [...]
    search_fields = [...]
    date_hierarchy = 'created_at'
```

### 3. Serializers
```python
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['organization', 'created_by']

class ProductCreateSerializer(serializers.ModelSerializer):
    # Validation personnalisée
```

### 4. ViewSets
```python
class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    filterset_class = ProductFilter

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user
        )
```

### 5. Filters
```python
class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
```

### 6. Factories (tests)
```python
class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Faker('sentence')
    price = factory.Faker('pyfloat', left_digits=3, right_digits=2)
```

### 7. Tests
```python
class ProductModelTest(TestCase):
    def test_create_product(self): ...

class ProductAPITest(APITestCase):
    def test_list_products(self): ...
```

### 8. Migrations
```bash
python manage.py makemigrations <app_label>
python manage.py migrate
```

## Patterns SaaS Inclus

### Multi-tenancy automatique
```python
# Tous les modèles sont automatiquement scoped par organization
def get_queryset(self):
    return Product.objects.filter(
        organization__members__user=self.request.user
    )
```

### Audit trail
```python
# Tracking automatique des créateurs/modificateurs
created_by = models.ForeignKey('users.User', ...)
updated_by = models.ForeignKey('users.User', ...)
```

### Soft delete
```python
# Suppression logique
is_active = models.BooleanField(default=True)
# Les objets ne sont jamais vraiment supprimés
```

### Permissions automatiques
```python
# Seuls les members de l'organization peuvent accéder
permission_classes = [IsAuthenticated, IsOrganizationMember]
```

## Templates de Modèles SaaS

### E-commerce
```bash
/create-model Product name price:decimal description:image category:fk stock:int
/create-model Order customer:fk:User status:choices total:decimal items:mk:OrderItem
/create-model OrderItem product:fk quantity:int price:decimal
```

### CRM
```bash
/create-model Lead company:contact_name email phone status:choices value:decimal
/create-model Deal lead:fk stage:choices amount:decimal close_date:date
/create-model Activity deal:fk type:choices notes:text date:datetime
```

### Project Management
```bash
/create-model Project name description:text status:choices start_date:end_date: team:mk
/create-model Task project:fk title assignee:fk status:choices priority:choices due_date:date
/create-model Comment task:fk content:text created_by:fk
```

### Help Desk
```bash
/create-model Ticket customer:fk subject priority:choices status:choices body:text
/create-model Message ticket:fk sender:fk content:text sent_at:datetime
/create-model Category name parent:fk self
```

### Booking/Reservation
```bash
/create-model Booking user:fk start:datetime end:datetime status:choices
/create-model Resource name:type:choices capacity:int price_per_hour:decimal
/create-model Availability resource:fk day:date slots:json
```

### Content Management
```bash
/create-model Page title slug content:text status:choices
/create-model Post page:fk title content:published_at author:fk
/create-model Media file original_filename mime_type size:int
```

## Commandes Rapides

```bash
# Créer un modèle avec tous les champs SaaS
/create-model Invoice organization:fk customer:fk total:decimal status:choices issued:date

# Créer plusieurs modèles liés
/create-model Category name slug parent:fk:self
/create-model Product category:fk name price:decimal
/create-model Review product:fk user:fk rating:int content:text
```

## Intégration avec /create-saas-app

Après avoir créé vos modèles avec `/create-model`, utilisez:

```bash
/create-saas-app products --use-existing-models
```

Cela générera automatiquement toute l'API complète basée sur vos modèles !

## Validation & Tests

```bash
# Tester le modèle immédiatement
pytest apps/products/tests/test_models.py -v

# Vérifier les migrations
python manage.py makemigrations --dry-run

# Admin interface
http://localhost:8000/admin/products/product/
```

## Performance Optimizations

Les modèles générés incluent:
- **Database indexes** sur les champs fréquemment recherchés
- **select_related** pour les ForeignKeys
- **prefetch_related** pour les ManyToMany
- **QuerySet optimization** pour éviter N+1 queries

## Documentation Auto-Générée

Champs avec docstrings complètes:
```python
name = models.CharField(
    max_length=200,
    help_text="Le nom du produit (affiché dans les listings)",
    verbose_name="Nom du produit"
)
```

## Champs Spéciaux SaaS

```bash
# Auto-generated UUID
/create-model Document uuid:uuid file:field title organization:fk

# Geo-localisation
/create-model Location latitude:decimal longitude:decimal address:text

# Multi-langue
/create-model Article title:ml:text content:ml:text language:choices:FR,EN,ES

# Versioning
/create-model Document content:text version:int parent:fk:self
```

Créez des modèles Django SaaS-parfaits en quelques secondes ! 🚀
