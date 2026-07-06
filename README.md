# Tourney-Overlay

> **Tournament overlay system for OBS** — real-time brackets, scores, notifications synced with **Challonge**. Built for fighting game streams (SF6, Tekken 8, Guilty Gear, etc.).

<p align="center">
  <img src="https://img.shields.io/github/v/tag/Deihatchi/tourney-overlay?label=version&style=flat-square" alt="version">
  <img src="https://img.shields.io/static/v1?label=license&message=PolyForm+Noncommercial&color=blue&style=flat-square" alt="license">
</p>

---

## 🎮 Features

### Overlays (OBS Browser Sources)

| Overlay | URL | Size | Description |
|---------|-----|------|-------------|
| **Bracket** | `/overview?tournament_id=...` | 1920×1080 | Full tournament bracket, round filtering, winner highlight gold |
| **Score** | `/overlay/score?match_id=...&tournament_id=...` | 1920×200 | Centered score bar with player names, avatars, character names |
| **Score Below** | `/overlay/score-below?match_id=...&tournament_id=...` | 2×240 blocks | **New** — Two independent blocks (one per player) placed under health bars, ideal for SF6-style layouts |
| **Recap** | `/overlay/recap?tournament_id=...` | 1920×1080 | **New** — All tournament matches in reverse round order, winner highlighted |
| **Notification** | `/overlay/notification` | 500×300 | Animated toast notifications for match start, score update, match complete, player qualified |

### Dashboard

| Feature | Description |
|---------|-------------|
| **Connected via API key** | Enter your Challonge API key in the dashboard — **no env vars needed** |
| **Game themes** | 24 pre-configured fighting game themes (SF6, Tekken 8, GG Strive, MK1, etc.) |
| **Custom colors** | Override primary/secondary/tertiary colors for any theme |
| **Score editing** | Update match scores from dashboard — syncs back to Challonge in real time |
| **Auto-generated URLs** | Copy-paste overlay URLs directly into OBS Browser Sources |
| **FR / EN** | Full French and English interface |
| **Real-time WebSocket** | Instant updates pushed to all overlays — no page refresh needed |

### Technical

- **Real-time WebSocket** — score changes, match completions pushed instantly to all overlays
- **24 game themes** — each with custom `primary` / `secondary` / `tertiary` colors + unique CSS animations (slide, fade, zoom, glitch, fire, pulse, neon sweep, matrix)
- **Winner detection** — gold highlight on winner name in bracket, score, recap, and notification overlays
- **Player avatars** — Gravatar integration
- **Character display** — per-player character name shown in score overlays
- **Round filtering** — bracket shows only the current active round
- **Completion tracking** — progress bar per tournament based on actual completed matches

---

## 🚀 Quick Start

### 1. Get your Challonge API Key

Go to **[challonge.com/settings/developer](https://challonge.com/settings/developer)** and copy your API Key.

### 2. Run with Docker

```bash
# Pull the latest image
docker pull ghcr.io/deihatchi/tourney-overlay:latest

# Run it
docker run -d \
  --name tourney-overlay \
  -p 8002:8000 \
  --restart unless-stopped \
  ghcr.io/deihatchi/tourney-overlay:latest
```

**No API key needed at launch** — you enter it in the dashboard UI.

### 3. Open Dashboard

→ **http://localhost:8002** (or your server IP)

### 4. Connect & Go

1. Paste your **API Key** → leave **Pseudo** empty (unless you use a Challonge org subdomain)
2. Click **⚡ Connecter**
3. Select a **Tournoi** → pick a **Match**
4. Copy overlay URLs
5. Add as **Browser Source** in OBS (transparent background)

---

### Docker Compose

```yaml
services:
  tourney-overlay:
    image: ghcr.io/deihatchi/tourney-overlay:latest
    container_name: tourney-overlay
    ports:
      - "8002:8000"
    restart: unless-stopped
```

> API key is configured via the dashboard — no env vars required.

---

## 🎨 Game Themes (24 included)

| Category | Games |
|----------|-------|
| **Fighting** | SF6, SFV, SFIV, SFIII, SFII, Tekken 8/7, GG Strive, BB CF, DBFZ, MK1, UNI, KOF XV, GBVS Rising |
| **FPS** | Valorant, CS2, Overwatch 2 |
| **MOBA** | LoL, Dota 2 |
| **Sports** | Rocket League, EA Sports FC |

---

## 📡 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/version` | Deployed version |
| `GET` | `/api/status` | Service status + active tournament |
| `GET` | `/api/games` | List 24 game themes |
| `POST` | `/api/configure` | Save API key + username |
| `GET` | `/api/tournaments` | List tournaments with completion % |
| `GET` | `/api/tournaments/{id}/matches` | List matches with participants |
| `POST` | `/api/poll/start` | Start WebSocket polling for a tournament |
| `POST` | `/api/poll/stop` | Stop polling |
| `POST` | `/api/match/score` | Update match score on Challonge |
| `GET` | `/overlay/score` | Score overlay (centered bar) |
| `GET` | `/overlay/score-below` | Score overlay (two blocks, under health bars) |
| `GET` | `/overlay/notification` | Winner notification toast |
| `GET` | `/overlay/recap` | All matches recap |
| `GET` | `/overview` | Bracket overview |
| `WS` | `/ws/dashboard` | Real-time dashboard updates |
| `WS` | `/ws/overlay/{match_id}` | Real-time score overlay updates |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI + Uvicorn |
| **API Client** | `urllib` (stdlib — SSL-safe in Docker) |
| **Templates** | Jinja2 |
| **Real-time** | Native Starlette WebSockets |
| **Container** | Docker multi-stage (~120MB) |
| **Fonts** | Orbitron (e-sports), Rajdhani, Inter |

---

## 🐳 Deploy via Portainer

The included `deploy.sh` script deploys via Portainer's Docker API proxy:

```bash
# Requires base64-encoded Portainer API token in /tmp/token_b64.txt
bash deploy.sh
```

Or use the official GHCR image directly in Portainer:
- **Image**: `ghcr.io/deihatchi/tourney-overlay:latest`
- **Port mapping**: `8002` ← `8000` (internal)
- **Restart policy**: `unless-stopped`

---

## 🎯 OBS Setup Tips

- Use **Browser Source** with transparent background
- Recommended sizes in the table above
- Check **"Control audio via OBS"** and **"Shutdown when not visible"**
- Append `?lang=en` for English interface
- Customize colors with `&primary=...&secondary=...&tertiary=...`
- Adjust Score Below position with `&offset_y=180` (pixels from top)

---

## 🏗️ Project Structure

```
tourney-overlay/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── deploy.sh
├── .env.example
├── CHANGELOG.md
├── CONTRIBUTING.md
├── README.md
├── LICENSE
└── app/
    ├── main.py
    ├── __init__.py             # FastAPI factory + CORS
    ├── config.py               # Pydantic settings
    ├── models.py               # Pydantic models
    ├── template_env.py         # Jinja2 setup
    ├── routes/
    │   ├── api.py              # REST endpoints
    │   ├── overlays.py         # Overlay HTML routes
    │   └── websocket_routes.py # WS endpoints
    ├── services/
    │   ├── tournament.py       # Challonge API client
    │   └── websocket_manager.py
    └── templates/
        ├── dashboard.html
        ├── overlay_score.html
        ├── overlay_score_below.html
        ├── overlay_notification.html
        ├── overlay_recap.html
        └── overview_overlay.html
```

---

## 📄 License

**PolyForm Noncommercial License 1.0.0** — see [LICENSE](LICENSE) for details.

Noncommercial use only. For commercial licensing, contact the maintainers.

---

## 🙏 Credits

- **[Challonge](https://challonge.com)** — tournament bracket API
- **[Gravatar](https://gravatar.com)** — player avatars
- **Google Fonts** — Orbitron, Rajdhani, Inter
- Built for the FGC streaming community ⚡🔥
