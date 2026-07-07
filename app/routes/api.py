"""REST API routes for SF Overlay2."""

from __future__ import annotations

import urllib.error
import base64
import json
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse

from app.config import settings
from app.models import AppConfig, ChallongeConfig, GAME_THEMES, ScoreUpdate, SwapPlayers
from app.services import tournament
from app.services.websocket_manager import manager
from app.template_env import STATIC_DIR

router = APIRouter()

# ── In-memory config state ───────────────────────────────────────────────────
_current_config = AppConfig()
_polling_active = False

# Logo storage path
_LOGO_PATH = Path(STATIC_DIR) / "logo.png"


# ── Status ───────────────────────────────────────────────────────────────────
@router.get("/status")
async def get_status() -> dict:
    """Return current service status."""
    return {
        "configured": bool(tournament.get_api_key()),
        "polling": len(tournament._polling_tasks) > 0,
        "service": _current_config.service,
        "game": _current_config.game,
        "tournament_name": "",
        "match_count": 0,
    }


# ── Version ──────────────────────────────────────────────────────────────────
@router.get("/version")
async def get_version() -> dict:
    """Return application version."""
    import importlib.metadata
    try:
        version = importlib.metadata.version("tourney-overlay")
    except importlib.metadata.PackageNotFoundError:
        version = "dev"
    return {"version": version}


# ── Games ────────────────────────────────────────────────────────────────────
@router.get("/games")
async def get_games() -> dict:
    """Return all 24 game themes."""
    games = []
    for key, theme in GAME_THEMES.items():
        games.append({
            "id": key,
            "name": theme["name"],
            "emoji": theme["emoji"],
            "category": theme["cat"],
            "colors": {
                "primary": theme["primary"],
                "secondary": theme["secondary"],
                "tertiary": theme["tertiary"],
            },
            "animation": theme["anim"],
            "icon": theme.get("icon", ""),
        })
    return {"games": games}


# ── Config ───────────────────────────────────────────────────────────────────
@router.get("/config")
async def get_config() -> AppConfig:
    """Return current configuration."""
    return _current_config


@router.post("/config")
async def save_config(config: AppConfig) -> dict:
    """Save full configuration. Applies game theme if not custom."""
    global _current_config
    _current_config = config

    # Store API key if provided
    if config.api_key:
        tournament.set_api_key(config.api_key)

    # Apply game theme if not custom
    if config.game != "custom" and config.game in GAME_THEMES:
        theme = GAME_THEMES[config.game]
        _current_config.primary_color = theme["primary"]
        _current_config.secondary_color = theme["secondary"]
        _current_config.tertiary_color = theme["tertiary"]
        _current_config.animation_style = theme["anim"]

    return {"status": "ok", "message": "Configuration sauvegardée", "config": _current_config.model_dump()}


# ── Configure (Challonge API key setup) ─────────────────────────────────────
@router.api_route("/configure", methods=["GET", "POST"])
async def configure(config: ChallongeConfig = None):
    """Configure Challonge API credentials (POST) or return current (GET)."""
    global _current_config

    if config is None:
        return ChallongeConfig(
            api_key=_current_config.api_key,
            username=_current_config.username or "",
        )

    # Verify the key
    valid = tournament.verify_api_key(config.api_key)
    if not valid:
        raise HTTPException(status_code=400, detail="Clé API Challonge invalide. Vérifie ta clé sur challonge.com/fr/settings/developer")

    # Store the key
    tournament.set_api_key(config.api_key)
    _current_config.api_key = config.api_key
    _current_config.username = config.username or ""

    return {"status": "ok", "message": "Configuration réussie !"}


# ── Tournaments ──────────────────────────────────────────────────────────────
@router.get("/tournaments")
async def get_tournaments() -> dict:
    """List tournaments from Challonge."""
    api_key = tournament.get_api_key()
    if not api_key:
        raise HTTPException(status_code=400, detail="Configure d'abord ta clé API Challonge")

    username = _current_config.username or settings.challonge_username
    try:
        tournaments = tournament.fetch_tournaments(api_key, username)
    except ValueError as e:
        # Challonge API error (invalid subdomain, auth, etc.)
        raise HTTPException(status_code=400, detail=f"Erreur Challonge: {e}")
    return {"tournaments": [t.model_dump() for t in tournaments]}


@router.get("/tournaments/{tournament_id}/matches")
async def get_matches(tournament_id: int) -> dict:
    """List matches for a tournament with participant info."""
    api_key = tournament.get_api_key()
    if not api_key:
        raise HTTPException(status_code=400, detail="Configure d'abord ta clé API Challonge")

    username = _current_config.username or settings.challonge_username
    try:
        matches = tournament.fetch_matches(api_key, tournament_id, username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Erreur Challonge: {e}")
    return {"matches": [m.model_dump() for m in matches]}


# ── Roster (participants + players.json) ─────────────────────────────────────
@router.get("/tournaments/{tournament_id}/participants")
async def get_participants(tournament_id: int) -> dict:
    """List participants merged with local roster (team_tag + avatar)."""
    api_key = tournament.get_api_key()
    if not api_key:
        raise HTTPException(status_code=400, detail="Configure d'abord ta clé API Challonge")

    username = _current_config.username or settings.challonge_username
    try:
        parts = tournament.get_participants(api_key, tournament_id, username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Erreur Challonge: {e}")
    return {"participants": parts}


@router.post("/update_tag")
async def update_tag(payload: dict) -> dict:
    """Update a player's team tag in players.json."""
    pseudo = payload.get("pseudo")
    team_tag = payload.get("team_tag", "")
    if not pseudo:
        raise HTTPException(status_code=400, detail="pseudo requis")
    entry = tournament.set_player_tag(pseudo, team_tag)
    return {"status": "ok", "pseudo": pseudo, "team_tag": entry.get("team_tag", "")}


@router.post("/upload_avatar/{pseudo:path}")
async def upload_avatar(pseudo: str, file: UploadFile = File(...)) -> dict:
    """Save an avatar image to /static/avatars/ and update players.json."""
    # Determine extension from uploaded filename
    original = file.filename or ""
    ext = os.path.splitext(original)[1].lower()
    if ext not in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
        ext = ".png"
    # Filesystem-safe filename (slug of pseudo) keeps players.json simple
    filename = tournament._slugify(pseudo) + ext
    avatars_dir = Path(STATIC_DIR) / "avatars"
    avatars_dir.mkdir(parents=True, exist_ok=True)
    dest = avatars_dir / filename
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Fichier vide")
    # Basic image size guard
    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image trop lourde (max 2 Mo)")
    with open(dest, "wb") as f:
        f.write(content)
    entry = tournament.set_player_avatar(pseudo, filename)
    return {
        "status": "ok",
        "pseudo": pseudo,
        "avatar_filename": entry.get("avatar_filename", ""),
        "avatar_url": f"/static/avatars/{filename}",
    }


@router.post("/poll/start")
async def start_poll(payload: dict) -> dict:
    """Start polling a tournament for match updates."""
    global _polling_active
    tournament_id = payload.get("tournament_id", 0)
    interval = payload.get("interval", 15)

    if not tournament_id:
        raise HTTPException(status_code=400, detail="tournament_id requis")

    api_key = tournament.get_api_key()
    if not api_key:
        raise HTTPException(status_code=400, detail="Configure d'abord ta clé API Challonge")

    tournament.start_polling(tournament_id, interval)
    _polling_active = True

    return {"status": "ok", "message": f"Surveillance du tournoi #{tournament_id} activée (intervalle: {interval}s)"}


@router.post("/poll/stop")
async def stop_poll() -> dict:
    """Stop all polling tasks."""
    global _polling_active
    tournament.stop_polling()
    _polling_active = False
    return {"status": "ok", "message": "Surveillance arrêtée"}


# ── Match Score ──────────────────────────────────────────────────────────────
@router.post("/match/score")
async def update_score(update: ScoreUpdate) -> dict:
    """Update match score on Challonge and broadcast via WebSocket."""
    api_key = tournament.get_api_key()
    if not api_key:
        raise HTTPException(status_code=400, detail="Clé API non configurée")

    scores_csv = f"{update.player1_score}-{update.player2_score}"
    try:
        result = tournament.update_match_score(
            update.tournament_id,
            update.match_id,
            scores_csv,
            update.winner_id,
        )

        # Persist manual team tag overrides (survive Challonge polls)
        tournament.set_team_tag_override(
            update.tournament_id,
            update.match_id,
            update.player1_team_tag,
            update.player2_team_tag,
        )

        # Re-fetch and broadcast via WebSocket
        try:
            matches = tournament.fetch_matches(api_key, update.tournament_id)
            for m in matches:
                if m.id == update.match_id:
                    m.bracket_reset = update.bracket_reset
                    await manager.broadcast_match_update(m)
                    if m.state.value == "completed":
                        await manager.broadcast_notification(m)
                    break
        except Exception:
            pass

        return {"status": "ok", "message": f"Score {scores_csv} enregistré sur Challonge"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur Challonge: {str(e)[:100]}")


@router.post("/match/swap")
async def swap_players(update: SwapPlayers) -> dict:
    """Swap Player 1 and Player 2 on Challonge."""
    api_key = tournament.get_api_key()
    if not api_key:
        raise HTTPException(status_code=400, detail="Clé API non configurée")

    try:
        result = tournament.swap_players(update.tournament_id, update.match_id)

        # Re-fetch and broadcast via WebSocket
        try:
            matches = tournament.fetch_matches(api_key, update.tournament_id)
            for m in matches:
                if m.id == update.match_id:
                    # fetch_matches already reflects the Challonge swap (IDs swapped),
                    # so player names, team tags and scores are in the correct order.
                    await manager.broadcast_match_update(m)
                    if m.state.value == "completed":
                        await manager.broadcast_notification(m)
                    break
        except Exception:
            pass

        return {"status": "ok", "message": "Joueurs inversés"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur Challonge: {str(e)[:100]}")


@router.post("/match/reset-bracket")
async def reset_bracket(update: SwapPlayers) -> dict:
    """Reset match scores to 0-0 for bracket reset (Grand Finals)."""
    api_key = tournament.get_api_key()
    if not api_key:
        raise HTTPException(status_code=400, detail="Clé API non configurée")

    try:
        result = tournament.reset_bracket(update.tournament_id, update.match_id)

        # Re-fetch and broadcast via WebSocket with bracket_reset flag
        try:
            matches = tournament.fetch_matches(api_key, update.tournament_id)
            for m in matches:
                if m.id == update.match_id:
                    m.bracket_reset = True
                    await manager.broadcast_match_update(m)
                    break
        except Exception:
            pass

        return {"status": "ok", "message": "Bracket Reset: scores remis à 0-0"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur Challonge: {str(e)[:100]}")


@router.get("/casters")
async def get_casters() -> dict:
    """Return current caster configuration."""
    return {
        "caster1_name": _current_config.caster1_name,
        "caster1_social": _current_config.caster1_social,
        "caster1_avatar": _current_config.caster1_avatar,
        "caster1_avatar_url": (tournament._AVATAR_URL_PREFIX + _current_config.caster1_avatar) if _current_config.caster1_avatar else "",
        "caster2_name": _current_config.caster2_name,
        "caster2_social": _current_config.caster2_social,
        "caster2_avatar": _current_config.caster2_avatar,
        "caster2_avatar_url": (tournament._AVATAR_URL_PREFIX + _current_config.caster2_avatar) if _current_config.caster2_avatar else "",
        "display_duration": _current_config.caster_display_duration,
    }


@router.post("/casters")
async def save_casters(payload: dict) -> dict:
    """Save caster configuration."""
    global _current_config
    _current_config.caster1_name = payload.get("caster1_name", "")
    _current_config.caster1_social = payload.get("caster1_social", "")
    # avatar filenames are managed via /api/upload_caster_avatar; keep existing if not provided
    if "caster1_avatar" in payload:
        _current_config.caster1_avatar = payload.get("caster1_avatar", "")
    if "caster2_avatar" in payload:
        _current_config.caster2_avatar = payload.get("caster2_avatar", "")
    _current_config.caster2_name = payload.get("caster2_name", "")
    _current_config.caster2_social = payload.get("caster2_social", "")
    if "caster_display_duration" in payload:
        try:
            _current_config.caster_display_duration = max(0, int(payload.get("caster_display_duration", 0)))
        except (ValueError, TypeError):
            pass
    return {"status": "ok", "message": "Casters sauvegardés"}


@router.post("/upload_caster_avatar/{num}")
async def upload_caster_avatar(num: int, file: UploadFile = File(...)) -> dict:
    """Upload an avatar for caster 1 or 2 (num=1|2)."""
    if num not in (1, 2):
        raise HTTPException(status_code=400, detail="num must be 1 or 2")
    original = file.filename or ""
    ext = os.path.splitext(original)[1].lower()
    if ext not in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
        ext = ".png"
    filename = f"caster{num}{ext}"
    avatars_dir = Path(STATIC_DIR) / "avatars"
    avatars_dir.mkdir(parents=True, exist_ok=True)
    dest = avatars_dir / filename
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Fichier vide")
    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image trop lourde (max 2 Mo)")
    with open(dest, "wb") as f:
        f.write(content)
    global _current_config
    if num == 1:
        _current_config.caster1_avatar = filename
    else:
        _current_config.caster2_avatar = filename
    return {
        "status": "ok",
        "num": num,
        "avatar_filename": filename,
        "avatar_url": f"/static/avatars/{filename}",
    }


# ── Logo ─────────────────────────────────────────────────────────────────────
@router.post("/logo")
async def upload_logo(payload: dict = None) -> dict:
    """Upload a base64-encoded logo image."""
    data = (payload or {}).get("logo", "")
    if not data:
        return {"status": "ok", "url": "/static/logo.png" if _LOGO_PATH.exists() else ""}

    # Strip data URL prefix if present
    if "," in data:
        data = data.split(",", 1)[1]

    try:
        img_bytes = base64.b64decode(data)
        _LOGO_PATH.parent.mkdir(parents=True, exist_ok=True)
        _LOGO_PATH.write_bytes(img_bytes)
        return {"status": "ok", "url": "/static/logo.png"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur logo: {str(e)[:100]}")


@router.get("/logo")
async def get_logo() -> dict:
    """Return the logo URL if it exists."""
    return {"url": "/static/logo.png" if _LOGO_PATH.exists() else ""}


# ── Translations ─────────────────────────────────────────────────────────────
TRANSLATIONS = {
    "fr": {
        "app_name": "Tournament Overlay",
        "service": "Service",
        "game": "Jeu",
        "api": "API",
        "api_key": "Clé API Challonge",
        "username": "Nom d'utilisateur (opt.)",
        "connect": "Connecter",
        "connected": "Connecté",
        "tournament": "Tournoi",
        "matches": "Matchs",
        "style": "Style de l'overlay",
        "primary": "Couleur principale",
        "secondary": "Couleur secondaire",
        "tertiary": "Couleur tertiaire (winner)",
        "animation": "Animation",
        "resolution": "Résolution OBS",
        "overlays": "Overlays",
        "bracket_overlay": "Bracket",
        "recap_overlay": "Récap",
        "score_overlay": "Score",
        "notification_overlay": "Notification",
        "open": "Ouvrir",
        "copy": "Copier",
        "copied": "Copié",
        "watch": "Surveiller",
        "stop": "Arrêter",
        "edit_score": "Éditer le score",
        "winner": "Gagnant",
        "send": "Envoyer à Challonge",
        "cancel": "Annuler",
        "select_match": "Sélectionne un match",
        "select_tourney": "Sélectionne un tournoi",
        "loading": "Chargement...",
        "error": "Erreur",
        "success": "Succès",
        "logo": "Logo personnalisé",
        "upload_logo": "Choisir un fichier",
        "language": "Langue",
        "score": "Score",
        "match_completed": "Match terminé",
        "score_updated": "Score mis à jour",
        "preview": "Aperçu",
                "optional": "optionnel",
                "swap_players": "Inverser P1/P2",
                "bracket_reset": "Bracket Reset",
                "casters": "Commentateurs",
                "caster1_name": "Caster 1 — Nom",
                "caster1_social": "Caster 1 — Réseau",
                "caster2_name": "Caster 2 — Nom",
                "caster2_social": "Caster 2 — Réseau",
                "save_casters": "Sauvegarder",
                "team_tag": "Tag équipe"
            },
            "en": {
                "app_name": "Tournament Overlay",
                "service": "Service",
                "game": "Game",
                "api": "API",
                "api_key": "Challonge API Key",
                "username": "Username (opt.)",
                "connect": "Connect",
                "connected": "Connected",
                "tournament": "Tournament",
                "matches": "Matches",
                "style": "Overlay Style",
                "primary": "Primary color",
                "secondary": "Secondary color",
                "tertiary": "Tertiary color (winner)",
                "animation": "Animation",
                "resolution": "OBS Resolution",
                "overlays": "Overlays",
                "bracket_overlay": "Bracket",
                "recap_overlay": "Recap",
                "score_overlay": "Score",
                "notification_overlay": "Notification",
                "open": "Open",
                "copy": "Copy",
                "copied": "Copied",
                "watch": "Watch",
                "stop": "Stop",
                "edit_score": "Edit score",
                "winner": "Winner",
                "send": "Send to Challonge",
                "cancel": "Cancel",
                "select_match": "Select a match",
                "select_tourney": "Select a tournament",
                "loading": "Loading...",
                "error": "Error",
                "success": "Success",
                "logo": "Custom logo",
                "upload_logo": "Choose file",
                "language": "Language",
                "score": "Score",
                "match_completed": "Match completed",
                "score_updated": "Score updated",
                "preview": "Preview",
                "optional": "optional",
                "swap_players": "Swap P1/P2",
                "bracket_reset": "Bracket Reset",
                "casters": "Casters",
                "caster1_name": "Caster 1 — Name",
                "caster1_social": "Caster 1 — Social",
                "caster2_name": "Caster 2 — Name",
                "caster2_social": "Caster 2 — Social",
                "save_casters": "Save",
                "team_tag": "Team Tag"
            },
}


@router.get("/translations")
async def get_translations() -> dict:
    """Return i18n translations (FR/EN)."""
    return TRANSLATIONS


# ── Caster Swap ───────────────────────────────────────────────────────────────
@router.post("/casters/swap")
async def swap_casters() -> dict:
    """Swap caster 1 and caster 2."""
    global _current_config
    _current_config.caster1_name, _current_config.caster2_name = _current_config.caster2_name, _current_config.caster1_name
    _current_config.caster1_social, _current_config.caster2_social = _current_config.caster2_social, _current_config.caster1_social
    _current_config.caster1_avatar, _current_config.caster2_avatar = _current_config.caster2_avatar, _current_config.caster1_avatar
    return {"status": "ok", "message": "Casteurs inversés"}
