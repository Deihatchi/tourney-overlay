# Contributing to Tourney-Overlay

Thank you for your interest in contributing!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/tourney-overlay.git`
3. Create a feature branch: `git checkout -b feature/my-feature`
4. Make your changes
5. Test with Docker: `docker compose up --build`
6. Submit a Pull Request

## Development Setup

```bash
# Install dependencies
cd tourney-overlay
uv sync --dev  # or pip install -e ".[dev]"

# Run locally (requires .env with API key)
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Code Style

- **Python**: Black + Ruff (configured in pyproject.toml)
- **HTML/JS**: Prettier (run via `npx prettier --write .`)
- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`, etc.)

## Adding a New Game Theme

1. Edit `app/models.py` → add to `GAME_THEMES` dict
2. Required fields: `id`, `name`, `emoji`, `cat`, `primary`, `secondary`, `tertiary`, `anim`
3. Test: `docker compose up --build` → check dashboard game selector

## Adding a New Overlay

1. Create template in `app/templates/` (e.g., `overlay_custom.html`)
2. Add route in `app/routes/overlays.py`
3. Add URL generation in `app/templates/dashboard.html` (function `updateUrls`)
4. Test in OBS

## Reporting Issues

Use GitHub Issues with:
- Clear title
- Steps to reproduce
- Expected vs actual behavior
- Docker logs (`docker logs tourney-overlay`)
- Screenshots if UI-related

## Security

- Never commit `.env` or API keys
- Report security issues privately via GitHub Security Advisories

## License

By contributing, you agree your contributions will be licensed under **PolyForm Noncommercial License 1.0.0**.