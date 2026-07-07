"""Challonge API service using urllib (not httpx) for Docker SSL compatibility."""

from __future__ import annotations

import asyncio
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from app.models import MatchInfo, PlayerInfo, TournamentInfo
from app.services.websocket_manager import manager

CHALLONGE_BASE = "https://api.challonge.com/v1"

# Global API key storage (set at runtime)
_api_key: str = ""

# Active polling tasks
_polling_tasks: dict[int, asyncio.Task] = {}


def set_api_key(key: str) -> None:
    """Store the Challonge API key globally."""
    global _api_key
    _api_key = key


def get_api_key() -> str:
    """Return the currently stored API key."""
    return _api_key


def _headers() -> dict[str, str]:
    return {"User-Agent": "SF-Overlay/2.0"}


def _build_url(endpoint: str, params: dict[str, str] | None = None) -> str:
    """Build a full Challonge API URL with query params."""
    if params is None:
        params = {}
    # Always include API key
    params["api_key"] = _api_key
    query = urllib.parse.urlencode(params)
    return f"{CHALLONGE_BASE}{endpoint}?{query}"


def _get(url: str) -> dict[str, Any] | list[Any]:
    """Perform a GET request and return parsed JSON. Raises ValueError on API error."""
    req = urllib.request.Request(url, headers=_headers())
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        raise ValueError(f"Challonge API error {e.code}: {body}")
    except urllib.error.URLError as e:
        raise ValueError(f"Network error: {e.reason}")


def _put(url: str, data: dict[str, str]) -> dict[str, Any]:
    """Perform a PUT request with form-encoded body and return parsed JSON. Raises ValueError on API error."""
    body = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="PUT", headers=_headers())
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        raise ValueError(f"Challonge API error {e.code}: {body}")
    except urllib.error.URLError as e:
        raise ValueError(f"Network error: {e.reason}")


# ── Public API ───────────────────────────────────────────────────────────────

def verify_api_key(api_key: str) -> bool:
    """Verify a Challonge API key by fetching the tournament list."""
    global _api_key
    previous = _api_key
    _api_key = api_key
    try:
        url = _build_url("/tournaments.json")
        _get(url)
        return True
    except Exception:
        _api_key = previous
        return False


def fetch_tournaments(api_key: str, username: str = "") -> list[TournamentInfo]:
    """Fetch all tournaments for the given API key."""
    global _api_key
    _api_key = api_key

    params: dict[str, str] = {}
    # Do NOT pass subdomain if empty (Challonge returns 422)
    if username:
        params["subdomain"] = username

    url = _build_url("/tournaments.json", params)
    raw = _get(url)

    tournaments: list[TournamentInfo] = []
    if isinstance(raw, list):
        for item in raw:
            t = item.get("tournament", {})
            state = t.get("state", "")
            # Calculate real completion percentage from matches
            comp = 0.0
            if state == "complete":
                comp = 100.0
            elif state in ("underway", "in_progress"):
                try:
                    t_matches = fetch_matches(api_key, t["id"], username)
                    total = len(t_matches)
                    if total > 0:
                        completed = sum(1 for m in t_matches if m.state in ("complete", "completed"))
                        comp = round(completed / total * 100, 1)
                except Exception:
                    comp = float(t.get("progress", 0) or 0)
            tournaments.append(
                TournamentInfo(
                    id=t.get("id", 0),
                    name=t.get("name", ""),
                    url=t.get("full_challonge_url", ""),
                    game_name=t.get("game_name") or "",
                    state=state,
                    tournament_type=t.get("tournament_type", "single elimination"),
                    participants_count=t.get("participants_count", 0),
                    progress=comp,
                )
            )
    return tournaments


def _parse_name_with_tag(full_name: str) -> tuple[str, str]:
    """Parse a participant name to extract team tag and player name.
    
    Expected formats:
    - "[TAG] PlayerName" -> ("TAG", "PlayerName")
    - "TAG PlayerName" -> ("TAG", "PlayerName")
    - "PlayerName" -> ("", "PlayerName")
    """
    name = full_name.strip()
    if not name:
        return ("", "")
    
    # Check for [TAG] format
    if name.startswith("[") and "]" in name:
        end = name.index("]")
        tag = name[1:end].strip()
        player_name = name[end+1:].strip()
        return (tag, player_name)
    
    # Check for space-separated tag (first word if it looks like a tag: all caps, 2-5 chars)
    parts = name.split(" ", 1)
    if len(parts) == 2 and parts[0].isupper() and 2 <= len(parts[0]) <= 5:
        return (parts[0], parts[1])
    
    return ("", name)


def _fetch_participants(api_key: str, tournament_id: int, username: str = "") -> dict[int, dict]:
    """Fetch participants for a tournament and return a dict keyed by participant id."""
    params: dict[str, str] = {}
    if username:
        params["subdomain"] = username

    url = _build_url(f"/tournaments/{tournament_id}/participants.json", params)
    raw = _get(url)

    participants: dict[int, dict] = {}
    if isinstance(raw, list):
        for item in raw:
            p = item.get("participant", {})
            pid = p.get("id", 0)
            # Parse team tag from name
            full_name = p.get("name", "") or f"Player {pid}"
            team_tag, player_name = _parse_name_with_tag(full_name)
            p["parsed_name"] = player_name
            p["team_tag"] = team_tag
            # Merge roster overrides (local players.json)
            roster = _load_roster()
            entry = roster.get(player_name)
            if entry:
                if entry.get("team_tag"):
                    p["team_tag"] = entry["team_tag"]
                if entry.get("avatar_filename"):
                    p["avatar_url"] = _AVATAR_URL_PREFIX + entry["avatar_filename"]
                else:
                    p["avatar_url"] = _avatar(p)
            else:
                p["avatar_url"] = _avatar(p)
            participants[pid] = p
    return participants


def _avatar(p: dict) -> str:
    """Gravatar URL from Challonge email_hash, or empty string."""
    email_hash = p.get("email_hash", "")
    if email_hash:
        return f"https://www.gravatar.com/avatar/{email_hash}?s=64&d=mp"
    return ""


def get_participants(api_key: str, tournament_id: int, username: str = "") -> list[dict]:
    """Return tournament participants merged with local roster data.

    Each entry: {id, name (parsed), team_tag, avatar_url}.
    """
    return list(_fetch_participants(api_key, tournament_id, username).values())


# ── Roster (local players.json) ──────────────────────────────────────────────

import os

# players.json + avatars both live inside the avatars dir so a single Docker
# volume mounted on /app/app/static/avatars keeps everything persistent and
# serves avatars from the requested /static/avatars/ URL.
_ROSTER_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
_AVATARS_DIR = os.path.join(_ROSTER_DIR, "avatars")
_ROSTER_FILE = os.path.join(_AVATARS_DIR, "players.json")
_AVATAR_URL_PREFIX = "/static/avatars/"


def _slugify(name: str) -> str:
    """Make a filesystem-safe name from a player pseudo."""
    s = name.strip().lower()
    s = "".join(c if (c.isalnum() or c in "-_") else "-" for c in s)
    s = "-".join(part for part in s.split("-") if part)
    return s or "player"


def _load_roster() -> dict:
    """Load players.json (keyed by pseudo) or return empty dict."""
    try:
        with open(_ROSTER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return {}


def _save_roster(roster: dict) -> None:
    """Persist players.json atomically."""
    os.makedirs(_AVATARS_DIR, exist_ok=True)
    tmp = _ROSTER_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(roster, f, ensure_ascii=False, indent=2)
    os.replace(tmp, _ROSTER_FILE)


def get_roster() -> dict:
    """Return the full roster dict (pseudo -> {team_tag, avatar_filename})."""
    return _load_roster()


def get_avatar_url(pseudo: str) -> str:
    """Return the local avatar URL for a pseudo, or empty string if none."""
    roster = _load_roster()
    entry = roster.get(pseudo)
    if entry and entry.get("avatar_filename"):
        return _AVATAR_URL_PREFIX + entry["avatar_filename"]
    return ""


def set_player_tag(pseudo: str, team_tag: str) -> dict:
    """Update (or create) a player's team tag in players.json."""
    roster = _load_roster()
    entry = roster.get(pseudo, {})
    entry["team_tag"] = team_tag or ""
    roster[pseudo] = entry
    _save_roster(roster)
    return entry


def set_player_avatar(pseudo: str, filename: str) -> dict:
    """Update a player's avatar filename in players.json."""
    roster = _load_roster()
    entry = roster.get(pseudo, {})
    entry["avatar_filename"] = filename
    roster[pseudo] = entry
    _save_roster(roster)
    return entry


def fetch_matches(api_key: str, tournament_id: int, username: str = "") -> list[MatchInfo]:
    """Fetch all matches for a tournament, including participant names and avatars."""
    global _api_key
    _api_key = api_key

    # Fetch participants first for name/avatar lookup
    participants = _fetch_participants(api_key, tournament_id, username)

    params: dict[str, str] = {}
    if username:
        params["subdomain"] = username

    url = _build_url(f"/tournaments/{tournament_id}/matches.json", params)
    raw = _get(url)

    matches: list[MatchInfo] = []
    if isinstance(raw, list):
        for item in raw:
            m = item.get("match", {})
            p1_id = m.get("player1_id") or 0
            p2_id = m.get("player2_id") or 0

            p1_data = participants.get(p1_id, {})
            p2_data = participants.get(p2_id, {})

            # State mapping
            state_map = {
                "open": "open",
                "pending": "pending",
                "in_progress": "in_progress",
                "complete": "completed",
                "completed": "completed",
            }
            match_state = state_map.get(m.get("state", ""), "open")

            # Score parsing
            scores_csv = m.get("scores_csv", "") or ""
            p1_score, p2_score = 0, 0
            if scores_csv:
                for part in scores_csv.split(","):
                    if "-" in part:
                        try:
                            a, b = part.strip().split("-")
                            p1_score += int(a.strip())
                            p2_score += int(b.strip())
                        except (ValueError, IndexError):
                            pass

            player1 = PlayerInfo(
                id=p1_id,
                name=p1_data.get("parsed_name", "") or f"Player {p1_id}",
                team_tag=p1_data.get("team_tag", ""),
                score=p1_score,
                is_winner=m.get("winner_id") == p1_id,
                avatar_url=p1_data.get("avatar_url", "") or _avatar(p1_data),
            ) if p1_id else None

            player2 = PlayerInfo(
                id=p2_id,
                name=p2_data.get("parsed_name", "") or f"Player {p2_id}",
                team_tag=p2_data.get("team_tag", ""),
                score=p2_score,
                is_winner=m.get("winner_id") == p2_id,
                avatar_url=p2_data.get("avatar_url", "") or _avatar(p2_data),
            ) if p2_id else None

            matches.append(
                MatchInfo(
                    id=m.get("id", 0),
                    tournament_id=tournament_id,
                    round=m.get("round", 1),
                    identifier=m.get("identifier", ""),
                    state=match_state,
                    player1=player1,
                    player2=player2,
                    winner_id=m.get("winner_id"),
                )
            )

    # Apply manual team tag overrides (persisted user-entered tags)
    for match in matches:
        _apply_team_tag_override(match)

    return matches


# ── Team Tag Overrides ────────────────────────────────────────────────────────

# Manual team tag overrides keyed by match id. Lets users set a tag in the
# dashboard modal that persists across Challonge polls (overrides parsed tag).
_team_tag_overrides: dict[int, dict] = {}


def set_team_tag_override(
    tournament_id: int,
    match_id: int,
    p1_tag: str | None = None,
    p2_tag: str | None = None,
) -> None:
    """Persist manual team tag overrides for a match.

    A non-None value (including empty string) overrides the Challonge-parsed tag.
    None means "keep the Challonge tag" (no override stored).
    """
    if p1_tag is None and p2_tag is None:
        return
    existing = _team_tag_overrides.get(match_id, {})
    if p1_tag is not None:
        existing["p1"] = p1_tag
    if p2_tag is not None:
        existing["p2"] = p2_tag
    _team_tag_overrides[match_id] = existing


def _apply_team_tag_override(match: "MatchInfo") -> None:
    """Apply stored team tag overrides onto a match (in place)."""
    override = _team_tag_overrides.get(match.id)
    if not override:
        return
    if "p1" in override and match.player1:
        match.player1.team_tag = override["p1"]
    if "p2" in override and match.player2:
        match.player2.team_tag = override["p2"]


def update_match_score(
    tournament_id: int,
    match_id: int,
    scores_csv: str,
    winner_id: int = 0,
) -> dict[str, Any]:
    """Update a match score on Challonge."""
    data: dict[str, str] = {"match[scores_csv]": scores_csv}
    if winner_id:
        data["match[winner_id]"] = str(winner_id)

    url = _build_url(f"/tournaments/{tournament_id}/matches/{match_id}.json")
    return _put(url, data)


# ── Polling ──────────────────────────────────────────────────────────────────

# Store last known match states for change detection
_match_cache: dict[int, int] = {}

async def poll_tournament(tournament_id: int, interval: int = 15) -> None:
    """Asyncio task that polls a tournament for match updates and broadcasts via WebSocket."""
    import asyncio as _asyncio

    global _match_cache

    while True:
        try:
            loop = _asyncio.get_event_loop()
            matches = await loop.run_in_executor(
                None, fetch_matches, _api_key, tournament_id, ""
            )
            for match in matches:
                # Create a hash of the match state for change detection
                match_hash = hash((
                    match.id,
                    match.state,
                    match.round,
                    match.player1.id if match.player1 else None,
                    match.player1.name if match.player1 else None,
                    match.player1.score if match.player1 else None,
                    match.player1.is_winner if match.player1 else None,
                    match.player2.id if match.player2 else None,
                    match.player2.name if match.player2 else None,
                    match.player2.score if match.player2 else None,
                    match.player2.is_winner if match.player2 else None,
                    match.winner_id,
                ))
                
                # Only broadcast if the match state has changed
                cache_key = match.id
                if _match_cache.get(cache_key) != match_hash:
                    _match_cache[cache_key] = match_hash
                    await manager.broadcast_match_update(match)
                    if match.state == "completed":
                        await manager.broadcast_notification(match)
        except Exception:
            pass
        await _asyncio.sleep(interval)


def start_polling(tournament_id: int, interval: int = 15) -> None:
    """Start a polling task for a tournament."""
    if tournament_id in _polling_tasks:
        _polling_tasks[tournament_id].cancel()
    _polling_tasks[tournament_id] = asyncio.create_task(
        poll_tournament(tournament_id, interval)
    )


def stop_polling() -> None:
    """Cancel all active polling tasks."""
    for task in _polling_tasks.values():
        task.cancel()
    _polling_tasks.clear()


# ── Match Operations ──────────────────────────────────────────────────────────

def swap_players(
    tournament_id: int,
    match_id: int,
) -> dict[str, Any]:
    """Swap player 1 and player 2 on Challonge by swapping their IDs."""
    # First, get current match data to know the player IDs
    matches = fetch_matches(_api_key, tournament_id)
    current_match = None
    for m in matches:
        if m.id == match_id:
            current_match = m
            break
    
    if not current_match or not current_match.player1 or not current_match.player2:
        raise ValueError("Match not found or missing players")
    
    # Swap player1_id and player2_id on Challonge
    data: dict[str, str] = {
        "match[player1_id]": str(current_match.player2.id),
        "match[player2_id]": str(current_match.player1.id),
    }
    
    url = _build_url(f"/tournaments/{tournament_id}/matches/{match_id}.json")
    return _put(url, data)


def reset_bracket(
    tournament_id: int,
    match_id: int,
) -> dict[str, Any]:
    """Reset match scores to 0-0 for bracket reset (Grand Finals)."""
    data: dict[str, str] = {
        "match[scores_csv]": "0-0",
    }
    
    url = _build_url(f"/tournaments/{tournament_id}/matches/{match_id}.json")
    return _put(url, data)
