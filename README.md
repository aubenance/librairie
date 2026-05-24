# 📚 LibrairieCI Pro — Documentation Complète
### Version 2.0 | Architecture Client–Serveur | Côte d'Ivoire

---

## 🏗 ARCHITECTURE DU SYSTÈME

```
┌─────────────────────────────────────────────────────────────┐
│                    ARCHITECTURE GLOBALE                      │
│                                                             │
│   POSTE 1 (Admin)        POSTE 2 (Employé)                 │
│   ┌─────────────┐        ┌─────────────┐                   │
│   │LibrairieCI  │        │LibrairieCI  │                   │
│   │   .exe      │        │   .exe      │                   │
│   └──────┬──────┘        └──────┬──────┘                   │
│          │  HTTPS/REST          │                           │
│          └──────────┬───────────┘                           │
│                     │                                       │
│            ┌────────▼────────┐                              │
│            │  SERVEUR        │  ← Railway / Render          │
│            │  FastAPI        │    (Hébergé sur Internet)    │
│            │  + Base SQLite  │                              │
│            └─────────────────┘                              │
│                                                             │
│  ✅ L'admin modifie un article → tous les postes voient     │
│     la mise à jour immédiatement au prochain chargement     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 STRUCTURE DES FICHIERS

```
LibrairieCI_Pro/
│
├── server/                    ← Code du serveur (à héberger)
│   ├── server.py              ← API FastAPI complète
│   ├── requirements.txt       ← Dépendances Python serveur
│   ├── Procfile               ← Config Railway/Render
│   └── railway.json           ← Config déploiement Railway
│
└── client/                    ← Code du client desktop
    ├── main.py                ← Point d'entrée application
    ├── api_client.py          ← Gestion des appels API
    ├── theme.py               ← Thème UI professionnel
    ├── config.json            ← URL du serveur (à modifier)
    ├── LibrairieCI.spec       ← Script de build PyInstaller
    ├── BUILD_EXE.bat          ← Script automatique build .exe
    ├── requirements.txt       ← Dépendances Python client
    └── frames/                ← Écrans de l'application
        ├── login_frame.py     ← Connexion
        ├── dashboard_frame.py ← Tableau de bord
        ├── articles_frame.py  ← Gestion articles (admin)
        ├── vente_frame.py     ← Nouvelle vente
        ├── stock_frame.py     ← Consultation stock
        ├── users_frame.py     ← Gestion utilisateurs (admin)
        └── rapports_frame.py  ← Rapports & statistiques
```

---

## 🚀 ÉTAPE 1 — HÉBERGER LE SERVEUR

### Option A : Railway (Recommandé — Gratuit)

1. Créer un compte sur **https://railway.app** (gratuit)
2. Cliquer **"New Project"** → **"Deploy from GitHub repo"**
   - OU cliquer **"New Project"** → **"Deploy from local directory"**
3. Glisser/déposer le dossier **`server/`** dans Railway
4. Railway détecte automatiquement Python et installe les dépendances
5. Aller dans **Settings** → **Networking** → **Generate Domain**
6. Vous obtenez une URL comme : `https://librairie-ci-xxxx.railway.app`
7. ✅ Votre serveur est en ligne !

**Via GitHub (méthode préférée) :**
```bash
# 1. Créer un repo GitHub avec le dossier server/
# 2. Sur Railway : New Project → GitHub → Sélectionner le repo
# 3. Railway déploie automatiquement à chaque commit
```

---

### Option B : Render (Gratuit)

1. Créer un compte sur **https://render.com**
2. **New** → **Web Service**
3. Connecter votre repo GitHub contenant le dossier `server/`
4. Configurer :
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `uvicorn server:app --host 0.0.0.0 --port $PORT`
5. Cliquer **Create Web Service**
6. URL fournie : `https://librairie-ci.onrender.com`

> ⚠️ **Note Render** : Le plan gratuit "s'endort" après 15min d'inactivité.
> La première requête après une pause prend ~30 secondes. Pour éviter ça,
> utiliser le plan Starter ($7/mois) ou Railway.

---

### Option C : Tester en local (sans internet)

```bash
cd server
pip install -r requirements.txt
python server.py
# Serveur disponible sur http://localhost:8000
```

---

## 🖥 ÉTAPE 2 — COMPILER LE CLIENT EN .EXE

### Prérequis
- Windows 10 ou 11 (64 bits)
- Python 3.11 ou 3.12 : **https://www.python.org/downloads/**
  → ⚠️ Cocher **"Add Python to PATH"** lors de l'installation !

### A. Configurer l'URL du serveur

Avant de compiler, ouvrir **`client/config.json`** et modifier l'URL :

```json
{
  "server_url": "https://votre-serveur.railway.app",
  "app_name": "LibrairieCI",
  "version": "2.0",
  "timeout": 10
}
```

Remplacer `https://votre-serveur.railway.app` par votre vraie URL Railway/Render.

### B. Lancer la compilation

Double-cliquer sur **`BUILD_EXE.bat`**

Le script fait automatiquement :
1. Installe toutes les dépendances
2. Compile le code Python en `.exe`
3. Crée `dist/LibrairieCI/LibrairieCI.exe`

⏳ La compilation prend **2 à 5 minutes** la première fois.

### C. Résultat

```
client/
└── dist/
    └── LibrairieCI/
        ├── LibrairieCI.exe    ← 🎯 Votre exécutable !
        ├── config.json        ← URL du serveur
        └── [autres fichiers]  ← Bibliothèques incluses
```

---

## 📦 ÉTAPE 3 — DISTRIBUER SUR LES POSTES

### Installation sur chaque poste
1. **Copier** le dossier complet `dist/LibrairieCI/` sur chaque poste
   (clé USB, partage réseau, Google Drive...)
2. **Créer un raccourci** vers `LibrairieCI.exe` sur le bureau
3. **Double-cliquer** sur `LibrairieCI.exe` → Le logiciel démarre !

> ✅ **Aucune installation Python requise** sur les postes clients.
> L'exe est autonome.

### Configuration par poste (optionnel)
Si besoin, modifier `config.json` dans le dossier de l'exe pour changer l'URL serveur.
Ou le faire directement depuis l'interface (champ "Serveur" sur l'écran de connexion).

---

## 🔑 COMPTES PAR DÉFAUT

| Rôle           | Identifiant | Mot de passe |
|----------------|-------------|--------------|
| Administrateur | `admin`     | `admin123`   |
| Employé        | `employe`   | `emp123`     |

> ⚠️ **SÉCURITÉ** : Changez ces mots de passe après la première connexion !
> Menu Utilisateurs → Sélectionner → 🔑 Réinitialiser MDP

---

## ✨ FONCTIONNALITÉS DÉTAILLÉES

### 👷 ESPACE EMPLOYÉ
| Section        | Fonctionnalités                                          |
|----------------|----------------------------------------------------------|
| 🛒 Vente       | Recherche rapide, panier, validation, ticket de caisse   |
| 📦 Stock       | Consultation en temps réel, alertes stock faible/rupture |

### 🔑 ESPACE ADMINISTRATEUR (tout + ci-dessous)
| Section         | Fonctionnalités                                          |
|-----------------|----------------------------------------------------------|
| 📖 Articles     | Ajouter, modifier, supprimer, recherche multi-critères   |
| 📊 Rapports     | Historique ventes, filtres par date, top 10 articles     |
| 👥 Utilisateurs | Créer comptes, modifier rôles, réinitialiser mots de passe|
| 🏠 Dashboard    | Stats temps réel : ventes du jour, CA, alertes stock     |

---

## 🔄 SYNCHRONISATION EN TEMPS RÉEL

Toute modification faite par l'admin (prix, stock, nouveaux articles) est
**immédiatement visible** sur tous les postes clients car les données sont
stockées sur le serveur central hébergé.

- Le tableau de bord se rafraîchit automatiquement toutes les **30 secondes**
- Les données de vente/stock sont rechargées à chaque ouverture de section
- Les articles ajoutés par l'admin apparaissent instantanément chez l'employé

---

## 🆘 DÉPANNAGE

| Problème                          | Solution                                              |
|-----------------------------------|-------------------------------------------------------|
| "Connexion impossible"            | Vérifier l'URL dans config.json et la connexion internet |
| "Token expiré"                    | Se déconnecter et se reconnecter                      |
| L'exe ne démarre pas              | Faire clic droit → Exécuter en tant qu'administrateur |
| Serveur lent au 1er démarrage     | Normal sur Render (plan gratuit), attendre 30s        |
| "Identifiant incorrect"           | Vérifier que le serveur est bien démarré              |
| Antivirus bloque l'exe            | Ajouter une exception dans l'antivirus                |

---

## 🔒 SÉCURITÉ

- Les mots de passe sont **hachés (SHA-256)** avant stockage
- Les communications sont protégées par **JWT (JSON Web Token)**
- Les tokens expirent après **12 heures** → reconnexion requise
- Les routes admin sont **protégées côté serveur** (les employés ne peuvent
  pas accéder aux fonctions admin même en modifiant le client)
- En production : activer **HTTPS** sur Railway/Render (automatique)

---

## 🌐 MISE À JOUR DU LOGICIEL

### Mise à jour du serveur
```bash
# Modifier server/server.py
# Pousser sur GitHub → Railway redéploie automatiquement
git add . && git commit -m "Mise à jour" && git push
```

### Mise à jour du client
1. Modifier le code source
2. Relancer `BUILD_EXE.bat`
3. Redistribuer le nouveau `dist/LibrairieCI/` sur les postes

---

## 📞 INFORMATIONS TECHNIQUES

| Composant       | Technologie                        |
|-----------------|------------------------------------|
| Backend API     | Python 3.12 + FastAPI              |
| Base de données | SQLite (local) / PostgreSQL (prod) |
| Authentification| JWT (python-jose)                  |
| Client desktop  | Python + CustomTkinter             |
| Compilation exe | PyInstaller                        |
| Hébergement     | Railway ou Render (gratuit)        |
| Communication   | REST API (HTTPS/JSON)              |

---

*LibrairieCI Pro v2.0 — Logiciel professionnel de gestion de librairie*
*Développé pour la Côte d'Ivoire 🇨🇮*
