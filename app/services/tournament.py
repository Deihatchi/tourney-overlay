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
            tournaments.append(
                TournamentInfo(
                    id=t.get("id", 0),
                    name=t.get("name", ""),
                    url=t.get("full_challonge_url", ""),
                    game_name=t.get("game_name") or "",
                    state=t.get("state", ""),
                    tournament_type=t.get("tournament_type", "single elimination"),
                    participants_count=t.get("participants_count", 0),
                    progress=float(t.get("progress", 0) or 0),
                )
            )
    return tournaments


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
            participants[pid] = p
    return participants


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

            # Avatar via Gravatar (email_hash from Challonge API)
            def _avatar(p: dict) -> str:
                email_hash = p.get("email_hash", "")
                if email_hash:
                    return f"https://www.gravatar.com/avatar/{email_hash}?s=64&d=mp"
                return ""

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
                name=p1_data.get("name", "") or f"Player {p1_id}",
                score=p1_score,
                is_winner=m.get("winner_id") == p1_id,
                avatar_url=_avatar(p1_data),
            ) if p1_id else None

            player2 = PlayerInfo(
                id=p2_id,
                name=p2_data.get("name", "") or f"Player {p2_id}",
                score=p2_score,
                is_winner=m.get("winner_id") == p2_id,
                avatar_url=_avatar(p2_data),
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
    return matches


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

async def poll_tournament(tournament_id: int, interval: int = 15) -> None:
    """Asyncio task that polls a tournament for match updates and broadcasts via WebSocket."""
    import asyncio as _asyncio

    while True:
        try:
            loop = _asyncio.get_event_loop()
            matches = await loop.run_in_executor(
                None, fetch_matches, _api_key, tournament_id, ""
            )
            for match in matches:
                await manager.broadcast_match_update(match)
                if match.state == "completed" or match.state.value == "completed":
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
