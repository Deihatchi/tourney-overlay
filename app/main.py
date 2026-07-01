"""Uvicorn entry point for SF Overlay2."""

import uvicorn

from app import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
