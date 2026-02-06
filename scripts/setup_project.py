import os
import secrets
import shutil

def init():
    print("🚀 Initialisation de la Stack Master...")
    if not os.path.exists('.env'):
        shutil.copy('.env.example', '.env')
        print("✅ Fichier .env créé.")
    
    with open('.env', 'r') as f:
        content = f.read()
    
    # Remplace la clé par défaut par une vraie clé sécurisée
    new_key = secrets.token_urlsafe(50)
    content = content.replace('django-insecure-change-me', new_key)
    
    with open('.env', 'w') as f:
        f.write(content)
    print("✨ Configuration terminée. Vous pouvez maintenant lancer Docker ou installer les requirements.")

if __name__ == "__main__":
    init()
