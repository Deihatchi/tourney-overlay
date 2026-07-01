"""WebSocket connection manager for SF Overlay2."""

from __future__ import annotations

import json

from starlette.websockets import WebSocket

from app.models import MatchInfo, WSMessage


class ConnectionManager:
    """Manages WebSocket connections organized by overlay rooms and dashboard."""

    def __init__(self) -> None:
        # match_id -> list of connected overlay WebSockets
        self._overlay_rooms: dict[int, list[WebSocket]] = {}
        # list of connected dashboard WebSockets
        self._dashboard_sockets: list[WebSocket] = []

    # ── Overlay connections ─────────────────────────────────────────────────

    async def connect_overlay(self, websocket: WebSocket, match_id: int) -> None:
        """Accept and register an overlay WebSocket for a specific match."""
        await websocket.accept()
        if match_id not in self._overlay_rooms:
            self._overlay_rooms[match_id] = []
        self._overlay_rooms[match_id].append(websocket)

    async def disconnect_overlay(self, websocket: WebSocket, match_id: int) -> None:
        """Remove an overlay WebSocket from its room."""
        room = self._overlay_rooms.get(match_id, [])
        if websocket in room:
            room.remove(websocket)
        if not room:
            self._overlay_rooms.pop(match_id, None)

    # ── Dashboard connections ───────────────────────────────────────────────

    async def connect_dashboard(self, websocket: WebSocket) -> None:
        """Accept and register a dashboard WebSocket."""
        await websocket.accept()
        self._dashboard_sockets.append(websocket)

    async def disconnect_dashboard(self, websocket: WebSocket) -> None:
        """Remove a dashboard WebSocket."""
        if websocket in self._dashboard_sockets:
            self._dashboard_sockets.remove(websocket)

    # ── Broadcasting ───────────────────────────────────────────────────────

    async def broadcast_match_update(self, match: MatchInfo) -> None:
        """Send a match update to the relevant overlay room and all dashboards."""
        message = WSMessage(
            type="match_update",
            match=match,
            tournament_id=match.tournament_id,
        )
        payload = json.dumps(message.model_dump(), default=str)

        # Send to overlay room for this match
        room = self._overlay_rooms.get(match.id, [])
        for ws in list(room):
            try:
                await ws.send_text(payload)
            except Exception:
                pass

        # Send to all dashboards
        for ws in list(self._dashboard_sockets):
            try:
                await ws.send_text(payload)
            except Exception:
                pass

    async def broadcast_notification(self, match: MatchInfo) -> None:
        """Send a match-completed notification to overlay rooms and dashboards."""
        message = WSMessage(
            type="notification",
            match=match,
            message=f"Match terminé : {match.player1.name if match.player1 else '?'} vs {match.player2.name if match.player2 else '?'}",
            tournament_id=match.tournament_id,
        )
        payload = json.dumps(message.model_dump(), default=str)

        room = self._overlay_rooms.get(match.id, [])
        for ws in list(room):
            try:
                await ws.send_text(payload)
            except Exception:
                pass

        for ws in list(self._dashboard_sockets):
            try:
                await ws.send_text(payload)
            except Exception:
                pass


# Singleton instance
manager = ConnectionManager()
