# 📚 Stack Reference - Django Master Stack (PowerEdition)

## 🏗️ Stack Technique
- **Django 6.0.2** (Python 3.12)
- **Wagtail 7.3** (CMS)
- **Celery + Redis** (Tâches asynchrones)
- **Stripe** (Paiements)
- **Playwright** (Scraping & Automation)
- **PostgreSQL** (Service métier)

---

## 🚀 Commandes de Puissance

### 📝 Gestion du Contenu (Wagtail)
Accès au CMS : `/cms/`
Pour créer votre premier accès :
```bash
python manage.py createsuperuser
```

### ⚙️ Tâches de Fond (Celery)
Pour lancer le worker Celery (nécessite Redis actif) :
```bash
celery -A config worker --loglevel=info
```
Pour lancer le scheduler (tâches récurrentes) :
```bash
celery -A config beat --loglevel=info
```

### 💳 Paiements (Stripe)
Vérifiez que vos clés sont configurées dans le `.env` :
- `STRIPE_PUBLIC_KEY`
- `STRIPE_SECRET_KEY`

### 🕸️ Scrapers (Playwright)
Si vous utilisez les scrapers, n'oubliez pas d'installer le driver si nécessaire (géré normalement par dev.nix) :
```bash
playwright install chromium
```

---

## ⚠️ Points d'Attention
1. **Python 3.12** : Cette stack NE FONCTIONNE PAS avec Python versions < 3.12 à cause de Django 6.
2. **Redis** : Assurez-vous que le service Redis est lancé pour que Celery ne plante pas.
3. **Postgres** : Configurez votre `DATABASE_URL` dans le `.env` pour sortir de SQLite en production.

---
*Maintenu par Antigravity - Février 2026*
