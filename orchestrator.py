import os
import subprocess
import sys

def setup_new_project():
    print("🛠️  Orchestrateur Python : Initialisation du projet...")
    
    # 1. Vérifier la présence des fichiers critiques
    if not os.path.exists('.env.example'):
        print("❌ Erreur : .env.example manquant.")
        return

    # 2. Lancer le setup existant
    subprocess.run([sys.executable, "scripts/setup_project.py"])
    
    # 3. Création automatique d'un environnement virtuel Python (Optionnel mais conseillé)
    if not os.path.exists('venv'):
        print("📦 Création de l'environnement virtuel...")
        subprocess.run([sys.executable, "-m", "venv", "venv"])
    
    print("\n✅ Système prêt. Vous pouvez commencer à coder avec les modules 'apps/'.")

if __name__ == "__main__":
    setup_new_project()
