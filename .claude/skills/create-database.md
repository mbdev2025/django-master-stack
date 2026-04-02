---
name: create-database
description: Génère automatiquement des schémas de base de données optimisés avec migrations, indexes, constraints
---

# Skill: Create Database

Crée instantanément des schémas de base de données optimisés pour le SaaS.

## Utilisation

```
/create-database <schema_name> [options]
```

## Exemples

```bash
# Schéma SaaS complet
/create-database ecommerce

# Schéma avec options
/create-database crm --with:audit,soft_delete,permissions

# Schéma multi-tenancy
/create-database saas --multi-tenant --row_level_security
```

## Options

- `--indexes`: Indexes optimisés automatiques
- `--constraints`: Constraints et validations
- `--audit`: Audit trail complet
- `--soft_delete`: Soft delete au lieu de hard delete
- `--row_level_security`: Row-level security par organization
- `--partitioning`: Partitioning pour grosses tables
- `--full_text`: Full-text search PostgreSQL
- `--triggers`: Triggers pour automatismes

## Ce qui est généré

### 1. Modèles Optimisés

```python
class Product(models.Model):
    # Champs métier
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(unique=True, max_length=250)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_index=True  # Index pour filtres prix
    )

    # Relations
    category = models.ForeignKey(
        'Category',
        on_delete=models.PROTECT,  # Protéger les suppressions accidentelles
        related_name='products',
        db_index=True
    )

    # Multi-tenancy
    organization = models.ForeignKey(
        'tenants.Organization',
        on_delete=models.CASCADE,
        related_name='products',
        db_index=True  # Index pour filtrage organization
    )

    # Audit trail
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_products'
    )
    updated_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_products'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Soft delete
    is_active = models.BooleanField(default=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        # Indexes composites
        indexes = [
            models.Index(fields=['organization', '-created_at']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['price', 'is_active']),
        ]

        # Ordering par défaut
        ordering = ['-created_at']

        # Permissions
        default_permissions = ('view', 'add', 'change', 'delete')
        permissions = [
            ('can_export', 'Can export products'),
            ('can_bulk_import', 'Can bulk import products'),
        ]

        # Constraints
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gte=0),
                name='price_positive'
            ),
            models.UniqueConstraint(
                fields=['organization', 'slug'],
                name='unique_org_slug'
            )
        ]

        # Database table options
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        """Soft delete implementation"""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()
```

### 2. Migrations avec Data

```python
# Generated migration
from django.db import migrations, models
import django.utils.timezone
import uuid

class Migration(migrations.Migration):
    dependencies = [
        ('tenants', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(primary_key=True)),
                ('name', models.CharField(max_length=200, db_index=True)),
                ('slug', models.SlugField(unique=True, max_length=250)),
                ('description', models.TextField()),
                ('price', models.DecimalField(
                    max_digits=10,
                    decimal_places=2,
                    db_index=True
                )),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True, db_index=True)),
                ('deleted_at', models.DateTimeField(null=True, blank=True)),
                ('metadata', models.JSONField(default=dict, blank=True)),
                ('category', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='products',
                    to='products.category',
                    db_index=True
                )),
                ('organization', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='products',
                    to='tenants.organization',
                    db_index=True
                )),
                ('created_by', models.ForeignKey(
                    on_delete=django.db.models.deletion.SET_NULL,
                    null=True,
                    related_name='created_products',
                    to='users.user'
                )),
                ('updated_by', models.ForeignKey(
                    on_delete=django.db.models.deletion.SET_NULL,
                    null=True,
                    related_name='updated_products',
                    to='users.user'
                )),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
                'ordering': ['-created_at'],
                'db_table': 'products',
            },
        ),

        # Indexes
        migrations.AddIndex(
            model_name='product',
            index=models.Index(
                fields=['organization', '-created_at'],
                name='product_org_created_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(
                fields=['category', 'is_active'],
                name='product_category_active_idx'
            ),
        ),

        # Constraints
        migrations.AddConstraint(
            model_name='product',
            constraint=models.CheckConstraint(
                check=models.Q(price__gte=0),
                name='price_positive'
            ),
        ),
        migrations.AddConstraint(
            model_name='product',
            constraint=models.UniqueConstraint(
                fields=['organization', 'slug'],
                name='unique_org_slug'
            ),
        ),
    ]
```

### 3. Triggers PostgreSQL

```python
# Migration pour triggers
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('products', '0002_auto_20240101_1234'),
    ]

    operations = [
        migrations.RunSQL("""
            -- Trigger: update updated_at automatiquement
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ language 'plpgsql';

            CREATE TRIGGER update_products_updated_at
                BEFORE UPDATE ON products
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();

            -- Trigger: soft delete avec timestamp
            CREATE OR REPLACE FUNCTION soft_delete_product()
            RETURNS TRIGGER AS $$
            BEGIN
                IF OLD.is_active = TRUE AND NEW.is_active = FALSE THEN
                    NEW.deleted_at = NOW();
                END IF;
                RETURN NEW;
            END;
            $$ language 'plpgsql';

            CREATE TRIGGER soft_delete_products
                BEFORE UPDATE OF is_active ON products
                FOR EACH ROW
                WHEN (NEW.is_active = FALSE)
                EXECUTE FUNCTION soft_delete_product();

            -- Trigger: audit log
            CREATE TABLE IF NOT EXISTS products_audit_log (
                id BIGSERIAL PRIMARY KEY,
                product_id BIGINT NOT NULL,
                action VARCHAR(10) NOT NULL,
                old_data JSONB,
                new_data JSONB,
                changed_by INTEGER REFERENCES users_user(id),
                changed_at TIMESTAMP DEFAULT NOW()
            );

            CREATE OR REPLACE FUNCTION log_product_changes()
            RETURNS TRIGGER AS $$
            BEGIN
                IF TG_OP = 'INSERT' THEN
                    INSERT INTO products_audit_log (product_id, action, new_data)
                    VALUES (NEW.id, 'INSERT', row_to_json(NEW)::jsonb);
                ELSIF TG_OP = 'UPDATE' THEN
                    INSERT INTO products_audit_log (product_id, action, old_data, new_data)
                    VALUES (NEW.id, 'UPDATE', row_to_json(OLD)::jsonb, row_to_json(NEW)::jsonb);
                ELSIF TG_OP = 'DELETE' THEN
                    INSERT INTO products_audit_log (product_id, action, old_data)
                    VALUES (OLD.id, 'DELETE', row_to_json(OLD)::jsonb);
                END IF;
                RETURN NULL;
            END;
            $$ language 'plpgsql';

            CREATE TRIGGER audit_products_changes
                AFTER INSERT OR UPDATE OR DELETE ON products
                FOR EACH ROW
                EXECUTE FUNCTION log_product_changes();
        """),
    ]
```

### 4. Row-Level Security

```python
# Migration pour RLS
migrations.RunSQL("""
    -- Activer Row-Level Security
    ALTER TABLE products ENABLE ROW LEVEL SECURITY;

    -- Policy: Les users ne voient que les produits de leur organization
    CREATE POLICY products_org_isolation_policy
        ON products
        FOR SELECT
        USING (
            organization_id IN (
                SELECT organization_id
                FROM tenants_member
                WHERE user_id = current_setting('app.user_id')::INTEGER
            )
        );

    -- Policy: Les users peuvent créer des produits dans leur organization
    CREATE POLICY products_create_policy
        ON products
        FOR INSERT
        WITH CHECK (
            organization_id IN (
                SELECT organization_id
                FROM tenants_member
                WHERE user_id = current_setting('app.user_id')::INTEGER
                  AND role IN ('admin', 'owner')
            )
        );

    -- Policy: Les admins peuvent modifier les produits de leur org
    CREATE POLICY products_update_policy
        ON products
        FOR UPDATE
        USING (
            organization_id IN (
                SELECT organization_id
                FROM tenants_member
                WHERE user_id = current_setting('app.user_id')::INTEGER
                  AND role IN ('admin', 'owner')
            )
        );

    -- Policy: Seuls les owners peuvent supprimer
    CREATE POLICY products_delete_policy
        ON products
        FOR DELETE
        USING (
            organization_id IN (
                SELECT organization_id
                FROM tenants_member
                WHERE user_id = current_setting('app.user_id')::INTEGER
                  AND role = 'owner'
            )
        );
""")
```

### 5. Full-Text Search

```python
# Migration pour FTS
migrations.RunSQL("""
    -- Ajouter colonne tsvector pour full-text search
    ALTER TABLE products ADD COLUMN search_vector tsvector;

    -- Créer index GIN
    CREATE INDEX products_search_idx ON products USING GIN (search_vector);

    -- Trigger pour mettre à jour search_vector
    CREATE OR REPLACE FUNCTION products_search_vector_update()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.search_vector :=
            setweight(to_tsvector('french', coalesce(NEW.name, '')), 'A') ||
            setweight(to_tsvector('french', coalesce(NEW.description, '')), 'B');
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE TRIGGER products_search_vector_trigger
        BEFORE INSERT OR UPDATE ON products
        FOR EACH ROW
        EXECUTE FUNCTION products_search_vector_update();
""")

# Query Manager
class ProductManager(models.Manager):
    def search(self, query):
        return self.get_queryset().filter(
            search_vector=query
        ).annotate(
            rank=SearchRank(F('search_vector'), SearchQuery(query))
        ).order_by('-rank')
```

### 6. Partitioning (Grosses Tables)

```python
# Migration pour partitioning par date
migrations.RunSQL("""
    -- Créer table parent
    CREATE TABLE orders (
        id BIGSERIAL,
        organization_id INTEGER NOT NULL,
        customer_id INTEGER NOT NULL,
        total DECIMAL(10,2) NOT NULL,
        status VARCHAR(20) NOT NULL,
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP NOT NULL,
        PRIMARY KEY (id, created_at)
    ) PARTITION BY RANGE (created_at);

    -- Créer partitions par mois
    CREATE TABLE orders_2024_01 PARTITION OF orders
        FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

    CREATE TABLE orders_2024_02 PARTITION OF orders
        FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

    -- Indexes sur partitions
    CREATE INDEX orders_2024_01_org_idx ON orders_2024_01(organization_id);
    CREATE INDEX orders_2024_01_status_idx ON orders_2024_01(status);
""")
```

### 7. Database Functions

```python
# Migration pour fonctions utilitaires
migrations.RunSQL("""
    -- Fonction: Calculer revenu mensuel
    CREATE OR REPLACE FUNCTION monthly_revenue(org_id INTEGER, month DATE)
    RETURNS DECIMAL AS $$
        DECLARE
            revenue DECIMAL;
        BEGIN
            SELECT COALESCE(SUM(total), 0)
            INTO revenue
            FROM orders
            WHERE organization_id = org_id
              AND DATE_TRUNC('month', created_at) = DATE_TRUNC('month', month)
              AND status IN ('paid', 'completed');
            RETURN revenue;
        END;
        $$ LANGUAGE plpgsql;

    -- Fonction: Compter utilisateurs actifs
    CREATE OR REPLACE FUNCTION count_active_users(org_id INTEGER, days INTEGER)
    RETURNS INTEGER AS $$
        DECLARE
            user_count INTEGER;
        BEGIN
            SELECT COUNT(DISTINCT user_id)
            INTO user_count
            FROM user_activity
            WHERE organization_id = org_id
              AND last_activity >= NOW() - INTERVAL '1 day' * days;
            RETURN user_count;
        END;
        $$ LANGUAGE plpgsql;
""")
```

### 8. Materialized Views

```python
# Migration pour materialized views
migrations.RunSQL("""
    -- Vue matérialisée: Statistiques products par category
    CREATE MATERIALIZED VIEW mv_product_stats AS
    SELECT
        c.id as category_id,
        c.name as category_name,
        COUNT(p.id) as product_count,
        AVG(p.price) as avg_price,
        MIN(p.price) as min_price,
        MAX(p.price) as max_price,
        SUM(CASE WHEN p.is_active THEN 1 ELSE 0 END) as active_count
    FROM categories c
    LEFT JOIN products p ON c.id = p.category_id
    GROUP BY c.id, c.name
    WITH DATA;

    -- Indexes sur vue matérialisée
    CREATE INDEX mv_product_stats_category_idx ON mv_product_stats(category_id);

    -- Fonction refresh
    CREATE OR REPLACE FUNCTION refresh_product_stats()
    RETURNS void AS $$
        BEGIN
            REFRESH MATERIALIZED VIEW CONCURRENTLY mv_product_stats;
        END;
        $$ LANGUAGE plpgsql;
""")
```

### 9. Backup & Restore

```python
# Management command pour backups
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Create database backup'

    def add_arguments(self, parser):
        parser.add_argument('--output', type=str, default='backup.sql')

    def handle(self, *args, **options):
        import subprocess
        from django.conf import settings

        db = settings.DATABASES['default']

        cmd = [
            'pg_dump',
            f'--host={db["HOST"]}',
            f'--port={db["PORT"]}',
            f'--user={db["USER"]}',
            f'--dbname={db["NAME"]}',
            '--no-owner',
            '--no-acl',
            '--format=plain',
            '--verbose',
            '--file=' + options['output']
        ]

        subprocess.run(cmd, env={'PGPASSWORD': db['PASSWORD']})
        self.stdout.write(self.style.SUCCESS(f'Backup saved to {options["output"]}'))
```

## Optimisations Performance

### Indexes Stratégiques
- **Composite indexes** pour les requêtes fréquentes
- **Partial indexes** pour les sous-ensembles de données
- **GIN indexes** pour full-text search et JSON
- **Expression indexes** pour les calculs fréquents

### Query Optimization
- **select_related** pour optimiser les FK
- **prefetch_related** pour optimiser les M2M
- **only()/defer()** pour limiter les champs chargés
- **QuerySet caching** pour les listes statiques

### Connection Pooling
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'sslmode': 'require',
            'connect_timeout': 10,
        },
        'CONN_MAX_AGE': 600,  # Connection pooling
        'POOL': {
            'MAX_SIZE': 20,
            'MIX_SIZE': 5,
        }
    }
}
```

Créez des schémas de base de données production-ready en quelques minutes ! 🗄️
