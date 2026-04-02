# 🎨 Guide d'Activation du Skill "Frontend Design"

## 📍 Via VSCode Interface

### Méthode 1: Via la Barre Latérale
1. **Ouvrir VSCode** et ouvrir votre projet django-master-stack
2. **Chercher l'icône Claude** dans la barre latérale droite (icône robotique)
3. **Cliquer sur l'icône Claude** pour ouvrir le panneau
4. **Dans le panneau Claude**, cliquer sur l'icône **⚙️ Settings** (engrenage)
5. **Chercher la section "Skills"** ou "Compétences"
6. **Trouver "frontend-design"** dans la liste
7. **Cliquer sur le toggle** pour l'activer ✅

### Méthode 2: Via Command Palette
1. **Ouvrir VSCode**
2. **Ctrl+Shift+P** (Windows/Linux) ou **Cmd+Shift+P** (Mac)
3. **Taper** : `Claude: Settings`
4. **Chercher** "Skills" ou "frontend-design"
5. **Activer le skill**

### Méthode 3: Via Settings JSON
1. **Ouvrir le fichier** `.vscode/settings.json`
   - S'il n'existe pas, le créer dans `.vscode/`
2. **Ajouter** la configuration :

```json
{
  "claude.skills.enabled": [
    "frontend-design"
  ]
}
```

## 🎯 Une Fois Activé

Le skill sera disponible dans toutes vos conversations Claude !

Vous pourrez alors demander :
- "Crée-moi une interface style Medium pour mon dashboard"
- "Design une page de paiement style Stripe"
- "Fais une interface admin style Linear"

Claude utilisera son expertise design + notre skill `/create-design-system` pour le code.

## ⚠️ Si le skill n'apparaît pas

### Vérifier la Version
1. **Ouvrir les Settings Claude**
2. **Chercher** "About" ou "Version"
3. **Vérifier** que vous avez la dernière version de Claude Code

### Mettre à Jour
1. **Dans VSCode**, aller dans **Extensions**
2. **Chercher** "Claude Code" ou "Claude"
3. **Vérifier les mises à jour**
4. **Installer** la dernière version

## 🔧 Alternative: Utiliser Notre Skill Personnalisé

Si vous ne trouvez pas le skill officiel, notre skill **`/create-design-system`** fait déjà 90% du travail :

```bash
# Créer un design system complet
/create-design-system medium

# Cela génère :
# - Système de typographie
# - Palette de couleurs  
# - Animations
# - Components UI
# - CSS + TypeScript complet
```

Notre skill est **spécifiquement conçu pour cette stack Django SaaS** ! 🎯
