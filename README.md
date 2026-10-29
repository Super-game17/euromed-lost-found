# 📍 Euromed Lost & Found — UEMF
Plateforme web de gestion des objets perdus et trouvés sur le campus de l'Université Euromed de Fès.
## 🛠️ Tech Stack
- **Backend :** Python (Flask), Flask-SQLAlchemy, Flask-Login
- **Frontend :** HTML5, CSS3, JavaScript
- **Base de données :** PostgreSQL / SQLite (local)
- **Déploiement :** Render

## Déploiement rapide sur Render

1. Enregistrer et pousser les changements sur GitHub, sur la branche `main`.
2. Dans Render, choisir **New + → Blueprint**, connecter le dépôt `Super-game17/euromed-lost-found` et valider `render.yaml`.
3. Attendre la création du service web et de PostgreSQL, puis ouvrir l’URL `onrender.com` indiquée par Render.

Le Blueprint génère automatiquement `SECRET_KEY` et relie l’application à PostgreSQL.
L’application démarre avec Gunicorn. La base PostgreSQL gratuite convient à un essai,
mais ses limites et sa durée de disponibilité dépendent de l’offre Render en vigueur.
Le stockage des photos téléversées est temporaire sur l’offre gratuite : les photos
peuvent disparaître lors d’un redéploiement ou d’un redémarrage. Pour conserver les
photos et les données de façon fiable, prévoir un stockage persistant avant la mise
en production. Les données de la base SQLite locale ne sont pas importées automatiquement.
## 👥 Organisation de l'Équipe
- **Groupe 1 (Authentification) :** Asia er Doae
- **Groupe 2 (Objets Perdu/Trouvé) :** Aymane et Ali
- **Groupe 3 (Recherche & Restitution) :** Chaimae et Charis
- **Designer / UI-UX :** Hajar
## 🚀 Installation Locale
1. **Cloner le dépôt :**
   ```bash
   git clone [https://github.com/Super-game17/euromed-lost-found.git](https://github.com/Super-game17/euromed-lost-found.git)
   cd euromed-lost-found
