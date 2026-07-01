# Changelog

All notable changes to SF-Overlay2 will be documented in this format.

## [2.0.0] - 2025-06-30

### Added
- Complete rewrite from v1 (sf-overlay)
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
- GitHub Actions workflow for GHCR image builds
- MIT License

### Fixed
- Frontend JS handling of `{tournaments: [...]}` API wrapper
- Frontend JS handling of `{matches: [...]}` API wrapper
- Subdomain handling (only passed if provided, avoids 422)
- CORS errors blocking browser API calls
- 500 errors on invalid Challonge subdomain
- MatchState enum uses `completed` (not `complete`)

## [1.0.0] - 2024 (Legacy sf-overlay)

### Added
- Initial tournament overlay system
- Challonge integration
- Basic OBS overlays
- Docker deployment

---

**Note**: v2.0.0 is a complete rewrite and not backward compatible with v1.