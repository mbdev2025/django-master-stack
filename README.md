# 🚀 Django Master Stack (Édition Omni-Channel)

> **La stack ultime pour développer des Applications Mobiles, Sites E-commerce, SaaS et Plateformes Web complexes.**
> *Backend: Django 6.0.2 + Wagtail CMS 7.3 | API: DRF 3.16.1 + JWT 5.5.1 | Frontend Ready: Mobile & Web*

## 🌟 Vision
Cette stack ne se contente pas d'être un backend. C'est un **écosystème complet** conçu pour lancer des projets de haut niveau (Type "Uber", "Shopify custom", "Super App") en quelques minutes. Elle unifie la gestion de contenu (CMS), le commerce, l'automatisation et l'API mobile.

---

## 🛠️ Pile technologique et architecture

### **Noyau et API (Priorité au mobile)**
*   **Django 6.0.2** : Le framework web sécurisé et évolutif.
*   **Django REST Framework 3.16.1** : Pour construire des API robustes.
*   **JWT Auth 5.5.1 (`simplejwt`)** : Authentification sécurisée pour Apps Mobiles (iOS/Android) & SPA.
*   **Swagger / OpenAPI 0.29.0 (`drf-spectacular`)** : Documentation API interactive automatique.
*   **CORS Headers 4.9.0** : Prêt pour le développement multiplateforme (React Native, Flutter, Next.js).

### **Contenu & E-commerce (Web & Tablette)**
*   **Wagtail CMS 7.3** : Gestion de contenu "Headless" puissante pour blogs, landing pages et catalogues.
*   **Stripe 14.3.0 (`apps.payments`)** : Module de paiement intégré (Abonnements & One-off).
*   **Django Filter 25.2** : Moteur de filtrage avancé pour catalogues produits (E-commerce).

### **Conception et interface utilisateur (pilotées par l'IA)**
*   **Google Stitch (IA Design)** : Génération de UI et prototypage rapide via Gemini.
*   **Figma** : Collaboration design et export d'assets.
*   **Material Design 3** : Système de composants UI.

### **Infrastructure et DevOps**
*   **PostgreSQL Ready** : Production de configuration (via `.env`), SQLite par défaut en dev.
*   **S3 Storage 1.14.6 (`django-storages`)** : Stockage cloud des médias (AWS/MinIO) prêt à l'emploi.
*   **Whitenoise 6.11.0** : Service de fichiers statiques haute performance.
*   **Docker Ready** : (À venir via `orchestrator.py`).
*   **Celery 5.6.2 + Redis 7.1.0** : Files d'attente pour tâches asynchrones.

---

## 🚀 Démarrage Rapide (Quick Start)

### 1. Cloner le projet
```bash
git clone https://github.com/mbdev2025/django-master-stack.git my-project
cd my-project
```

### 2. Initialiser l'environnement
```bash
# Créer l'environnement virtuel et installer les dépendances
python3 -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Lancer le script de setup (génère .env)
python scripts/setup_project.py
```

### 3. Lancer les migrations et le serveur
```bash
python manage.py migrate
python manage.py createsuperuser # Créer un admin (ex: admin/admin)
python manage.py runserver
```

---

## 🗺️ Guide des Endpoints

Une fois le serveur lancé (`http://localhost:8000`), voici vos outils :

| Service | URL | Description |
| :--- | :--- | :--- |
| **🏠 Admin Django** | `/admin/` | Gestion technique et base de données. |
| **📝 Wagtail CMS** | `/cms/` | Édition de contenu, pages, images, documents. |
| **📚 API Docs (Swagger)** | `/api/docs/` | Documentation interactive de l'API pour les devs mobile/front. |
| **🔌 API Schema** | `/api/schema/` | Schéma OpenAPI 3.0 brut. |
| **🔑 Auth Token** | `/api/token/` | Obtenir un token JWT (Login). |

---

## ⚙️ Configuration (.env)

Le fichier `.env` contrôle tout. Voici les nouvelles sections clés :

```ini
# === SECURITY ===
DEBUG=True
SECRET_KEY=...
ALLOWED_HOSTS=...

# === DATABASE ===
# Décommenter pour la PROD
# DATABASE_URL=postgres://user:pass@host:5432/db

# === STORAGE (S3 / MinIO) ===
# Si défini, le stockage bascule automatiquement sur S3
# AWS_ACCESS_KEY_ID=...
# AWS_SECRET_ACCESS_KEY=...
# AWS_STORAGE_BUCKET_NAME=...

# === APPS ===
STRIPE_SECRET_KEY=...
N8N_API_KEY=...
```

---

## 📱 Prêt pour le Mobile ?

1.  Connectez votre app (React Native / Flutter) à `http://localhost:8000/api/`.
2.  Utilisez `/api/token/` pour loguer vos utilisateurs.
3.  Consommez le contenu éditorial via l'API Wagtail (activé par défaut).

## 🛒 Prêt pour l'E-commerce ?

1.  Utilisez `apps.payments` pour gérer les clients Stripe.
2.  Créez vos modèles `Product` dans `apps.core`.
3.  Utilisez `django-filter` pour créer des facettes de recherche.

---
*Maintained by MBDev2025*
