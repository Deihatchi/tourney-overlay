# Changelog

All notable changes to Tourney-Overlay will be documented in this format.

## [1.2.3] - 2025-07-05

### Fixed
- **All inline onclick handlers replaced** with event delegation — eliminates all JavaScript escaping issues (`SyntaxError: Unexpected string`)
- **Bracket overlay** — removed "EN DIRECTE", miniaturized "LIVE", added round filtering (shows only current round), full FR/EN translations
- **Preview/copy buttons** — restored functionality (were broken by `\\'` escaping)
- **Score editor** — player names with apostrophes no longer break the modal

## [1.2.2] - 2025-07-03

### Fixed
- **Dashboard JavaScript escaping** - Fixed `SyntaxError: Unexpected string` caused by malformed string escaping in `updateUrls()` function
- **Undefined functions** - Fixed `connectApi`, `syncColor`, `syncHex`, `loadGames`, `updateUrls`, `applyStyle` being undefined due to JS parse error
- **Color picker** - Color inputs now properly sync with hex fields
- **API connection** - "Connecter" button now works correctly

## [1.2.1] - 2025-07-03

### Added
- **Version badge** visible on dashboard header and all overlays (bracket, score, notification)
- **Change detection in polling** — only broadcasts WebSocket updates when match state actually changes (scores, winner, state)
- **Real-time dashboard match list updates** via WebSocket — no page reload when matches change

### Changed
- **Removed logo handling entirely** from dashboard and all overlay URLs (`&logo=` parameter removed)
- **Overlay bracket**: winner displayed with animated "VAINQUEUR"/"WINNER" badge
- **All overlays**: version badge in bottom-right corner
- **WebSocket broadcasting**: optimized to only send updates on actual changes

### Fixed
- **Dashboard game selector** now properly loads 24 games on startup
- **API key configuration** flow works correctly (connect → load tournaments → select → watch)

## [1.2.0] - 2025-07-02

### Added
- **Official Challonge SVG logo** in dashboard (replaces trophy emoji)
- **Official game icons** (Steam headers) displayed next to game selector
- **Winner badge** with i18n: "VAINQUEUR" (FR) / "WINNER" (EN) replaces animated crown
- **Instant score overlay loading** — shows match data immediately via WebSocket

### Changed
- **Dashboard**: removed all emojis from titles, buttons, dropdowns, categories
- **Card titles**: lighter color `rgba(255,255,255,0.6)` for better readability
- **Overview overlay**: status texts without emojis, winner displayed in match status
- **Card status**: Orbitron font, 700 weight, 11px, 0.8 opacity
- **Completed matches**: gold status color, Live matches: primary color
- **LIVE badge** in bracket overlay: translated (EN COURS / LIVE), smaller, centered

### Removed
- **Logo upload/management** from dashboard (handled directly in OBS)
- **Logo display** from score and bracket overlays (managed in OBS)
- `&logo=` parameter from generated overlay URLs

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