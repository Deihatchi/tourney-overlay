"""Game themes and Pydantic models for SF Overlay2."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel

# ── GAME_THEMES ──────────────────────────────────────────────────────────────

GAME_THEMES: dict[str, dict] = {
    # ── Fighting ──────────────────────────────────────────────────────────────
    "sf6": {
        "name": "Street Fighter 6",
        "primary": "#ff4655",
        "secondary": "#00d4ff",
        "tertiary": "#ffd700",
        "anim": "slide",
        "emoji": "🥊",
        "cat": "Fighting",
        "icon": "https://cdn.cloudflare.steamstatic.com/steam/apps/1364780/header.jpg",
    },
    "sf5": {
        "name": "Street Fighter V",
        "primary": "#ff4655",
        "secondary": "#1a1a2e",
        "tertiary": "#e94560",
        "anim": "slide",
        "emoji": "🥊",
        "cat": "Fighting",
        "icon": "https://cdn.cloudflare.steamstatic.com/steam/apps/310950/header.jpg",
    },
    "sf4": {
        "name": "Street Fighter IV",
        "primary": "#ff6b35",
        "secondary": "#ffd700",
        "tertiary": "#ffffff",
        "anim": "slide",
        "emoji": "🥊",
        "cat": "Fighting",
        "icon": "https://cdn.cloudflare.steamstatic.com/steam/apps/4000/header.jpg",
    },
    "sf3": {
        "name": "Street Fighter III",
        "primary": "#9b59b6",
        "secondary": "#3498db",
        "tertiary": "#ecf0f1",
        "anim": "slide",
        "emoji": "🥊",
        "cat": "Fighting",
        "icon": "https://www.fightersgeneration.com/nf6/char2/sf33s-logo.gif",
    },
    "sf2": {
        "name": "Street Fighter II",
        "primary": "#e74c3c",
        "secondary": "#f39c12",
        "tertiary": "#2ecc71",
        "anim": "slide",
        "emoji": "🥊",
        "cat": "Fighting",
        "icon": "https://www.fightersgeneration.com/nf6/char2/sf2-logo.gif",
    },
    "tekken8": {
        "name": "Tekken 8",
        "primary": "#ff1744",
        "secondary": "#000000",
        "tertiary": "#ffab00",
        "anim": "punch",
        "emoji": "👊",
        "cat": "Fighting",
        "icon": "https://cdn.cloudflare.steamstatic.com/steam/apps/2338770/header.jpg",
    },
    "tekken7": {
        "name": "Tekken 7",
        "primary": "#d50000",
        "secondary": "#212121",
        "tertiary": "#ffc107",
        "anim": "punch",
        "emoji": "👊",
        "cat": "Fighting",
        "icon": "https://cdn.cloudflare.steamstatic.com/steam/apps/389730/header.jpg",
    },
    "ggst": {
        "name": "Guilty Gear Strive",
        "primary": "#ff6f00",
        "secondary": "#1de9b6",
        "tertiary": "#ffffff",
        "anim": "swing",
        "emoji": "⚔️",
        "cat": "Fighting",
        "icon": "https://cdn.cloudflare.steamstatic.com/steam/apps/1384160/header.jpg",
    },
    "bbcf": {
        "name": "BlazBlue Centralfiction",
        "primary": "#6200ea",
        "secondary": "#00bcd4",
        "tertiary": "#ffffff",
        "anim": "swing",
        "emoji": "⚔️",
        "cat": "Fighting",
        "icon": "https://cdn.cloudflare.steamstatic.com/steam/apps/586140/header.jpg",
    },
    "dbfz": {
        "name": "Dragon Ball FighterZ",
        "primary": "#ff9100",
        "secondary": "#2979ff",
        "tertiary": "#ffd600",
        "anim": "blast",
        "emoji": "💥",
        "cat": "Fighting",
        "icon": "https://cdn.cloudflare.steamstatic.com/steam/apps/678950/header.jpg",
    },
    "mk1": {
        "name": "Mortal Kombat 1",
        "primary": "#ffd600",
        "secondary": "#000000",
        "tertiary": "#ff1744",
        "anim": "fatality",
        "emoji": "💀",
        "cat": "Fighting",
        "icon": "https://cdn.cloudflare.steamstatic.com/steam/apps/2375420/header.jpg",
    },
    "unist": {
        "name": "Under Night In-Birth",
        "primary": "#651fff",
        "secondary": "#00e5ff",
        "tertiary": "#ffffff",
        "anim": "slide",
        "emoji": "🌙",
        "cat": "Fighting",
        "icon": "https://cdn.cloudflare.steamstatic.com/steam/apps/1257900/header.jpg",
    },
    "smashu": {
        "name": "Super Smash Bros Ultimate",
        "primary": "#ff1744",
        "secondary": "#2979ff",
        "tertiary": "#ffea00",
        "anim": "bounce",
        "emoji": "🎮",
        "cat": "Fighting",
        "icon": "https://cdn.cloudflare.steamstatic.com/steam/apps/1384160/header.jpg",
    },
    "smashm": {
        "name": "Super Smash Bros Melee",
        "primary": "#ffea00",
        "secondary": "#000000",
        "tertiary": "#ffffff",
        "anim": "bounce",
        "emoji": "🎮",
        "cat": "Fighting",
        "icon": "https://www.ssbwiki.com/images/thumb/3/3d/SSBM_logo.png/800px-SSBM_logo.png",
    },
    "kof15": {
        "name": "King of Fighters XV",
        "primary": "#d500f9",
        "secondary": "#00e676",
        "tertiary": "#ffffff",
        "anim": "slide",
        "emoji": "🔥",
        "cat": "Fighting",
        "icon": "https://cdn.cloudflare.steamstatic.com/steam/apps/1520060/header.jpg",
    },
    "gbfvr": {
        "name": "Granblue Fantasy Versus Rising",
        "primary": "#00b0ff",
        "secondary": "#ff1744",
        "tertiary": "#ffd600",
        "anim": "swing",
        "emoji": "⚔️",
        "cat": "Fighting",
        "icon": "https://cdn.cloudflare.steamstatic.com/steam/apps/2358570/header.jpg",
    },
    # ── FPS ──────────────────────────────────────────────────────────────────
    "valo": {
        "name": "Valorant",
        "primary": "#ff4655",
        "secondary": "#0f1923",
        "tertiary": "#00ffa3",
        "anim": "fade",
        "emoji": "🎯",
        "cat": "FPS",
        "icon": "https://cdn.cloudflare.steamstatic.com/steam/apps/1526830/header.jpg",
    },
    "cs2": {
        "name": "Counter-Strike 2",
        "primary": "#f5a623",
        "secondary": "#2c3e50",
        "tertiary": "#ecf0f1",
        "anim": "fade",
        "emoji": "🔫",
        "cat": "FPS",
        "icon": "https://cdn.cloudflare.steamstatic.com/steam/apps/730/header.jpg",
    },
    "ow2": {
        "name": "Overwatch 2",
        "primary": "#f99e1a",
        "secondary": "#212529",
        "tertiary": "#00d4ff",
        "anim": "fade",
        "emoji": "🦸",
        "cat": "FPS",
        "icon": "https://cdn.cloudflare.steamstatic.com/steam/apps/2357570/header.jpg",
    },
    # ── MOBA ─────────────────────────────────────────────────────────────────
    "lol": {
        "name": "League of Legends",
        "primary": "#c89b3c",
        "secondary": "#0a1428",
        "tertiary": "#00d4ff",
        "anim": "glow",
        "emoji": "⚔️",
        "cat": "MOBA",
        "icon": "https://cdn.cloudflare.steamstatic.com/steam/apps/427520/header.jpg",
    },
    "dota2": {
        "name": "Dota 2",
        "primary": "#e74c3c",
        "secondary": "#1a1a1a",
        "tertiary": "#f39c12",
        "anim": "glow",
        "emoji": "🛡️",
        "cat": "MOBA",
        "icon": "https://cdn.cloudflare.steamstatic.com/steam/apps/570/header.jpg",
    },
    # ── Sports ───────────────────────────────────────────────────────────────
    "rl": {
        "name": "Rocket League",
        "primary": "#00d4ff",
        "secondary": "#ff6b00",
        "tertiary": "#ffffff",
        "anim": "spin",
        "emoji": "🚗",
        "cat": "Sports",
        "icon": "https://cdn.cloudflare.steamstatic.com/steam/apps/252950/header.jpg",
    },
    "fifa": {
        "name": "EA Sports FC",
        "primary": "#00ff87",
        "secondary": "#1a1a2e",
        "tertiary": "#ffffff",
        "anim": "spin",
        "emoji": "⚽",
        "cat": "Sports",
        "icon": "https://cdn.cloudflare.steamstatic.com/steam/apps/1811260/header.jpg",
    },
    # ── Custom ───────────────────────────────────────────────────────────────
    "custom": {
        "name": "Custom",
        "primary": "#ff4655",
        "secondary": "#00d4ff",
        "tertiary": "#ffd700",
        "anim": "slide",
        "emoji": "🎨",
        "cat": "Custom",
        "icon": "https://challonge.com/assets/logo-500x500.png",
    },
}


# ── Enums ────────────────────────────────────────────────────────────────────

class MatchState(str, Enum):
    open = "open"
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


# ── Pydantic Models ──────────────────────────────────────────────────────────

class PlayerInfo(BaseModel):
    id: int = 0
    name: str = ""
    team_tag: str = ""
    score: int = 0
    is_winner: bool = False
    character: str = ""
    avatar_url: str = ""


class MatchInfo(BaseModel):
    id: int = 0
    tournament_id: int = 0
    tournament_name: str = ""
    round: int = 1
    identifier: str = ""
    state: str = MatchState.open
    player1: PlayerInfo | None = None
    player2: PlayerInfo | None = None
    winner_id: int | None = None
    bracket_reset: bool = False


class TournamentInfo(BaseModel):
    id: int = 0
    name: str = ""
    url: str = ""
    game_name: str | None = ""
    state: str = ""
    tournament_type: str = "single elimination"
    participants_count: int = 0
    progress: float = 0.0


class ChallongeConfig(BaseModel):
    api_key: str = ""
    username: str = ""


class AppConfig(BaseModel):
    service: str = "challonge"
    game: str = "sf6"
    api_key: str = ""
    username: str = ""
    tournament_id: int = 0
    match_id: int = 0
    primary_color: str = ""
    secondary_color: str = ""
    tertiary_color: str = ""
    animation_style: str = ""
    notification_duration: int = 8
    notification_position: str = "bottom-right"
    # Casters
    caster1_name: str = ""
    caster1_social: str = ""
    caster2_name: str = ""
    caster2_social: str = ""


class OverlayConfig(BaseModel):
    match_id: int = 0
    tournament_id: int = 0
    primary_color: str = "#ff4655"
    secondary_color: str = "#00d4ff"
    tertiary_color: str = "#ffd700"
    animation_style: str = "slide"
    font_family: str = "'Rajdhani', sans-serif"


class WSMessage(BaseModel):
    type: str = ""
    match: MatchInfo | None = None
    message: str = ""
    tournament_id: int = 0


class ScoreUpdate(BaseModel):
    match_id: int = 0
    tournament_id: int = 0
    player1_score: int = 0
    player2_score: int = 0
    winner_id: int = 0
    bracket_reset: bool = False


class SwapPlayers(BaseModel):
    match_id: int = 0
    tournament_id: int = 0
