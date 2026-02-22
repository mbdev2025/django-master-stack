# 🎯 Préparation pour la Mise en Production Enedis

Ce document récapitule les points clés pour votre réunion Teams avec Enedis (eRITM4245470).

## 1. Déroulé de la Démonstration (The Golden Path)

1.  **Dashboard Pro** : Montrez l'interface installateur. Expliquez que c'est l'outil de gestion des dossiers solaires.
2.  **Invitation (Nouveau Formulaire)** :
    *   Saisissez la **Civilité**, le **Nom** et le **PRM**.
    *   Montrez la fenêtre de prévisualisation : "Bonjour M./Mme [Nom]".
    *   *Argument à dire* : "Nous respectons un formalisme strict dès le premier contact pour rassurer l'usager."
3.  **Page de Consentement** :
    *   Suivez le lien. Montrez la mise en page institutionnelle.
    *   *Argument à dire* : "Nous présentons clairement les 3 types de données collectées et la durée d'historique de 36 mois exigée pour un audit solaire précis."
4.  **Validation Fluide** : Cliquez sur **"CONFIRMER MON ACCORD"**.
    *   *Note technique* : Pour la démo, nous avons activé un mode fluide qui simule le succès immédiatement. En production, ce bouton pointe vers `enedis.fr` via le `EnedisClient` déjà prêt.
5.  **Historique & Suivi** :
    *   Montrez la ligne client passer de **"EN ATTENTE"** à **"ACCEPTÉ"**.
    *   Expliquez la possibilité d'**Annuler** ou de **Supprimer** un dossier.

## 2. Réponses aux Questions Techniques

| Question Enedis | Votre Réponse |
| :--- | :--- |
| **Comment gérez-vous le consentement ?** | "Via le flux OAuth2 DataConnect standard. Nous utilisons `duration=P3D` (3 jours) pour minimiser l'intrusion et rassurer l'usager, tout en collectant l'historique de 36 mois nécessaire à l'audit dès la validation." |
| **Où sont stockées les données ?** | "Les données sont stockées sur nos serveurs sécurisés. Les tokens (Access/Refresh) sont chiffrés en base de données selon les normes RGPD." |
| **Quelle est la finalité exacte ?** | "L'analyse fine de la courbe de charge (pas 30 min) pour calculer précisément le taux d'autoconsommation et générer une section **'Analyse et recommandations'** personnalisée." |
| **Comment l'utilisateur peut-il révoquer ?** | "Depuis son espace client ou en retirant les droits sur son portail Enedis." |
| **Gérez-vous les différents tarifs (HC/HP, Tempo) ?** | "Oui. L'outil récupère le calendrier tarifaire via le service **'Données Techniques'** de l'API. Notre moteur applique ensuite les index HC/HP spécifiques au point de livraison pour un ROI exact." |

## 3. Points Forts de la Version Actuelle (Conformité V5)

- [x] **Parcours Client Homologué** : Respect strict du flux en 6 étapes (Documenté sur Enedis DataHub).
- [x] **Bouton Officiel** : Utilisation du visuel conforme "j'accède à mon espace client Enedis" avec logo et couleur #1E40AF.
- [x] **Wordings Institutionnels** : Intégration des mentions obligatoires sur le rôle d'Enedis et la transparence de redirection.
- [x] **Gestion Tarifaire** : Sélecteur dynamique (Base, HC/HP, Tempo, EJP) pour s'adapter à 100% des contrats.
- [x] **Historique Détaillé** : Tableau mensuel avec colonnes **Total, HC et HP** et filtre par année (2023-2025).
- [x] **Rapport Pro** : Section rebaptisée *"Analyse et recommandations"* pour coller aux standards d'audit.
- [x] **Navigation Fluide** : Boutons de retour rapides entre les rapports et le dashboard pro.
- [x] **Export Clean** : Impression PDF optimisée (masquage des éléments d'interface).
- [x] **Page de Succès Premium** : Redirection automatique vers une page confirmant la liaison du compte (Step 5 du parcours).
- [x] **Gestion des Statuts** : Cycle de vie clair (**Accepté**, **En attente**, **Annulé**).


---
*Document synchronisé le 13/02/2026 pour le dossier eRITM4245470.*
*Mise en conformité Parcours Client v5 effectuée.*
