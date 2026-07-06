"""Overlay HTML rendering routes for SF Overlay2.

All overlay configuration is passed via URL query parameters.
Game theme colors take priority; only game=custom allows free colors.
"""

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse

from app.models import GAME_THEMES
from app.template_env import templates_env

router = APIRouter()


def _resolve_theme(game: str, primary: str, secondary: str, tertiary: str, animation: str) -> dict:
    """Resolve theme: use game preset if game is known and not custom."""
    if game != "custom" and game in GAME_THEMES:
        theme = GAME_THEMES[game]
        return {
            "primary": theme["primary"],
            "secondary": theme["secondary"],
            "tertiary": theme["tertiary"],
            "animation": theme["anim"],
        }
    return {
        "primary": primary or "#ff4655",
        "secondary": secondary or "#00d4ff",
        "tertiary": tertiary or "#ffd700",
        "animation": animation or "slide",
    }


@router.get("/overlay/score", response_class=HTMLResponse)
async def overlay_score(
    request: Request,
    match_id: int = Query(default=0, description="Match ID"),
    tournament_id: int = Query(default=0, description="Tournament ID"),
    game: str = Query(default="sf6", description="Game: sf6, tekken8, custom..."),
    primary: str = Query(default="#ff4655", description="Primary color (hex)"),
    secondary: str = Query(default="#00d4ff", description="Secondary color (hex)"),
    tertiary: str = Query(default="#ffd700", description="Tertiary/winner color (hex)"),
    animation: str = Query(default="slide", description="Animation style"),
    font: str = Query(default="Rajdhani", description="Font family"),
    show_round: bool = Query(default=True),
    res: str = Query(default="1920x1080", description="Resolution"),
    lang: str = Query(default="fr", description="Language"),
):
    theme = _resolve_theme(game, primary, secondary, tertiary, animation)
    winner_text = "VAINQUEUR" if lang == "fr" else "WINNER"
    import importlib.metadata
    try:
        version = importlib.metadata.version("tourney-overlay")
    except importlib.metadata.PackageNotFoundError:
        version = "dev"

    # Fetch initial match data from API
    player1_name = ""
    player2_name = ""
    player1_score = ""
    player2_score = ""
    try:
        from app.services.tournament import fetch_matches, get_api_key
        key = get_api_key()
        if key:
            matches = fetch_matches(key, tournament_id)
            for m in matches:
                if m.id == match_id:
                    if m.player1:
                        player1_name = m.player1.name or ""
                        player1_score = str(m.player1.score) if m.player1.score is not None else ""
                    if m.player2:
                        player2_name = m.player2.name or ""
                        player2_score = str(m.player2.score) if m.player2.score is not None else ""
                    break
    except Exception:
        pass  # API not configured yet, will load via WS

    tmpl = templates_env.get_template("overlay_score.html")
    return tmpl.render(
        request=request,
        match_id=match_id,
        tournament_id=tournament_id,
        game=game,
        **theme,
        font_family=f"'Orbitron', monospace" if font == "Orbitron" else f"'{font}', sans-serif",
        show_round=show_round,
        resolution=res,
        lang=lang,
        winner_text=winner_text,
        version=version,
        player1_name=player1_name,
        player2_name=player2_name,
        player1_score=player1_score,
        player2_score=player2_score,
    )


@router.get("/overlay/notification", response_class=HTMLResponse)
async def overlay_notification(
    request: Request,
    game: str = Query(default="sf6"),
    primary: str = Query(default="#ff4655"),
    secondary: str = Query(default="#00d4ff"),
    tertiary: str = Query(default="#ffd700"),
    animation: str = Query(default="slide"),
    duration: int = Query(default=8),
    position: str = Query(default="bottom-right"),
    font: str = Query(default="Rajdhani"),
    lang: str = Query(default="fr"),
):
    theme = _resolve_theme(game, primary, secondary, tertiary, animation)
    # Get version from package metadata
    import importlib.metadata
    try:
        version = importlib.metadata.version("tourney-overlay")
    except importlib.metadata.PackageNotFoundError:
        version = "dev"
    tmpl = templates_env.get_template("overlay_notification.html")
    return tmpl.render(
        request=request,
        game=game,
        **theme,
        notification_duration=duration,
        notification_position=position,
        font_family=f"'{font}', sans-serif",
        lang=lang,
        version=version,
    )


@router.get("/overview", response_class=HTMLResponse)
async def overview_overlay(
    request: Request,
    tournament_id: int = Query(default=0),
    game: str = Query(default="sf6"),
    primary: str = Query(default="#ff4655"),
    secondary: str = Query(default="#00d4ff"),
    tertiary: str = Query(default="#ffd700"),
    animation: str = Query(default="slide"),
    font: str = Query(default="Rajdhani"),
    lang: str = Query(default="fr"),
):
    theme = _resolve_theme(game, primary, secondary, tertiary, animation)
    # Get version from package metadata
    import importlib.metadata
    try:
        version = importlib.metadata.version("tourney-overlay")
    except importlib.metadata.PackageNotFoundError:
        version = "dev"
    tmpl = templates_env.get_template("overview_overlay.html")
    return tmpl.render(
        request=request,
        game=game,
        tournament_id=tournament_id,
        **theme,
        font_family=f"'{font}', sans-serif",
        lang=lang,
        version=version,
    )


@router.get("/", response_class=HTMLResponse)
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    tmpl = templates_env.get_template("dashboard.html")
    # Get version from package metadata
    import importlib.metadata
    try:
        version = importlib.metadata.version("tourney-overlay")
    except importlib.metadata.PackageNotFoundError:
        version = "dev"
    return tmpl.render(request=request, version=version)
