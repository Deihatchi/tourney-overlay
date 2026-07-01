"""Native Starlette WebSocket routes for SF Overlay2."""

from __future__ import annotations

from fastapi import APIRouter, WebSocketDisconnect
from starlette.websockets import WebSocket

from app.services.websocket_manager import manager

router = APIRouter()


@router.websocket("/ws/overlay/{match_id}")
async def websocket_overlay(websocket: WebSocket, match_id: int) -> None:
    """WebSocket endpoint for overlay clients subscribed to a specific match."""
    await manager.connect_overlay(websocket, match_id)
    try:
        while True:
            # Keep connection alive; handle ping/pong and client messages
            data = await websocket.receive_text()
            # Echo or ignore — primarily used for keepalive
    except WebSocketDisconnect:
        await manager.disconnect_overlay(websocket, match_id)
    except Exception:
        await manager.disconnect_overlay(websocket, match_id)


@router.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket) -> None:
    """WebSocket endpoint for dashboard clients."""
    await manager.connect_dashboard(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Keepalive / handle dashboard commands
    except WebSocketDisconnect:
        await manager.disconnect_dashboard(websocket)
    except Exception:
        await manager.disconnect_dashboard(websocket)
