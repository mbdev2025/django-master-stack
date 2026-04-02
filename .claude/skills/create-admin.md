---
name: create-admin
description: Génère une interface admin Django optimisée SaaS avec dashboards, filtres, actions bulk, export
---

# Skill: Create Admin

Crée instantanément une interface admin Django moderne et optimisée pour le SaaS.

## Utilisation

```
/create-admin <ModelName> [options]
```

## Exemples

```bash
# Admin standard
/create-admin Product

# Admin complet avec toutes les fonctionnalités
/create-admin Order --dashboard --export --actions

# Admin avancé avec filtres personnalisés
/create-admin Subscription --filters --charts --permissions

# Multi admin
/create-admin Product,Category,Order --full
```

## Options

- `--dashboard`: Ajoute dashboard avec statistiques
- `--export`: Export CSV/Excel/PDF
- `--actions`: Actions bulk personnalisées
- `--filters`: Filtres avancés
- `--charts`: Graphiques et métriques
- `--permissions`: Permissions basées sur les rôles
- `--inline`: Inline models pour les relations
- `--calendar`: Vue calendar pour les dates
- `--geomap`: Vue carte pour les adresses

## Ce qui est généré

### 1. Admin Class Complexe

```python
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Liste des champs
    list_display = [
        'name', 'category', 'price', 'is_active',
        'organization', 'created_at', 'get_actions'
    ]

    # Filtres
    list_filter = [
        'is_active', 'category', 'created_at',
        'organization__name', 'created_by'
    ]

    # Recherche
    search_fields = [
        'name', 'description', 'category__name',
        'organization__name'
    ]

    # Navigation par date
    date_hierarchy = 'created_at'

    # Pagination
    list_per_page = 25

    # Ordering par défaut
    ordering = ['-created_at']

    # Read-only fields
    readonly_fields = ['created_at', 'updated_at', 'created_by']

    # Actions bulk
    actions = ['mark_active', 'mark_inactive', 'export_csv']

    # Fieldsets pour organiser le formulaire
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'category', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'compare_at_price', 'sku', 'stock')
        }),
        ('Organisation & Statut', {
            'fields': ('organization', 'is_active', 'created_by')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Inline relations
    inlines = [ProductImageInline, ReviewInline]

    def get_actions(self, obj):
        """Actions personnalisées par ligne"""
        return format_html(
            '<a class="button" href="/admin/products/{}/duplicate/">Dupliquer</a>',
            obj.id
        )

    def mark_active(self, request, queryset):
        """Action bulk: marquer actif"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} produits marqués actifs')
    mark_active.short_description = "Marquer comme actif"

    def export_csv(self, request, queryset):
        """Export CSV des produits sélectionnés"""
        import csv
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=products.csv'
        writer = csv.writer(response)
        writer.writerow(['name', 'price', 'category', 'is_active'])
        for obj in queryset:
            writer.writerow([obj.name, obj.price, obj.category, obj.is_active])
        return response
    export_csv.short_description = "Exporter en CSV"

    def save_model(self, request, obj, form, change):
        """Auto-assigner l'utilisateur connecté"""
        if not change:
            obj.created_by = request.user
            obj.organization = request.user.organization
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """Filtrer par organization du user"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(organization=request.user.organization)
```

### 2. Dashboard Admin Personnalisé

```python
# admin.py de votre app
class DashboardAdmin(admin.ModelAdmin):
    """Dashboard avec statistiques SaaS"""

    def has_add_permission(self, request):
        return False  # Pas d'ajout

    def has_change_permission(self, request, obj=None):
        return False  # Pas de modification

    def changelist_view(self, request, extra_context=None):
        # Statistiques
        from django.db.models import Count, Sum, Avg
        from apps.tenants.models import Organization
        from apps.users.models import User
        from apps.subscriptions.models import Subscription

        # Métriques business
        total_revenue = Subscription.objects.filter(
            status='active'
        ).aggregate(total=Sum('amount'))['total'] or 0

        active_subscriptions = Subscription.objects.filter(status='active').count()

        # Métriques utilisateurs
        total_users = User.objects.count()
        new_users_this_month = User.objects.filter(
            created_at__month=timezone.now().month
        ).count()

        # Métriques organizations
        total_orgs = Organization.objects.count()
        orgs_with_subscriptions = Organization.objects.filter(
            subscriptions__status='active'
        ).distinct().count()

        # Graphiques
        subscription_growth = self._get_subscription_growth()

        extra_context = extra_context or {}
        extra_context.update({
            'total_revenue': total_revenue,
            'active_subscriptions': active_subscriptions,
            'total_users': total_users,
            'new_users_this_month': new_users_this_month,
            'total_orgs': total_orgs,
            'orgs_with_subscriptions': orgs_with_subscriptions,
            'subscription_growth': subscription_growth,
        })

        return super().changelist_view(request, extra_context)

    def _get_subscription_growth(self):
        """Données pour graphique croissance"""
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta

        last_30_days = [timezone.now() - timedelta(days=i) for i in range(30)]
        data = []
        for day in last_30_days:
            count = Subscription.objects.filter(
                created_at__date=day.date()
            ).count()
            data.append({'date': day.date(), 'count': count})
        return data

# Template dashboard changelist
# templates/admin/dashboard.html
{% extends "admin/change_list.html" %}

{% block content %}
<div class="dashboard-stats">
    <div class="stat-card">
        <h3>Revenu Total</h3>
        <p class="stat-value">€{{ total_revenue|floatformat:2 }}</p>
    </div>
    <div class="stat-card">
        <h3>Abonnements Actifs</h3>
        <p class="stat-value">{{ active_subscriptions }}</p>
    </div>
    <div class="stat-card">
        <h3>Utilisateurs Totaux</h3>
        <p class="stat-value">{{ total_users }}</p>
    </div>
    <div class="stat-card">
        <h3>Nouveaux ce mois</h3>
        <p class="stat-value">+{{ new_users_this_month }}</p>
    </div>
</div>

<canvas id="subscriptionChart"></canvas>
<script>
const data = {{ subscription_growth|safe }};
// Chart.js code here
</script>
{% endblock %}
```

### 3. Inline Admin

```python
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary']

class ProductVariantInline(admin.StackedInline):
    model = ProductVariant
    extra = 0
    fields = ['size', 'color', 'stock', 'price']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ProductVariantInline]
```

### 4. Filters Personnalisés

```python
class PriceRangeFilter(admin.SimpleListFilter):
    title = 'Gamme de prix'
    parameter_name = 'price_range'

    def lookups(self, request, model_admin):
        return (
            ('low', 'Moins de 50€'),
            ('medium', '50€ - 200€'),
            ('high', 'Plus de 200€'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'low':
            return queryset.filter(price__lt=50)
        if self.value() == 'medium':
            return queryset.filter(price__gte=50, price__lte=200)
        if self.value() == 'high':
            return queryset.filter(price__gt=200)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_filter = [
        PriceRangeFilter,
        'category',
        'is_active',
    ]
```

### 5. Admin Actions Avancées

```python
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    actions = ['mark_as_paid', 'generate_invoices', 'send_notifications']

    def mark_as_paid(self, request, queryset):
        """Marquer comme payé avec historique"""
        for order in queryset:
            order.status = 'paid'
            order.paid_at = timezone.now()
            order.save()
            # Log action
            OrderHistory.objects.create(
                order=order,
                user=request.user,
                action='marked_as_paid'
            )
        self.message_user(
            request,
            f'{queryset.count()} commandes marquées comme payées'
        )
    mark_as_paid.short_description = "Marquer comme payé"

    def generate_invoices(self, request, queryset):
        """Générer factures PDF"""
        from django.core.files.base import ContentFile
        from apps.invoices.utils import generate_pdf_invoice

        for order in queryset:
            pdf = generate_pdf_invoice(order)
            order.invoice.save(
                f'invoice_{order.id}.pdf',
                ContentFile(pdf)
            )
        self.message_user(
            request,
            f'Factures générées pour {queryset.count()} commandes'
        )
```

### 6. Templates Admin Personnalisés

```python
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    change_list_template = 'admin/event_changelist.html'

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)

        # Ajouter vue calendar
        try:
            qs = self.get_queryset(request)
            response.context_data['events'] = qs.values('id', 'title', 'start', 'end')
        except:
            pass
        return response
```

### 7. Export Multi-Format

```python
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    actions = ['export_csv', 'export_excel', 'export_pdf']

    def export_excel(self, request, queryset):
        """Export Excel avec pandas"""
        import pandas as pd
        from django.http import HttpResponse

        data = list(queryset.values(
            'name', 'price', 'category__name', 'stock', 'is_active'
        ))
        df = pd.DataFrame(data)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=products.xlsx'
        df.to_excel(response, index=False)
        return response

    def export_pdf(self, request, queryset):
        """Export PDF avec reportlab"""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=products.pdf'

        doc = SimpleDocTemplate(response, pagesize=letter)
        data = [['Name', 'Price', 'Category', 'Stock']]
        for product in queryset:
            data.append([
                product.name, str(product.price),
                product.category.name, str(product.stock)
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        doc.build([table])
        return response
```

### 8. Permissions par Rôle

```python
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if request.user.role == 'viewer':
            return False
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if request.user.role == 'viewer':
            return False
        if obj and obj.organization != request.user.organization:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if request.user.role in ['viewer', 'member']:
            return False
        if obj and obj.organization != request.user.organization:
            return False
        return super().has_delete_permission(request, obj)
```

### 9. Search Autocomplete

```python
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = ['name', 'sku']

    def get_search_results(self, request, queryset, search_term):
        """Optimiser la recherche avec autocomplete"""
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        if search_term:
            # Recherche FTS avec PostgreSQL
            queryset |= queryset.filter(
                description__search=search_term
            )
        return queryset, use_distinct
```

## Types d'Admin Générés

### E-commerce Admin
```bash
/create-admin Product,Order,Customer --dashboard --export --actions
```

### CRM Admin
```bash
/create-admin Lead,Deal,Activity --filters --charts
```

### Help Desk Admin
```bash
/create-admin Ticket,Message --calendar --permissions
```

### Content Management Admin
```bash
/create-admin Page,Post,Media --inline --bulk-upload
```

## Dashboard Analytics

```python
# Ajoute automatiquement au dashboard
- Revenu mensuel (graphique)
- Croissance utilisateurs (courbe)
- Abonnements actifs (jauge)
- Taux de conversion (progress bar)
- Top produits (tableau)
- Performance serveurs (indicateurs)
```

Créez des interfaces admin Django professionnelles en quelques secondes ! 🚀
