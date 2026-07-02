# Changelog

All notable changes to Tourney-Overlay will be documented in this format.

## [1.1.0] - 2025-07-01

### Added
- **Official game icons**: 24 games now have Steam header images (SF6, Tekken 8, GG Strive, etc.)
- **Challonge logo** for Custom game option
- **Game icon display** next to game selector in dashboard (updates on game change)
- **Winner badge** replaces animated crown on score overlay
- **Winner text i18n**: "VAINQUEUR" (FR) / "WINNER" (EN) based on `lang` parameter
- Winner badge styling: gold border, pulse animation, tertiary color theming

### Changed
- Score overlay: crown emoji → styled winner badge with text
- Dashboard: game selector now shows official game icon
- Dashboard: removed all emojis (titles, buttons, dropdowns, categories)
- Card titles: lighter color `rgba(255,255,255,0.6)`
- Overview overlay: status texts without emojis, winner displayed in status
- Card status: Orbitron font, 700 weight, 11px, 0.8 opacity
- Completed matches: gold status, Live matches: primary color

## [1.0.0] - 2025-06-30

### Added
- Initial release of **Tourney-Overlay** (complete rewrite from legacy sf-overlay)
- FastAPI backend with async support
- Native Starlette WebSockets for real-time updates
- 24 game themes with custom colors & animations
- Single-file dashboard WebUI (~800 lines)
- Three OBS overlays: Score, Notification, Bracket
- Challonge API integration (urllib for SSL compatibility)
- Player avatars via Gravatar
- Score parsing from `scores_csv` (multi-set support)
- Match state mapping: `completed`/`in_progress`/`pending`/`open`
- CORS middleware for local network access
- Proper error handling for Challonge API (400 with details)
- Docker multi-stage build (Python 3.13 + uv)
- docker-compose.yml for easy deployment
- Portainer deploy script
- GitHub Actions CI workflow (`docker-build.yml`)
- GitHub Actions Release workflow (`docker-publish.yml`) — auto-release on tag push
- **PolyForm Noncommercial License 1.0.0**

### Fixed
- Frontend JS handling of `{tournaments: [...]}` API wrapper
- Frontend JS handling of `{matches: [...]}` API wrapper
- Subdomain handling (only passed if provided, avoids 422)
- CORS errors blocking browser API calls
- 500 errors on invalid Challonge subdomain
- MatchState enum uses `completed` (not `complete`)

---

## [0.9.0] - 2024 (Legacy sf-overlay)

### Added
- Initial tournament overlay system
- Challonge integration
- Basic OBS overlays
- Docker deployment

---

**Note**: v1.0.0 is a complete rewrite and not backward compatible with the legacy sf-overlay.