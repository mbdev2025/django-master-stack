{ pkgs, ... }: {
  # Canal stable
  channel = "stable-23.11";

  # Paquets système pour une stack complexe (Django 6 + Wagtail + Celery + Playwright)
  packages = [
    pkgs.python312
    pkgs.python312Packages.pip
    pkgs.python312Packages.virtualenv
    pkgs.postgresql
    pkgs.redis
    pkgs.git
    pkgs.playwright-driver
    # Dépendances pour Playwright/Scrapers
    pkgs.nss
    pkgs.nspr
    pkgs.libdrm
    pkgs.dbus
    pkgs.atk
    pkgs.at-spi2-atk
    pkgs.expat
    pkgs.libxkbcommon
    pkgs.pango
    pkgs.cairo
  ];

  env = {
    PYTHON_VERSION = "3.12";
    DJANGO_SETTINGS_MODULE = "config.settings";
  };

  services = {
    # Activation de Redis pour Celery/Caching
    redis.enable = true;
    
    # Activation de PostgreSQL pour la base de données métier
    postgres = {
      enable = true;
      package = pkgs.postgresql;
    };
  };

  idx = {
    extensions = [
      "ms-python.python"
      "batisteo.vscode-django"
      "ms-azuretools.vscode-docker"
      "redhat.vscode-yaml"
    ];

    workspace = {
      onCreate = {
        setup = ''
          # Initialisation Backend
          python3 -m venv venv
          source venv/bin/activate
          pip install --upgrade pip
          pip install -r requirements.txt
          
          # Configuration environnement
          if [ ! -f .env ]; then
            cp .env.example .env
            # Génération d'une SECRET_KEY automatique via python
            python -c "import secrets; print(f'\nSECRET_KEY=\"{secrets.token_urlsafe(50)}\"')" >> .env
          fi
          
          # Migrations
          python manage.py migrate
          
          echo "✅ PowerStack Master initialisée avec succès !"
        '';
      };
    };

    previews = {
      enable = true;
      previews = {
        web = {
          command = ["venv/bin/python" "manage.py" "runserver" "0.0.0.0:$PORT"];
          manager = "web";
          env = {
            PORT = "8000";
          };
        };
      };
    };
  };
}
