# Tourney-Overlay — Tournament Overlay for OBS

> **Animated tournament overlays** synced with **Challonge** brackets. Built for fighting game streams (Street Fighter, Tekken, Guilty Gear, etc.).

---

## 🎮 Features

| Feature | Description |
|---------|-------------|
| **Live Score Overlay** | Real-time match scores with player names, avatars, round indicators |
| **Winner Notification** | Animated "Match Complete" popup with winner highlight |
| **Bracket Overview** | Full tournament bracket with progress tracking |
| **24 Game Themes** | Pre-configured color schemes & animations per game |
| **Web Dashboard** | Configure API, pick tournament/match, copy OBS URLs |
| **WebSocket Updates** | Instant score changes pushed to overlays |
| **Challonge Integration** | Read tournaments, matches, participants, avatars |
| **Score Editing** | Update scores directly from dashboard → syncs to Challonge |

---

## 🚀 Quick Start

### 1. Get your Challonge API Key
1. Go to **[challonge.com/settings/developer](https://challonge.com/settings/developer)**
2. Copy your **API Key**

### 2. Configure & Run

**Option A: Docker Compose (recommended)**
```bash
git clone https://github.com/Deihatchi/tourney-overlay.git
cd tourney-overlay

# Configure
cp .env.example .env
# Edit .env with your API key
nano .env

# Launch
docker compose up -d --build
```

**Option B: Docker directly**
```bash
docker build -t tourney-overlay .
docker run -d \
  --name tourney-overlay \
  -p 8002:8000 \
  -e SF_CHALLENGE_API_KEY=your_key_here \
  -e SF_CHALLENGE_USERNAME=your_org \
  tourney-overlay
```

### 3. Open Dashboard
→ **http://localhost:8002** (or your server IP)

### 4. Connect & Go
1. Paste **API Key** → leave **Pseudo** empty (unless you use an org subdomain)
2. Click **⚡ Connecter**
3. Select a **Tournoi** → pick a **Match**
4. Copy the **3 OBS URLs** (Score / Notification / Bracket)
5. Add as **Browser Source** in OBS (transparent background)

---

## 📁 Project Structure

```
tourney-overlay/
├── docker-compose.yml      # Compose config
├── Dockerfile              # Multi-stage build
├── pyproject.toml          # Python deps
├── deploy.sh               # Portainer deploy script
├── .env.example            # Env template
├── .gitignore
├── README.md
└── app/
    ├── main.py             # Entry point
    ├── __init__.py         # FastAPI factory + CORS
    ├── config.py           # Pydantic settings
    ├── models.py           # Pydantic models
    ├── template_env.py     # Jinja2 setup
    ├── routes/
    │   ├── api.py          # REST: /api/tournaments, /api/matches, /api/configure...
    │   ├── overlays.py     # Overlay endpoints: /overlay/score, /overlay/notification, /overview
    │   └── websocket_routes.py  # WS: /ws/dashboard
    ├── services/
    │   ├── tournament.py   # Challonge API (urllib, no httpx)
    │   └── websocket_manager.py
    └── templates/
        ├── dashboard.html  # Single-file WebUI (~800 lines)
        ├── overlay_score.html
        ├── overlay_notification.html
        └── overview_overlay.html
```

---

## 🎨 Game Themes (24 included)

| Category | Games |
|----------|-------|
| **Fighting** | SF6, SFV, SFIV, SFIII, SFII, Tekken 8/7, GG Strive, BB CF, DBFZ, MK1, UNI, KOF XV, GBVS Rising |
| **FPS** | Valorant, CS2, Overwatch 2 |
| **MOBA** | LoL, Dota 2 |
| **Sports** | Rocket League, EA Sports FC |

Each theme defines: `primary` / `secondary` / `tertiary` colors + animation (`slide`, `fade`, `zoom`, `glitch`, `fire`, `pulse`, `neon_sweep`, `matrix`)

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI + Uvicorn |
| **API Client** | `urllib` (stdlib — SSL-safe in Docker) |
| **Templates** | Jinja2 |
| **Real-time** | Native Starlette WebSockets |
| **Container** | Docker (multi-stage, ~120MB) |
| **Deployment** | Portainer / Docker Compose |

---

## 🔧 Configuration

| Env Var | Required | Default | Description |
|---------|----------|---------|-------------|
| `SF_CHALLENGE_API_KEY` | **Yes** | — | Challonge API key |
| `SF_CHALLENGE_USERNAME` | No | `""` | Org subdomain (if applicable) |
| `SF_HOST` | No | `0.0.0.0` | Bind address |
| `SF_PORT` | No | `8000` | Internal port |

---

## 📡 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/status` | Service status |
| `GET` | `/api/games` | List 24 game themes |
| `POST` | `/api/configure` | Save API key + username |
| `GET` | `/api/tournaments` | List tournaments |
| `GET` | `/api/tournaments/{id}/matches` | List matches with participants |
| `POST` | `/api/poll/start` | Start WebSocket polling |
| `POST` | `/api/poll/stop` | Stop polling |
| `POST` | `/api/match/score` | Update score on Challonge |
| `GET/POST` | `/api/logo` | Upload/get custom logo |
| `GET` | `/overlay/score` | Score overlay (OBS) |
| `GET` | `/overlay/notification` | Winner notification (OBS) |
| `GET` | `/overview` | Bracket overview (OBS) |
| `WS` | `/ws/dashboard` | Real-time updates |

---

## 🐳 Deploy to Portainer

The included `deploy.sh` handles Portainer deployment:

```bash
# Requires Portainer token in /tmp/token_b64.txt (base64 encoded)
bash deploy.sh
```

What it does:
1. Deletes old container
2. Builds image via Docker API proxy
3. Creates container on port 8002
4. Starts it

---

## 🎯 OBS Setup

| Overlay | URL Params | Recommended Size |
|---------|------------|------------------|
| **Score** | `game`, `primary`, `secondary`, `tertiary`, `animation`, `match_id`, `tournament_id`, `res`, `logo` | 1920×200 |
| **Notification** | `game`, `primary`, `secondary`, `tertiary`, `animation`, `logo` | 500×300 |
| **Bracket** | `game`, `primary`, `secondary`, `tertiary`, `animation`, `tournament_id`, `logo` | 1920×1080 |

**Important**: In OBS Browser Source → check **"Control audio via OBS"** + **"Shutdown when not visible"** → set **Background** to transparent.

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📄 License

**PolyForm Noncommercial License 1.0.0** — see [LICENSE](LICENSE) for details.

Noncommercial use only. For commercial licensing, contact the maintainers.

---

## 🙏 Credits

- **Challonge API** for bracket data
- **Gravatar** for player avatars
- **Google Fonts**: Orbitron, Rajdhani, Inter
- Built for the FGC streaming community ⚡