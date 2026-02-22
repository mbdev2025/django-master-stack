# 📋 Dossier de Conformité : Parcours Client Enedis DataConnect v5

**À l'attention de : Équipe Enedis DataConnect**  
**Objet : Demande de validation en production - Dossier eRITM4245470**  
**Projet : Linky Monitor (Energy Sobriété)**  
**Date : 13 février 2026**  
**Version du parcours : DataConnect v5**

---

## 1. Présentation de l'Application

**Nom commercial :** Linky Monitor  
**Éditeur :** Energy Sobriété  
**Finalité :** Audit de consommation électrique pour dimensionnement d'installations solaires photovoltaïques  
**URL de production :** `https://energysobriete.com`  
**URL de callback OAuth2 :** `https://energysobriete.com/api/energy/auth/callback/`

### Scopes demandés
- `openid` : Identification utilisateur
- `identity` : Nom et prénom
- `contact` : Coordonnées
- `contracts` : Informations contractuelles
- `addresses` : Adresse du point de livraison
- `daily_consumption` : Consommation journalière
- `consumption_load_curve` : Courbe de charge (pas 30 min)

### Durée de consentement
**3 jours** (`duration=P3D`) pour minimiser l'intrusion tout en permettant la collecte ponctuelle de l'historique de **36 mois** nécessaire à l'audit solaire.

---

## 2. Respect du Parcours Client en 6 Étapes

### 📸 Étape 1 : Présentation du Service (Dashboard Partenaire)

![Dashboard avec bouton Enedis](dossier_1_dashboard_conformity_1770995706879.png)

**Éléments conformes :**
- ✅ Bouton bleu officiel Enedis (#1E40AF) avec logo carré
- ✅ Wording exact : *"j'accède à mon espace client Enedis"* (tout en minuscules)
- ✅ Mention institutionnelle obligatoire sous le bouton : *"Enedis gère le réseau d'électricité jusqu'au compteur d'électricité"*

**Vue technique :** Le bouton déclenche une redirection vers notre page de consentement intermédiaire (`/simulation/enedis/authorize/`) qui prépare l'utilisateur avant le passage sur le portail Enedis.

---

### 📸 Étape 2 : Page de Consentement Intermédiaire

![Page de consentement avec parcours 6 étapes](enedis_6_step_journey_1770996641829.png)

**Éléments conformes :**

1. **Texte Institutionnel (Bloc 1)** :
   > *"Enedis gère le réseau d'électricité jusqu'au compteur d'électricité. Pour Linky Monitor, autorisez Enedis à nous transmettre vos données Linky."*

2. **Rôle d'Enedis (Bloc 2)** :
   > *"Enedis est le gestionnaire du réseau public de distribution d'électricité sur 95% du territoire français continental."*

3. **Parcours Visuel** : Frise en 6 étapes clairement identifiée
   - Étape 1 : Présentation
   - Étape 2 : Bouton de partage
   - Étape 3 : Connexion Enedis
   - Étape 4 : Choix des données
   - Étape 5 : Retour application
   - Étape 6 : Gestion du partage

4. **Avertissement de Redirection (Bloc 3)** :
   > *"En cliquant sur ce bouton, vous allez accéder à votre compte personnel Enedis où vous pourrez donner votre accord pour qu'Enedis nous transmette vos données."*

5. **Bouton de Validation** : Reprend le wording officiel *"j'accède à mon espace client Enedis"*

---

### Étape 3 : Connexion au Portail Enedis

L'utilisateur est redirigé vers :
```
https://mon-compte-particulier.enedis.fr/dataconnect/v1/oauth2/authorize?
  client_id=J0Ikt1bIiD9h3r_lJJnr4BziMkIa&
  duration=P3D&
  redirect_uri=https://energysobriete.com/api/energy/auth/callback/&
  response_type=code&
  scope=openid%20identity%20contact%20contracts%20addresses%20daily_consumption%20consumption_load_curve
```

**Point clé :** L'utilisateur voit clairement sur le portail Enedis qu'il consent pour **3 jours**, tout en étant informé que l'**historique de 36 mois** sera collecté (conforme aux mentions obligatoires Enedis).

---

### Étape 4 : Validation sur le Portail Enedis

L'utilisateur :
1. Se connecte avec ses identifiants Enedis
2. Consulte la liste des données partagées (consommation, identité, contrats)
3. Coche la case de consentement libre et éclairé
4. Valide le partage

---

### 📸 Étape 5 : Retour vers l'Application (Page de Succès)

![Page de confirmation de succès](dossier_2_consent_page_v5_1770995781554.png)

**Éléments conformes :**
- ✅ Confirmation visuelle immédiate (icône de succès)
- ✅ Message de remerciement clair
- ✅ Indication de la synchronisation en cours
- ✅ Redirection automatique vers le dashboard après 3 secondes

**Vue technique :** Après validation, Enedis renvoie un `code` d'autorisation à notre callback. Nous l'échangeons contre un `access_token` et un `refresh_token`, puis affichons cette page de confirmation avant de rediriger vers le dashboard utilisateur.

---

### Étape 6 : Gestion du Partage de Données

**Révocation par l'utilisateur :**
1. Depuis son dashboard Linky Monitor : bouton "Révoquer l'accès Enedis"
2. Depuis son espace personnel Enedis : gestion des consentements

**Conformité RGPD :**
- Tokens chiffrés en base de données
- Pas de conservation de données au-delà de la finalité (audit solaire)
- Possibilité de suppression totale du compte utilisateur

---

## 3. Justifications Techniques

### Pourquoi 3 jours de consentement pour 36 mois d'historique ?

**Principe de minimisation :** Nous ne conservons l'accès actif que le temps nécessaire à la récupération des données historiques et à la génération du rapport d'audit. Une fois le rapport généré (généralement sous 24-48h), l'accès n'est plus requis.

**Transparence utilisateur :** L'affichage "3 jours" sur le portail Enedis rassure l'utilisateur quant à la durée de notre accès, tout en respectant l'exigence métier de récupération d'un historique long (nécessaire pour analyser les variations saisonnières et calculer un taux d'autoconsommation précis).

### Scopes requis : Justification

| Scope | Justification métier |
|-------|---------------------|
| `openid`, `identity`, `contact` | Identification du client pour associer le PRM au dossier solaire |
| `contracts`, `addresses` | Vérification de la puissance souscrite et du tarif (Base, HC/HP, Tempo, EJP) |
| `daily_consumption` | Vue macro pour tendance annuelle |
| `consumption_load_curve` | **Donnée clé** : Courbe à 30 min sur 36 mois pour calculer autoconsommation/injection précise |

### Gestion des Tarifs Complexes

Notre moteur d'analyse récupère le calendrier tarifaire via le service **Données Techniques** de l'API Enedis, puis applique les index HC/HP spécifiques au point de livraison pour un ROI exact, conforme aux exigences de l'audit énergétique réglementaire.

---

## 4. Sécurité et Conformité RGPD

- **Chiffrement** : Tokens OAuth2 stockés chiffrés (AES-256)
- **Logs** : Traçabilité des accès API Enedis (date, scope, résultat)
- **Durée de conservation** : 3 ans maximum conformément à la réglementation sur les audits énergétiques
- **Droit à l'effacement** : Suppression complète des données sur demande utilisateur

---

## 5. Points de Contact

**Responsable technique :**  
Nom : [Votre Nom]  
Email : [Votre Email]  
Téléphone : [Votre Téléphone]

**Déclaration CNIL :** [Numéro le cas échéant]

---

## 6. Checklist de Conformité v5

- [x] Bouton officiel Enedis avec wording exact
- [x] Mentions institutionnelles obligatoires (rôle Enedis, 95% du territoire)
- [x] Parcours client en 6 étapes visualisé
- [x] Avertissement de redirection vers portail Enedis
- [x] Page de confirmation après retour OAuth2
- [x] Gestion de la révocation utilisateur
- [x] Scopes justifiés et minimisés
- [x] Durée de consentement adaptée (P3D)
- [x] Conformité RGPD (chiffrement, traçabilité, effacement)

---

**Nous confirmons que l'implémentation respecte scrupuleusement le guide "Parcours Client DataConnect v5" et sommes prêts pour la mise en production.**

*Cordialement,*  
*L'équipe Energy Sobriété*
