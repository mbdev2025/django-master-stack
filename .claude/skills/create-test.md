---
name: create-test
description: Génère automatiquement des tests complets (unitaires, intégration, E2E) avec coverage et fixtures
---

# Skill: Create Test

Génère instantanément des tests professionnels pour vos modèles et API Django.

## Utilisation

```
/create-test <ModelName> [options]
```

## Exemples

```bash
# Tests complets pour un modèle
/create-test Product

# Tests avec options spécifiques
/create-test Order --with-factory --with-e2e

# Tests pour plusieurs modèles
/create-test Product,Category,Review --full

# Tests avec scénarios spécifiques
/create-test Subscription --scenarios:trial,upgrade,cancel,refund
```

## Options

- `--unit`: Tests unitaires seulement
- `--integration`: Tests d'intégration seulement
- `--e2e`: Tests end-to-end avec Playwright
- `--with-factory`: Génère fixtures Factory Boy
- `--with-mock`: Ajoute mocks pour APIs externes
- `--coverage`: Ajoute marqueurs de coverage
- `--performance`: Tests de performance
- `--scenarios:liste`: Tests scénarios métier

## Ce qui est généré

### 1. Tests Unitaires Modèles

```python
# tests/test_models.py
from django.test import TestCase
from apps.products.factories import ProductFactory, CategoryFactory
from apps.products.models import Product

class ProductModelTest(TestCase):
    def setUp(self):
        self.category = CategoryFactory(name="Électronique")
        self.product = ProductFactory(
            name="iPhone 15",
            price=999.99,
            category=self.category
        )

    def test_create_product(self):
        """Test création produit"""
        self.assertEqual(self.product.name, "iPhone 15")
        self.assertEqual(self.product.price, 999.99)
        self.assertTrue(self.product.is_active)

    def test_product_slug_generation(self):
        """Test génération automatique slug"""
        self.assertEqual(self.product.slug, "iphone-15")

    def test_product_category_relation(self):
        """Test relation avec catégorie"""
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.category.name, "Électronique")

    def test_product_str_method(self):
        """Test méthode __str__"""
        self.assertEqual(str(self.product), "iPhone 15")

    def test_product_soft_delete(self):
        """Test soft delete"""
        product_id = self.product.id
        self.product.is_active = False
        self.product.save()

        # Le produit existe toujours en base
        self.assertTrue(Product.objects.filter(id=product_id).exists())
        # Mais n'est pas actif
        self.assertFalse(Product.objects.get(id=product_id).is_active)

    def test_product_organization_scoping(self):
        """Test scoping par organization"""
        from apps.tenants.factories import OrganizationFactory
        from apps.users.factories import UserFactory

        org1 = OrganizationFactory()
        org2 = OrganizationFactory()

        product1 = ProductFactory(organization=org1)
        product2 = ProductFactory(organization=org2)

        # Chaque org ne voit que ses produits
        org1_products = Product.objects.filter(organization=org1)
        org2_products = Product.objects.filter(organization=org2)

        self.assertIn(product1, org1_products)
        self.assertNotIn(product2, org1_products)
```

### 2. Tests d'Intégration API

```python
# tests/test_views.py
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.products.factories import ProductFactory, CategoryFactory
from apps.users.factories import UserFactory
from apps.tenants.factories import OrganizationFactory

class ProductAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory(email='user@example.com')
        self.organization = OrganizationFactory()
        self.organization.members.create(
            user=self.user,
            role='admin'
        )
        self.client.force_authenticate(user=self.user)

        self.category = CategoryFactory()
        self.product = ProductFactory(
            name="Test Product",
            price=99.99,
            category=self.category,
            organization=self.organization
        )

    def test_list_products(self):
        """Test listing des produits"""
        ProductFactory.create_batch(10, organization=self.organization)

        response = self.client.get('/api/products/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 11)  # 10 + 1 du setUp

    def test_create_product(self):
        """Test création produit"""
        data = {
            'name': 'Nouveau Produit',
            'price': '149.99',
            'category': self.category.id,
            'description': 'Super produit'
        }

        response = self.client.post('/api/products/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Nouveau Produit')
        self.assertEqual(response.data['price'], '149.99')

    def test_retrieve_product(self):
        """Test récupération produit"""
        response = self.client.get(f'/api/products/{self.product.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')

    def test_update_product(self):
        """Test mise à jour produit"""
        data = {'name': 'Produit Modifié'}

        response = self.client.patch(
            f'/api/products/{self.product.id}/',
            data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Produit Modifié')

    def test_delete_product(self):
        """Test suppression produit"""
        response = self.client.delete(f'/api/products/{self.product.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Vérifier soft delete
        self.product.refresh_from_db()
        self.assertFalse(self.product.is_active)

    def test_product_filters(self):
        """Test filtres produits"""
        ProductFactory(name="Cheap", price=10, organization=self.organization)
        ProductFactory(name="Expensive", price=1000, organization=self.organization)

        # Filtre prix min
        response = self.client.get('/api/products/?price_min=50')
        self.assertEqual(len(response.data['results']), 2)  # product + Expensive

        # Filtre prix max
        response = self.client.get('/api/products/?price_max=100')
        self.assertEqual(len(response.data['results']), 2)  # product + Cheap

        # Recherche
        response = self.client.get('/api/products/?search=Cheap')
        self.assertEqual(len(response.data['results']), 1)

    def test_product_permissions(self):
        """Test permissions produits"""
        other_user = UserFactory(email='other@example.com')
        other_org = OrganizationFactory()
        other_org.members.create(user=other_user, role='admin')

        other_product = ProductFactory(organization=other_org)

        # L'utilisateur ne peut pas voir les produits d'autres orgs
        response = self.client.get(f'/api/products/{other_product.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_product_validation(self):
        """Test validation produit"""
        data = {
            'name': '',  # Vide
            'price': '-10',  # Négatif
        }

        response = self.client.post('/api/products/', data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('price', response.data)

    def test_product_pagination(self):
        """Test pagination produits"""
        ProductFactory.create_batch(30, organization=self.organization)

        response = self.client.get('/api/products/?page=1&page_size=10')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertIsNotNone(response.data['next'])
```

### 3. Factories Factory Boy

```python
# factories.py
import factory
from factory import fuzzy
from apps.products.models import Product, Category
from apps.users.models import User
from apps.tenants.models import Organization

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    role = 'user'

class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organization

    name = factory.Faker('company')
    slug = factory.LazyAttribute(lambda obj: slugify(obj.name))
    industry = factory.Iterator(['Tech', 'Finance', 'Healthcare'])

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Iterator(['Électronique', 'Vêtements', 'Alimentation'])
    slug = factory.LazyAttribute(lambda obj: slugify(obj.name))

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Faker('sentence', nb_words=3)
    slug = factory.LazyAttribute(lambda obj: slugify(obj.name))
    description = factory.Faker('text', max_nb_chars=200)
    price = fuzzy.FuzzyDecimal(10, 1000, 2)
    is_active = True
    stock = fuzzy.FuzzyInteger(0, 100)

    category = factory.SubFactory(CategoryFactory)
    organization = factory.SubFactory(OrganizationFactory)
    created_by = factory.SubFactory(UserFactory)
```

### 4. Tests E2E avec Playwright

```python
# tests_e2e/test_user_flow.py
from playwright.sync_api import Page, expect
from apps.users.factories import UserFactory
from apps.products.factories import ProductFactory

class TestUserFlow:
    def test_login_and_view_products(self, page: Page):
        """Test flux: login → voir produits"""
        # Créer user
        user = UserFactory(email='test@example.com', password='testpass123')
        ProductFactory.create_batch(5, organization=user.organization)

        # Aller à la page login
        page.goto("http://localhost:3000/login")

        # Remplir formulaire
        page.fill("input[name='email']", "test@example.com")
        page.fill("input[name='password']", "testpass123")
        page.click("button[type='submit']")

        # Vérifier redirection dashboard
        expect(page).to_have_url("http://localhost:3000/dashboard")

        # Cliquer sur Produits
        page.click("text=Produits")

        # Vérifier affichage produits
        products = page.locator(".product-card")
        expect(products).to_have_count(5)

    def test_create_product_flow(self, page: Page):
        """Test flux: créer produit"""
        user = UserFactory(email='admin@example.com', password='admin123')
        page.goto("http://localhost:3000/login")
        page.login_as(user)

        # Aller à page création produit
        page.click("text=Nouveau Produit")
        expect(page).to_have_url("http://localhost:3000/products/new")

        # Remplir formulaire
        page.fill("input[name='name']", "Produit Test")
        page.fill("input[name='price']", "99.99")
        page.fill("textarea[name='description']", "Description test")
        page.select_option("select[name='category']", "1")

        # Soumettre
        page.click("button[type='submit']")

        # Vérifier succès
        expect(page).to_have_url("http://localhost:3000/products")
        expect(page.locator("text=Produit Test")).to_be_visible()

    def test_product_filters(self, page: Page):
        """Test filtres produits"""
        user = UserFactory()
        ProductFactory(name="Cheap", price=10, organization=user.organization)
        ProductFactory(name="Expensive", price=1000, organization=user.organization)

        page.goto("http://localhost:3000/products")

        # Filtre prix
        page.fill("input[name='price_min']", "50")
        page.click("button[type='submit']")

        # Vérifier résultat
        products = page.locator(".product-card")
        expect(products).to_have_count(1)
        expect(page.locator("text=Expensive")).to_be_visible()
```

### 5. Tests de Performance

```python
# tests/test_performance.py
from django.test import TestCase
from django.db import connection
from django.test.utils import override_settings
from apps.products.factories import ProductFactory
from apps.users.factories import UserFactory

class ProductPerformanceTest(TestCase):
    def test_list_query_performance(self):
        """Test performance listing produits"""
        user = UserFactory()
        ProductFactory.create_batch(100, organization=user.organization)

        with self.assertNumQueries(2):  # 1 query pour produits, 1 pour count
            response = self.client.get('/api/products/')

        self.assertEqual(len(response.data['results']), 20)  # page_size

    def test_select_related_optimization(self):
        """Test optimisation select_related"""
        from apps.products.models import Product

        # Sans select_related = N queries
        products = Product.objects.all()[:10]
        with self.assertNumQueries(11):  # 1 + 10 pour les catégories
            for product in products:
                _ = product.category.name

        # Avec select_related = 1 query
        products = Product.objects.select_related('category')[:10]
        with self.assertNumQueries(1):
            for product in products:
                _ = product.category.name

    @override_settings(DEBUG=True)
    def test_no_n_plus_one_queries(self):
        """Test absence N+1 queries"""
        user = UserFactory()
        ProductFactory.create_batch(20, organization=user.organization)

        from django.db import reset_queries
        reset_queries()

        response = self.client.get('/api/products/')

        # Vérifier nombre de queries
        queries = len(connection.queries)
        self.assertLess(queries, 5, f"Trop de queries: {queries}")

    def test_bulk_create_performance(self):
        """Test performance bulk create"""
        from apps.products.models import Product

        # Bulk create = 1 query
        products_data = [
            ProductFactory.build() for _ in range(100)
        ]
        with self.assertNumQueries(1):
            Product.objects.bulk_create(products_data)

        # Create individuel = 100 queries
        with self.assertNumQueries(100):
            for product_data in products_data:
                ProductFactory.create(**product_data)
```

### 6. Tests de Scénarios Métier

```python
# tests/test_scenarios.py
from django.test import TestCase
from apps.subscriptions.factories import SubscriptionFactory
from apps.users.factories import UserFactory

class SubscriptionScenarioTest(TestCase):
    def test_trial_to_paid_conversion(self):
        """Test scénario: essai → abonnement payant"""
        user = UserFactory()

        # Créer abonnement trial
        trial = SubscriptionFactory(
            user=user,
            plan='TRIAL',
            status='active',
            trial_end=timezone.now() + timezone.timedelta(days=14)
        )

        # Simuler fin du trial
        trial.trial_end = timezone.now() - timezone.timedelta(days=1)
        trial.save()

        # Appeler tâche de conversion
        from apps.subscriptions.tasks import convert_trial_to_paid
        convert_trial_to_paid()

        # Vérifier conversion
        trial.refresh_from_db()
        self.assertEqual(trial.plan, 'BASIC')
        self.assertEqual(trial.status, 'active')

    def test_subscription_upgrade_flow(self):
        """Test scénario: upgrade abonnement"""
        user = UserFactory()
        subscription = SubscriptionFactory(
            user=user,
            plan='BASIC',
            status='active'
        )

        # Upgrade vers PRO
        subscription.upgrade('PRO')

        self.assertEqual(subscription.plan, 'PRO')
        self.assertTrue(subscription.is_active())

        # Vérifier facture générée
        self.assertEqual(
            subscription.invoices.filter(type='upgrade').count(),
            1
        )

    def test_subscription_cancellation(self):
        """Test scénario: annulation abonnement"""
        user = UserFactory()
        subscription = SubscriptionFactory(
            user=user,
            plan='PRO',
            status='active'
        )

        # Annuler immédiatement
        subscription.cancel(immediate=True)

        self.assertEqual(subscription.status, 'cancelled')
        self.assertFalse(subscription.is_active())

        # Vérifier prorata calculé
        self.assertIsNotNone(subscription.refund_amount)
```

### 7. Pytest Fixtures

```python
# conftest.py
import pytest
from apps.users.factories import UserFactory
from apps.tenants.factories import OrganizationFactory

@pytest.fixture
def user(db):
    """User authentifié"""
    return UserFactory(email='test@example.com')

@pytest.fixture
def authenticated_client(client, user):
    """Client authentifié"""
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def organization(db, user):
    """Organization avec user comme owner"""
    org = OrganizationFactory()
    org.members.create(user=user, role='owner')
    return org

@pytest.fixture
def api_client():
    """API client pour tests"""
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def product_data(organization):
    """Données valides pour créer un produit"""
    return {
        'name': 'Test Product',
        'price': '99.99',
        'description': 'Test description',
        'organization': organization.id
    }
```

## Commandes pytest

```bash
# Tests avec coverage
pytest --cov=apps.products --cov-report=html

# Tests parallèles (plus rapide)
pytest -n auto

# Tests marqués
pytest -m "not slow"

# Tests avec debugging
pytest -vv -s

# Tests échouants uniquement
pytest --lf
```

Générez des tests professionnels complets en quelques secondes ! 🧪
