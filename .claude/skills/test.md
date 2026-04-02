---
name: test
description: Tests intelligents pour Django SaaS avec génération automatique, coverage et E2E
---

# Skill: Test

Ce skill génère et gère les tests pour l'application Django SaaS.

## Utilisation

```
/test [commande] [options]
```

## Commandes

### `generate`
Génère des tests complets pour une app

```bash
/test generate <app_name> [--with-factories] [--with-e2e]
```

**Options:**
- `--with-factories`: Génère les fixtures Factory Boy
- `--with-e2e`: Génère les tests end-to-end avec Playwright
- `--coverage`: Ajoute les marqueurs de coverage

### `run`
Exécute les tests avec différentes options

```bash
/test run [--unit] [--integration] [--e2e] [--coverage]
```

**Options:**
- `--unit`: Tests unitaires seulement
- `--integration`: Tests d'intégration seulement
- `--e2e`: Tests end-to-end seulement
- `--coverage`: Génère le rapport de coverage

### `watch`
Mode watch pour le développement

```bash
/test watch
```

Relance les tests automatiquement quand les fichiers changent.

### `coverage`
Génère un rapport de coverage détaillé

```bash
/test coverage [--html] [--xml]
```

## Types de tests générés

### 1. Tests unitaires
Tests isolés pour chaque composant:

```python
# test_models.py
class ProductModelTest(TestCase):
    def test_create_product(self):
        product = Product.objects.create(
            name="Test Product",
            price=99.99
        )
        self.assertEqual(product.name, "Test Product")

    def test_product_slug_generation(self):
        product = Product.objects.create(
            name="Test Product"
        )
        self.assertEqual(product.slug, "test-product")
```

### 2. Tests d'intégration
Tests des interactions entre composants:

```python
# test_views.py
class ProductAPITestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

    def test_list_products(self):
        ProductFactory.create_batch(10)
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 10)

    def test_create_product_requires_auth(self):
        response = self.client.post('/api/products/', {
            'name': 'New Product'
        })
        self.assertEqual(response.status_code, 401)
```

### 3. Tests E2E
Tests complets avec Playwright:

```python
# test_e2e.py
class ProductE2ETest(PlaywrightTestCase):
    async def test_product_creation_flow(self):
        # Login
        await self.page.goto("http://localhost:8000/login")
        await self.page.fill("input[name='email']", "user@example.com")
        await self.page.fill("input[name='password']", "password")
        await self.page.click("button[type='submit']")

        # Navigate to products
        await self.page.click("text=Products")
        await self.page.wait_for_url("**/products**")

        # Create product
        await self.page.click("text=New Product")
        await self.page.fill("input[name='name']", "E2E Test Product")
        await self.page.click("button[type='submit']")

        # Verify creation
        await self.page.wait_for_selector("text=E2E Test Product")
        assert await self.page.content().__contains__("E2E Test Product")
```

### 4. Tests de permissions
Tests du système RBAC:

```python
# test_permissions.py
class ProductPermissionsTest(TestCase):
    def test_only_org_members_can_access(self):
        product = ProductFactory()
        non_member = UserFactory()

        self.client.force_authenticate(user=non_member)
        response = self.client.get(f'/api/products/{product.id}/')
        self.assertEqual(response.status_code, 404)

    def test_admin_can_access_all_products(self):
        product = ProductFactory()
        admin = UserFactory(role='admin')

        self.client.force_authenticate(user=admin)
        response = self.client.get(f'/api/products/{product.id}/')
        self.assertEqual(response.status_code, 200)
```

## Fixtures Factory Boy

Génère des factories pour les tests:

```python
# factories.py
class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    role = 'user'

class OrganizationFactory(DjangoModelFactory):
    class Meta:
        model = Organization

    name = factory.Faker('company')
    slug = factory.LazyAttribute(lambda obj: slugify(obj.name))

class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Faker('sentence', nb_words=3)
    price = factory.Faker('pyfloat', left_digits=3, right_digits=2, positive=True)
    organization = factory.SubFactory(OrganizationFactory)
```

## Structure des tests

```
apps/<app_name>/tests/
├── __init__.py
├── factories.py          # Fixtures Factory Boy
├── test_models.py        # Tests des modèles
├── test_views.py         # Tests des ViewSets
├── test_serializers.py   # Tests des sérialiseurs
├── test_permissions.py   # Tests des permissions
├── test_filters.py       # Tests des filtres
├── conftest.py           # Fixtures pytest
└── e2e/
    ├── __init__.py
    └── test_flows.py     # Tests E2E Playwright
```

## Commandes pytest

```bash
# Tous les tests
pytest

# Une app spécifique
pytest apps/products/tests/

# Tests unitaires seulement
pytest -m unit

# Tests avec coverage
pytest --cov=apps.products --cov-report=html

# Tests parallèles (plus rapide)
pytest -n auto

# Tests avec debugging
pytest -vv -s

# Tests qui échouent uniquement
pytest --lf

# Tests avec marqueurs
pytest -m "not slow"
```

## Configuration pytest

```python
# conftest.py
import pytest
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

@pytest.fixture
def authenticated_user(db):
    User = get_user_model()
    return User.objects.create_user(
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def api_client(authenticated_user):
    from rest_framework.test import APIClient
    client = APIClient()
    client.force_authenticate(user=authenticated_user)
    return client

@pytest.fixture
def organization(db, authenticated_user):
    from apps.tenants.factories import OrganizationFactory
    org = OrganizationFactory()
    org.members.create(user=authenticated_user, role='owner')
    return org
```

## Coverage

### Objectifs de coverage
- **Models**: 100%
- **Views**: 95%+
- **Serializers**: 90%+
- **Permissions**: 100%
- **Global**: 85%+

### Rapports générés
- **HTML**: `htmlcov/index.html`
- **XML**: `coverage.xml` (pour CI/CD)
- **Terminal**: Résumé dans la console

## Marqueurs pytest

```python
# tests marqués
@pytest.mark.unit
def test_model_method():
    pass

@pytest.mark.integration
def test_api_endpoint():
    pass

@pytest.mark.slow
def test_heavy_computation():
    pass

@pytest.mark.e2e
async def test_user_flow():
    pass
```

## Performance des tests

```bash
# Profiling des tests lents
pytest --durations=10

# Tests parallèles (4 workers)
pytest -n 4

# Tests optimisés pour la vitesse
--dist=loadscope  # Distribue par classe de test
```

## CI/CD Integration

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: |
    pytest --cov=. --cov-report=xml --cov-report=html

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v2
  with:
    files: ./coverage.xml
```

## Mocking & Fixtures avancés

```python
# Mock API externe
@patch('apps.products.services.stripe_api.create_product')
def test_product_creation_with_stripe(mock_stripe):
    mock_stripe.return_value = {'id': 'stripe_123'}
    # ... test

# Fake temps
@freeze_time("2024-01-01")
def test_new_year_promotion():
    # ... test

# Fake fichiers
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_image_upload():
    # ... test
```

## Tests de charge

```python
# test_load.py
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Login
        self.client.post("/api/auth/login/", {
            "email": "test@example.com",
            "password": "testpass"
        })

    @task(3)
    def view_products(self):
        self.client.get("/api/products/")

    @task(1)
    def create_product(self):
        self.client.post("/api/products/", {
            "name": "Load Test Product"
        })
```

Lancer avec: `locust -f test_load.py --host=http://localhost:8000`
