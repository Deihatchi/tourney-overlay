# 🛠️ Guide d'installation complet — Tourney-Overlay

> **Ce guide est fait pour des novices complets.** Pas besoin de savoir programmer : suivez les étapes une par une. À la fin, vous aurez des overlays de tournoi professionnels dans OBS, synchronisés avec Challonge.

---

## 📋 Sommaire

1. [Qu'est-ce dont vous avez besoin ?](#1-qu-est-ce-dont-vous-avez-besoin-)
2. [Installer Docker](#2-installer-docker)
3. [Vérifier que Docker fonctionne](#3-vérifier-que-docker-fonctionne)
4. [Récupérer votre clé API Challonge](#4-récupérer-votre-clé-api-challonge)
5. [Lancer Tourney-Overlay avec Docker Compose](#5-lancer-tourney-overlay-avec-docker-compose)
6. [Ouvrir le tableau de bord (Dashboard)](#6-ouvrir-le-tableau-de-bord-dashboard)
7. [Connecter Challonge et choisir un tournoi](#7-connecter-challonge-et-choisir-un-tournoi)
8. [Ajouter les overlays dans OBS](#8-ajouter-les-overlays-dans-obs)
9. [Personnaliser (team tags, avatars, casters)](#9-personnaliser-team-tags-avatars-casters)
10. [Dépannage](#10-dépannage)

> 📸 **Astuce captures** : pour illustrer ce guide, faites des captures d'écran chez vous (`` Win+Shift+S `` sur Windows, `` Cmd+Shift+4 `` sur Mac) et placez-les dans un dossier `docs/`. Les emplacements suggérés sont indiqués à chaque étape entre crochets, ex : `[docs/dashboard-main.png]`.

---

## 1. Qu'est-ce dont vous avez besoin ?

| Élément | Pourquoi |
|---------|----------|
| Un ordinateur (Windows 10/11, macOS ou Linux) | Pour faire tourner le serveur en local |
| **Docker** | Le logiciel qui fait tourner Tourney-Overlay dans un « conteneur » isolé (pas besoin d'installer Python, etc.) |
| Une connexion internet | Pour télécharger l'image et parler à Challonge |
| Un compte [Challonge](https://challonge.com) | Pour récupérer les données de votre tournoi |
| [OBS Studio](https://obsproject.com/) | Pour diffuser (gratuit) |

> 💡 **C'est quoi Docker ?** Imaginez une boîte autonome qui contient tout le nécessaire pour faire tourner l'application. Vous ne touchez à rien d'autre sur votre PC. C'est la méthode la plus simple et la plus sûre.

---

## 2. Installer Docker

### 🪟 Sur Windows

1. Allez sur → https://www.docker.com/products/docker-desktop/
2. Cliquez **« Download for Windows »**.
3. Ouvrez le fichier `.exe` téléchargé.
4. Laissez toutes les cases cochées par défaut, cliquez **« Ok »** puis **« Install »**.
5. Redémarrez votre ordinateur si on vous le demande.
6. Au démarrage, ouvrez **Docker Desktop** depuis le menu Démarrer.

> 📸 *[docs/docker-desktop.png]* Capture suggérée : la fenêtre Docker Desktop avec la baleine 🐳 dans la barre des tâches.

> ⚠️ **Windows 10/11 Home** : Docker Desktop installe automatiquement le « WSL 2 » nécessaire. Laissez-le faire, ça peut prendre quelques minutes.

### 🍎 Sur macOS

1. Allez sur → https://www.docker.com/products/docker-desktop/
2. Cliquez **« Download for Mac »** (choisissez **Apple Silicon** si votre Mac est récent, sinon **Intel**).
3. Ouvrez le `.dmg`, glissez l'icône Docker dans le dossier **Applications**.
4. Ouvrez **Docker** depuis le Launchpad. Une petite baleine 🐳 apparaît en haut à droite de l'écran.

> 📸 *[docs/docker-desktop.png]* Capture suggérée : l'icône Docker dans la barre de menu macOS.

### 🐧 Sur Linux (Ubuntu/Debian)

Ouvrez un terminal (`Ctrl+Alt+T`) et collez ces lignes une par une :

```bash
# Mettre le système à jour
sudo apt update

# Installer les prérequis
sudo apt install -y ca-certificates curl gnupg

# Ajouter la clé et le dépôt Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Lancer Docker au démarrage
sudo systemctl enable --now docker
```

---

## 3. Vérifier que Docker fonctionne

Ouvrez un **terminal** (Invite de commandes sur Windows, Terminal sur Mac, déjà ouvert sur Linux) et tapez :

```bash
docker --version
docker compose version
```

Vous devriez voir quelque chose comme :
```
Docker version 27.0.0
Docker Compose version v2.28.0
```

> 📸 *[docs/terminal-docker-version.png]* Capture suggérée : la fenêtre terminal affichant les deux numéros de version.

✅ Si les deux commandes répondent avec un numéro de version, c'est bon ! Passez à l'étape suivante.

---

## 4. Récupérer votre clé API Challonge

1. Connectez-vous sur → https://challonge.com/settings/developer
2. Copiez votre **API Key** (une longue chaîne de lettres et chiffres).

> 📸 *[docs/challonge-api-key.png]* Capture suggérée : la page Developer Settings de Challonge avec la clé mise en évidence.

> 🔒 Cette clé ne sert qu'à lire/écrire vos tournois. Elle reste sur votre machine (dans le tableau de bord), elle n'est jamais envoyée ailleurs.

---

## 5. Lancer Tourney-Overlay avec Docker Compose

### Méthode A — Fichier docker-compose (recommandée)

Créez un fichier `docker-compose.yml` sur votre bureau avec ce contenu :

```yaml
services:
  tourney-overlay:
    image: ghcr.io/deihatchi/tourney-overlay:latest
    container_name: tourney-overlay
    ports:
      - "8002:8000"
    restart: unless-stopped
```

Puis dans un terminal, depuis le dossier où est le fichier :

```bash
docker compose up -d
```

Le terminal affiche le téléchargement de l'image, puis `Container tourney-overlay Started`. 🎉

> 📸 *[docs/terminal-docker-up.png]* Capture suggérée : le terminal montrant le téléchargement puis « Started ».

### Méthode B — Ligne de commande directe

Si vous préférez une seule commande :

```bash
docker run -d --name tourney-overlay -p 8002:8000 --restart unless-stopped ghcr.io/deihatchi/tourney-overlay:latest
```

> 💡 `8002` est le port sur lequel vous accéderez. Si ce port est occupé, changez-le (ex : `8003:8000`).

---

## 6. Ouvrir le tableau de bord (Dashboard)

Ouvrez votre navigateur (Chrome, Firefox, Edge) et allez sur :

```
http://localhost:8002
```

Vous voyez le tableau de bord de Tourney-Overlay. 🎨

> 📸 *[docs/dashboard-main.png]* Capture suggérée : l'écran principal du dashboard (panneau de configuration à gauche, thèmes/couleurs à droite).

---

## 7. Connecter Challonge et choisir un tournoi

1. Collez votre **clé API Challonge** dans le champ « Colle ta clé API… ».
2. Laissez **Pseudo** vide (sauf si vous utilisez un sous-domaine d'organisation Challonge).
3. Cliquez **⚡ CONNECTER**.
4. Sélectionnez votre **Tournoi** dans la liste.
5. Choisissez un **Match** si besoin.

Le tableau de bord affiche alors les matchs, le bracket, et les boutons pour copier les liens d'overlays.

> 📸 *[docs/dashboard-connected.png]* Capture suggérée : le dashboard après connexion, avec la liste des tournois et matchs.

---

## 8. Ajouter les overlays dans OBS

Dans OBS, pour **chaque** overlay que vous voulez afficher :

1. Cliquez **「＋」→ Source → Source de navigateur**.
2. Donnez un nom (ex : « Score »).
3. Dans **URL**, collez le lien généré par le tableau de bord (ex : `http://localhost:8002/overlay/score?match_id=123&tournament_id=456`).
4. Réglez la **Largeur** et **Hauteur** selon l'overlay (voir tableau ci-dessous).
5. Cochez **「Contrôler l'audio via OBS」** et **「Arrêter quand non visible」**.
6. Cliquez **OK**.

| Overlay | URL | Taille recommandée |
|---------|-----|-------------------|
| Bracket | `/overview?tournament_id=...` | 1920×1080 |
| Score | `/overlay/score?match_id=...&tournament_id=...` | 1920×200 |
| Score Below | `/overlay/score-below?match_id=...&tournament_id=...&offset_y=120` | 2×240 blocs |
| Recap | `/overlay/recap?tournament_id=...` | 1920×1080 |
| Casters | `/overlay/casters` | 1920×1080 |
| Notification | `/overlay/notification` | 500×300 |

> 📸 *[docs/obs-overlay.png]* Capture suggérée : la fenêtre « Propriétés de la source de navigateur » d'OBS avec l'URL remplie.

> ✨ Les overlays se mettent à jour **en temps réel** : dès que vous changez un score dans le tableau de bord, l'overlay OBS change instantanément. Pas besoin de recharger.

---

## 9. Personnaliser (team tags, avatars, casters)

Le tableau de bord permet beaucoup de personnalisation, sans toucher au code :

- **🏷️ Team Tags** : dans la section **Roster**, donnez un `[TAG]` à chaque joueur (ex : `BMS`, `ZEN`). Le tag s'affiche dans tous les overlays et suit le joueur même si vous inversez les positions.
- **🖼️ Avatars joueurs** : uploadez une image par joueur. Elle remplace l'avatar Gravatar de Challonge.
- **🎙️ Casters** : renseignez le nom + réseau (X/Twitch) de chaque caster, uploadez leur avatar (bouton 📷), et réglez **la durée d'affichage** (en secondes). Les cartes casters apparaissent puis disparaissent automatiquement.
- **🎨 Couleurs** : changez les couleurs primaire / secondaire / tertiaire du thème.
- **🌍 Langue** : basculez FR / EN en haut à droite.

> 📸 *[docs/dashboard-roster-casters.png]* Capture suggérée : la section Roster (team tags + avatars) et la section Commentateurs (casters) du dashboard.

> 📸 *[docs/overlay-casters.png]* Capture suggérée : l'overlay Casters en fonctionnement (avatars + noms sur les côtés).

---

## 10. Dépannage

| Problème | Solution |
|----------|----------|
| « Impossible de se connecter à localhost:8002 » | Vérifiez que Docker tourne et que le conteneur est démarré (`docker ps`). Attendez 10 s après `docker compose up`. |
| L'overlay reste vide | Vérifiez que le tournoi est bien sélectionné dans le dashboard et que `match_id`/`tournament_id` sont dans l'URL. |
| « Port 8002 already in use » | Changez le port dans `docker-compose.yml` (`8003:8000`) et utilisez `http://localhost:8003`. |
| Les overlays ne se mettent pas à jour | Cliquez **「SURVEILLER」** dans le dashboard pour activer le suivi temps réel (WebSocket). |
| Docker ne démarre pas sur Windows | Activez la virtualisation dans le BIOS et WSL 2 (Docker propose de le faire automatiquement). |

Pour tout arrêter :
```bash
docker compose down
```

Pour mettre à jour vers la dernière version :
```bash
docker compose pull
docker compose up -d
```

---

## 📚 Ressources

- [Dépôt GitHub](https://github.com/Deihatchi/tourney-overlay)
- [Challonge API](https://api.challonge.com/v1)
- [Documentation OBS](https://obsproject.com/wiki/)

**Licence** : PolyForm Noncommercial 1.0.0 — usage non commercial uniquement.
